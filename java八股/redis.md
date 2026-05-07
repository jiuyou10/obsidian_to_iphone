# Redis 常见数据结构和使用场景

## 五种基本数据类型

### 1. String（字符串）

**内部编码**：`int` / `embstr` / `raw`

| 特性   | 说明                         |
| ---- | -------------------------- |
| 最大容量 | 512 MB                     |
| 底层实现 | SDS（Simple Dynamic String） |

**常见命令**：`SET` `GET` `MSET` `MGET` `INCR` `DECR` `SETNX` `GETSET`

**使用场景**：

| 场景 | 示例 |
|------|------|
| **缓存** | 缓存用户信息、页面片段等 JSON 序列化数据 |
| **计数器** | 网站 PV/UV、点赞数、限流用计数器 `INCR article:readcount:1001` |
| **分布式锁** | `SETNX lock:resource 1` + `EXPIRE` |
| **共享 Session** | 分布式系统中统一存储用户会话 |
| **ID 生成器** | `INCR id:generator` 生成全局唯一 ID |

#### 内部实现：SDS（Simple Dynamic String）

**SDS 结构**（Redis 6.x / 7.x）：

```c
struct sdshdr {
    int   len;       // 已用字节数（不包含 '\0'）
    int   free;      // 未用字节数（可分配的剩余空间）
    char  buf[];     // 字节数组，以 '\0' 结尾（兼容 C 字符串函数）
};
```

**SDS 相比 C 字符串的优势**：

| | C 字符串 | SDS |
|--|---------|-----|
| 获取长度 | O(n)，需遍历 | **O(1)**，直接读 `len` 字段 |
| 二进制安全 | ❌ 遇 `\0` 截断 | ✅ 以 `len` 为准，可存图片/序列化数据 |
| 缓冲区溢出 | ✅ 可能（`strcat` 不检查目标空间） | ❌ 自动扩容（API 检查 `free`，不足则分配新空间） |
| 修改次数 N 的内存重分配 | N 次（每次修改都可能 realloc） | **最多 N 次**（预分配策略减少 realloc） |

**内存预分配策略**（减少频繁扩容）：
- SDS 长度 < 1MB：分配 `len` 的 **2 倍**（即 `free = len`）
- SDS 长度 ≥ 1MB：每次多分配 **1MB**（即 `free = 1MB`）

**三种编码的转换**：

```
SET key 123          → int（整数值，用 long 存）
SET key "abc"        → embstr（短字符串，≤44 字节，一次分配）
SET key "很长..."    → raw（长字符串，>44 字节，两次分配）
```

- `embstr`：SDS 头和字符串数据在同一块连续内存，**一次内存分配**，缓存友好
- `raw`：SDS 头和字符串数据**分开分配**，两次内存分配
- **`int → raw`**：执行 `APPEND` 等操作后，int 编码会转为 raw

---

### 2. Hash（哈希）

**内部编码**：`listpack`（7.0+）/ `ziplist`（旧版） / `hashtable`

| 特性 | 说明 |
|------|------|
| 结构 | field-value 映射，类似 Java 的 `Map<String, String>` |
| 容量 | 最多 2³² - 1 个 field |

**常见命令**：`HSET` `HGET` `HMSET` `HMGET` `HGETALL` `HDEL` `HINCRBY` `HLEN`

**使用场景**：

| 场景 | 示例 |
|------|------|
| **对象存储** | `HMSET user:1001 name "张三" age 25 city "北京"` |
| **购物车** | `userId` 为 key，`productId` 为 field，`数量` 为 value |
| **计数器分组** | `HINCRBY article:1001:stats views 1` |

> **Hash 和 String 存对象的区别**：String 存整个 JSON（修改一个字段要全量覆盖），Hash 支持单独修改某个 field，**更灵活但占用更多内存**。

#### 内部实现：listpack / ziplist vs hashtable

**编码转换条件**（以 7.0+ listpack 为例）：

```
listpack → hashtable 升级条件（任一满足即转换）：
  - field 数量 > hash-max-listpack-entries（默认 512）
  - 某个 field 或 value 长度 > hash-max-listpack-value（默认 64 字节）
```

**listpack（紧凑编码）结构**：

```
[entry1][entry2]...[entryN]
 每个 entry:
 [编码类型(1B)][字段内容][编码类型(1B)][值内容]
```

- 所有 field-value **连续存储**在一段连续内存中
- **优点**：内存占用极低，适合小 Hash（小字段、小值）
- **缺点**：查询为 O(n) 扫描，每次修改可能触发内存复制

**hashtable（字典）结构**：

```
dict
 ├── type        （类型特定函数）
 ├── ht[0]       （主哈希表）
 └── ht[1]       （rehash 备用表）

ht[x] 结构：
 ├── table[]     （哈希数组，每个槽位是链表头）
 ├── size        （数组大小，总是 2^n）
 └── used        （已用槽位数）
```

- **哈希冲突解决**：链地址法（链表）
- **渐进式 rehash**：不一次性搬完，而是分散到后续每次增删改查操作中
- **dict 为什么存两张表**：`ht[0]` 服务正常读写，`ht[1]` 在 rehash 时分配新空间；rehash 期间同时在两张表查

---

### 3. List（列表）

**内部编码**：`quicklist`（3.2+）

| 特性 | 说明 |
|------|------|
| 结构 | 双向链表，支持两端插入/弹出 |
| 阻塞操作 | `BLPOP` `BRPOP` 支持超时阻塞等待 |

**常见命令**：`LPUSH` `RPUSH` `LPOP` `RPOP` `LRANGE` `LINDEX` `LLEN` `BLPOP` `BRPOP`

**使用场景**：

| 场景 | 示例 |
|------|------|
| **消息队列** | `LPUSH` 生产，`BRPOP` 消费（实现简单队列） |
| **最新消息/时间线** | `LPUSH` 插入最新，`LRANGE 0 9` 获取前 10 条 |
| **栈** | `LPUSH` + `LPOP`（后进先出） |
| **列表分页** | `LRANGE key 0 9` 等 |

> **注意**：List 作为消息队列是**生产环境不推荐**的（没有 ACK 机制、消息可能丢失）。推荐用 **Stream** 或专业的 MQ。

#### 内部实现：quicklist

**quicklist 结构**：

```
quicklist
 ├── head → quicklistNode → quicklistNode → ... → tail
 └── count（总元素数）

quicklistNode:
 ├── prev / next（指向上/下一个节点）
 ├── entry[]      （listpack 紧凑数组，存实际数据）
 └── sz           （listpack 的字节大小）
```

**发展历史**：

| 版本       | 编码                                        | 问题                                              |
| -------- | ----------------------------------------- | ----------------------------------------------- |
| < 3.2    | `ziplist`（紧凑）或 `linkedlist`（双向链表）         | linkedlist 每个节点 24 字节指针开销大；ziplist 存在**连锁更新**问题 |
| **3.2+** | **quicklist** = ziplist 节点 + 双向链表         | 折中方案，但 ziplist 连锁更新问题未根除                        |
| **7.0+** | **quicklist** 内部 ziplist 替换为 **listpack** | **彻底解决连锁更新问题** ✅                                |

#### 补充：ziplist 连锁更新 & listpack 的改进

**ziplist 的 entry 结构**：

```
entry:
[prevlen][encoding][data]
```

- `prevlen` 记录**前一个** entry 的总长度
- 编码规则：前一个 entry < 254 字节 → 1 字节；≥ 254 字节 → 5 字节

**连锁更新触发链**：

```
① entry2 变大，跨过 254 字节阈值
② entry3 的 prevlen 需要从 1B → 5B，entry3 整体多了 4 字节
③ entry3 变大后，entry4 的 prevlen 也可能要变……
④ 像多米诺骨牌一样向后传播，最坏 O(n²) ❌
```

**listpack 的 entry 结构**：

```
entry:
[encoding][data][backlen]
```

- `backlen` 记录**当前** entry 自身总长度（不依赖任何其他 entry）
- 修改 entry N 只更新自己的 `backlen`，**不会影响任何相邻 entry** ✅

> **一句话**：ziplist 的 `prevlen` 存的是别人的信息，listpack 的 `backlen` 存的是自己的信息——我的长度我做主，连锁更新自然不存在。

**参数控制**：
- `list-max-listpack-size`（默认 -2）：控制每个 quicklistNode 的 listpack 最大大小
- `list-compress-depth`（默认 0）：两端不压缩的节点数

**为什么用 quicklist 替代纯链表**：
- 纯双向链表：每个节点存 prev/next 指针（8+8=16 字节），元素越多指针开销越大
- quicklist：多个元素共享一个节点的 listpack 数组，指针开销平摊，**内存效率大幅提升**

---

### 4. Set（集合）

**内部编码**：`intset`（全整数且数量少时） / `hashtable`

| 特性 | 说明 |
|------|------|
| 结构 | 无序、不可重复的字符串集合 |
| 支持集合运算 | 交集、并集、差集 |

**常见命令**：`SADD` `SMEMBERS` `SISMEMBER` `SCARD` `SINTER` `SUNION` `SDIFF` `SRANDMEMBER` `SPOP`

**使用场景**：

| 场景 | 示例 |
|------|------|
| **标签系统** | `SADD article:1001:tags java redis` |
| **点赞/收藏** | `SADD post:2001:likes user:1001`，`SCARD` 统计数量 |
| **共同好友** | `SINTER user:1001:friends user:1002:friends` |
| **抽奖** | `SRANDMEMBER key count` 随机抽取，`SPOP` 随机移除并返回 |
| **去重统计** | 统计独立 IP、独立用户 ID |

#### 内部实现：intset vs hashtable

**编码转换条件**：

```
intset → hashtable 转换条件（任一满足即转换）：
  - 元素数量 > set-max-intset-entries（默认 512）
  - 插入的元素不是整数（如字符串 "abc"）
```

**intset（整数集合）结构**：

```c
typedef struct intset {
    uint32_t encoding;  // 编码方式：INTSET_ENC_INT16 / INT32 / INT64
    uint32_t length;    // 元素个数
    int8_t  contents[]; // 整数数组，升序排列
} intset;
```

- 所有整数**升序排列**，查找用**二分查找** O(log n)
- 当插入的整数超过当前范围时，**整体升级**编码（如 INT16 → INT32），但**不会降级**
- **优点**：内存极紧凑（成员都是 2/4/8 字节的整数，无指针开销）
- **缺点**：插入/删除涉及内存移动，所以只在元素少时使用

**hashtable**：退化为只有 key 的字典（value 固定为 NULL），仍遵循渐进式 rehash。

---

### 5. ZSet（有序集合 / Sorted Set）

**内部编码**：`listpack`（7.0+）/ `ziplist`（旧版） / `skiplist + hashtable`

| 特性 | 说明 |
|------|------|
| 结构 | 每个元素关联一个 **score（分数）**，按 score 排序 |
| 唯一性 | member 唯一，score 可重复 |
| 底层 | **跳表**实现高效的范围查询 |

**常见命令**：`ZADD` `ZRANGE` `ZREVRANGE` `ZRANK` `ZREVRANK` `ZSCORE` `ZINCRBY` `ZRANGEBYSCORE` `ZREM` `ZCARD`

**使用场景**：

| 场景 | 示例 |
|------|------|
| **排行榜** | `ZINCRBY leaderboard:2024 score user:1001` |
| **延迟队列** | 将任务执行时间戳作为 score，`ZRANGEBYSCORE ...` 轮询到期任务 |
| **滑动窗口限流** | 时间戳作为 score，删除窗口外的旧记录 |
| **商品推荐** | 按权重排序，取 Top N 推荐 |
| **范围查询** | 按分数取范围内的数据 |

#### 内部实现：listpack / ziplist vs skiplist + hashtable

**编码转换条件**（以 7.0+ 为例）：

```
listpack → skiplist 转换条件（任一满足即转换）：
  - 元素数量 > zset-max-listpack-entries（默认 128）
  - 某个 member 长度 > zset-max-listpack-value（默认 64 字节）
```

**listpack 模式**：
- 所有 member 和 score 交替紧凑存储：`[m1][s1][m2][s2]...`
- 按 score **升序排列**，插入需移动内存
- 二分查找定位

**skiplist + hashtable 双结构**：

```
ZSet  = skiplist（按 score 排序 + 范围查询）
       + dict（按 member 查 score，O(1)）
```

为什么需要**两个结构**？

| 操作 | 用哪个结构 | 不用的后果 |
|------|-----------|-----------|
| `ZRANGE` / `ZRANGEBYSCORE`（范围查询） | **skiplist** 按顺序遍历 | 用 dict 无法按序输出 |
| `ZSCORE`（查 member 的分数） | **dict** O(1) 直接返回 | 用 skiplist 需 O(log n) 搜索 |
| `ZRANK`（查 member 的排名） | **dict** 找到 member 后，再用 skiplist 算排名 | — |
| 插入新元素 | 两个结构各插入一份 | 数据一致性问题 |

**skiplist（跳表）结构**：

```
Level 3:  head ──────────────────────────────────→ tail
Level 2:  head ──────────→ node ────────────────→ tail
Level 1:  head ──→ node ──→ node ──→ node ──→ node ──→ tail
Level 0:  head ──→ node ──→ node ──→ node ──→ node ──→ tail
```

**跳表 vs 平衡树（红黑树）**：

| | 跳表 | 红黑树 |
|--|------|--------|
| 范围查询 | ✅ 简单，沿链表遍历 | ⚠️ 中序遍历，实现复杂 |
| 实现难度 | 简单（几十行代码） | 复杂（旋转、变色） |
| 平均查找 | O(log n) | O(log n) |
| 内存占用 | 稍高（每节点多层指针） | 较低 |
| 区间锁 | ✅ 支持（范围操作只需锁部分节点） | ❌ 需锁整棵树 |

**Redis 选择跳表而不是红黑树的核心原因**：
1. **范围查询更简单**：跳表找到起点后单链表顺序遍历即可，红黑树需要中序遍历
2. **实现更简洁**：跳表插入/删除不需要复杂的旋转调整
3. **层数概率分布**：跳表通过概率决定层数，平均 O(log n)，最坏 O(n) 但概率极低

---

## 进阶数据结构

| 类型 | 特点 | 使用场景 |
|------|------|---------|
| **Bitmap** | 位图，基于 String 的位操作 | 签到、活跃用户统计（亿级用户每天 1 bit） |
| **HyperLogLog** | 基数统计，固定 12KB 内存 | UV 统计（允许 0.81% 误差） |
| **GEO** | 地理位置，底层 ZSet + GeoHash 编码 | 附近的人、附近商家 |
| **Stream** | 消息队列，支持消费组、ACK | 可靠消息队列（替代 List + Pub/Sub） |

## 选择口诀

```
简单缓存用 String，对象存储用 Hash
消息队列用 List，去重判断用 Set
排行榜单用 ZSet，签到统计 Bitmap
UV 统计 HyperLogLog，附近的人就用 GEO
可靠消息选 Stream，数据结构别选错
```

## 持久化

### RDB（Redis Database）

基于内存快照的持久化方式，将某一时刻的全量数据写入磁盘。

**触发方式**：

| 方式 | 命令/配置 | 特点 |
|------|----------|------|
| **手动** | `SAVE` | **同步**阻塞，主进程生成 RDB 文件，期间不处理任何请求 |
| **手动** | `BGSAVE` | **异步**，fork 子进程生成 RDB，主进程继续处理请求（推荐） |
| **自动** | `save m n` 配置 | m 秒内有 n 次写操作时自动执行 BGSAVE |

**RDB 文件格式**：

```
RDB 文件 = 魔数(9B) + 数据集(Sorted) + 校验和(8B)
```

**优点**：
- **文件紧凑**，二进制格式，体积小，适合备份和跨网络传输
- **恢复速度最快**，直接加载到内存即可
- 子进程生成，**主进程不进行磁盘 I/O**

**缺点**：
- **可能丢数据**：两次快照之间的数据在宕机时全部丢失
- `fork` 子进程时，如果数据量大（如 10GB+），fork 耗时较长
- **写时复制（Copy-on-Write）导致内存飙升**：`BGSAVE` fork 后父子进程共享物理内存，主进程写数据时会触发 COW——**谁写谁复制**，主进程要修改某个页时，操作系统分配新物理页、复制原数据，然后**主进程页表指向新页**，原共享页被子进程独享。如果写入密集导致大量页被复制，可能接近翻倍

> **COW 详细流程**：fork 后父子进程共享同一块物理内存（页表指向同一地址），所有页标记为**只读**。当主进程收到写请求时：① 操作系统分配一页新物理内存 ② 将原共享页数据复制到新页 ③ 主进程页表指向新页（标记为可写，后续直接改新页）④ 原共享页只剩子进程引用。子进程始终读到 fork 时的快照。子进程退出后，共享页自动释放。

### AOF（Append Only File）

基于**操作日志追加**的持久化方式，记录每条写命令。

**写入流程**：

```
客户端命令 → 追加到 AOF buffer → 根据刷盘策略写入文件
```

**刷盘策略（`appendfsync`）**：

| 策略 | 行为 | 安全性 | 性能 |
|:----:|------|:------:|:----:|
| `always` | 每次写命令都 fsync | 不丢数据 ✅ | ❌ 差 |
| `everysec`（默认） | 每秒 fsync 一次 | 丢 1 秒数据 | ✅ 好 |
| `no` | 由操作系统决定刷盘时机 | 丢较多数据 | 🚀 最快 |

**AOF 重写（Rewrite）**：

**问题**：AOF 文件持续追加会越来越大，加载变慢。

**解决**：`BGREWRITEAOF` 用子进程将内存中的数据转化为最小命令集，生成新 AOF 替换旧文件。

> **COW 说明**：`BGREWRITEAOF` 同样基于 `fork()` + COW 机制，与 `BGSAVE` 完全一样。子进程读取 fork 时的共享内存快照生成新 AOF，主进程继续处理写请求。写入密集时同样可能因 COW 导致内存飙升，且 AOF 重写通常比 RDB 触发更频繁，实践中影响反而更大。

```
原始 AOF：SET k1 v1 → DEL k1 → SET k1 v2 → SET k1 v3
重写后：   SET k1 v3（只保留最终状态）
```

**重写触发条件（`auto-aof-rewrite-percentage` 和 `auto-aof-rewrite-min-size`）**：
- AOF 文件大小超过上次重写时的**百分比**（默认 100%）
- 且文件大小超过**最小阈值**（默认 64MB）

#### AOF 重写的阻塞问题

**重写期间的双缓冲区机制**：

```
BGREWRITEAOF 期间：
主进程                         子进程
  │                              │
  ├─ 写命令 → AOF 缓冲区（正常写入AOF文件） │
  ├─ 写命令 → AOF 重写缓冲区             │
  │                              ├─ 读取内存快照生成新 AOF
  │                              ├─ 完成后发送信号给主进程
  │ ←──────── 信号 ──────────────┤
  │                              │
  ├─ 阻塞！将重写缓冲区的增量命令追加到新 AOF ❌
  ├─ 用新 AOF 替换旧 AOF
  └─ 恢复处理请求 ✅
```

**为什么会有两个缓冲区**？

| 缓冲区 | 作用 |
|--------|------|
| **AOF 缓冲区** | 正常写入旧 AOF 文件，保证宕机时可恢复 |
| **AOF 重写缓冲区** | 记录重写期间的所有写命令，防止数据丢失 |

**阻塞时刻**：子进程完成重写后，主进程需要将重写缓冲区中的数据**同步追加**到新 AOF 文件，这个过程是**阻塞**的（不阻塞会导致数据不一致）。追加完成后用新 AOF 替换旧文件，才恢复处理请求。

> **阻塞时长**取决于重写期间积累了多少增量命令，通常很短（毫秒级）。如果写入量极大导致重写缓冲区很大，阻塞时间会变长。
### RDB vs AOF

| 对比维度 | RDB | AOF |
|--------|-----|-----|
| 数据完整性 | 可能丢两次快照间的数据 | 最多丢 1 秒数据（everysec） |
| 恢复速度 | **快**（直接加载二进制快照） | **慢**（逐条回放命令） |
| 文件大小 | **小**（二进制压缩） | **大**（文本协议 + 重复命令） |
| 对性能影响 | fork 子进程，主进程几乎无影响 | 写频率高时刷盘可能卡顿 |
| 适用场景 | 备份、灾难恢复、冷备 | 数据完整性要求高的场景 |

### Redis 4.0+ 混合持久化

```conf
aof-use-rdb-preamble yes
```

**思路**：AOF 重写时，将当前内存数据先以 RDB 格式写入 AOF 文件头部，后续增量命令以 AOF 格式追加。

**优点**：
- **加载快**：RDB 部分直接加载，不用逐条回放
- **丢数据少**：AOF 部分最多丢 1 秒
- 文件比纯 AOF 小

---

## 大 Key 影响

### 什么是大 Key

| 维度 | 判断标准 | 示例 |
|------|---------|------|
| **单个 String** | value > **10 KB** | 存了大 JSON 或序列化数据 |
| **集合类型** | 元素数量 > **1 万** 或 整体大小 > **1 MB** | 大的 Hash / List / Set / ZSet |
| **大 Value 集合** | 单个元素 value 很大 | List 里每个元素都是大字符串 |

### 大 Key 的危害

| 问题 | 原因 | 具体表现 |
|------|------|---------|
| **阻塞请求** | 操作大 key 耗时久（如 `HGETALL` 百万字段的 Hash） | 单线程模型下**所有请求排队**，RT 飙升 |
| **内存不均** | 大 key 集中在某个 Redis 实例 | 集群模式下**数据倾斜**，部分节点 OOM |
| **网络带宽** | 读取大 key 返回大量数据 | 出口带宽打满，影响其他请求 |
| **持久化风险** | RDB 生成 / AOF 重写时 | fork 耗时变长，写时复制导致内存翻倍 |
| **删除阻塞** | `DEL` 大 key | 删除大集合需遍历释放内存，阻塞主线程数十秒 |

### 如何发现大 Key

```bash
# 方式一：redis-cli 扫描（推荐）
redis-cli --bigkeys

# 方式二：手动用 SCAN + TYPE + 查看大小
SCAN 0
MEMORY USAGE key
STRLEN key   # String 长度
HLEN key     # Hash 字段数
LLEN key     # List 长度
SCARD key    # Set 大小
ZCARD key    # ZSet 大小

# 方式三：使用 redis-rdb-tools 分析 RDB 文件
```

### 大 Key 处理方案

| 方案 | 做法 | 适用场景 |
|------|------|---------|
| **拆分** | 大 Hash 拆成多个小 Hash（按 field 哈希分桶） | 大集合类型 |
| **压缩** | 用压缩算法（gzip/snappy）压缩 value 后存入 | 大 String（如大 JSON） |
| **本地缓存** | 热点大 key 在应用层做本地缓存 | 读多写少的大 key |
| **异步删除** | `UNLINK key`（后台回收内存，不阻塞主线程） | 必须删除大 key 时 |
| **定期清理** | 设置 TTL 或用 `EXPIRE` 自动过期 | 临时数据 |
| **滚动删除** | 用 `LRANGE` / `SSCAN` 分批删 | 需要删除大集合部分元素时 |

> **原则**：设计阶段就避免大 key，分桶、分片、限制单个 key 的大小是更根本的解法。
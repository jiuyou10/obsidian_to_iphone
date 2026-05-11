## 集合框架

### 集合体系

```
Collection（单列）
├── List（有序可重复）
│   ├── ArrayList  → 数组结构
│   ├── LinkedList → 双向链表
│   └── Vector     → 线程安全数组（已过时）
├── Set（无序不可重复）
│   ├── HashSet       → HashMap 实现
│   ├── LinkedHashSet → 可维护插入顺序
│   └── TreeSet       → 红黑树，可排序
└── Queue
    ├── PriorityQueue → 堆结构
    └── ArrayDeque    → 双端队列

Map（键值对）
├── HashMap       → 数组+链表+红黑树
├── LinkedHashMap → 维护插入/访问顺序
├── TreeMap       → 红黑树，key 可排序
└── ConcurrentHashMap → 线程安全
```

### ArrayList

- **底层**：`Object[]` 数组
- **默认容量**：10（JDK 8 懒加载，首次 add 才初始化）
- **扩容**：`newCapacity = oldCapacity + (oldCapacity >> 1)` → **1.5 倍**
- **特点**：随机访问 O(1)，中间插入/删除 O(n)
- **实现 RandomAccess 接口**：标记接口，表明支持快速随机访问，`Collections.binarySearch()` 会据此选择用索引遍历而非迭代器

### LinkedList

- **底层**：**双向链表**（Node 有 prev / next / item）
- **特点**：头尾插入/删除 O(1)，中间插入 O(n)，随机访问 O(n)
- **双向队列**：实现了 Deque 接口，可作为栈 / 队列使用

| 对比 | ArrayList | LinkedList |
|---|---|---|
| 底层 | 数组 | 双向链表 |
| 随机访问 | O(1) | O(n) |
| 头尾插入 | O(n) | O(1) |
| 内存 | 连续空间，更紧凑 | 每个元素多存前后指针 |
| 扩容 | 1.5 倍扩容，有拷贝开销 | 无扩容概念 |

### List 的线程安全实现

**List 本身不保证线程安全**，多线程同时读写 `ArrayList` 或 `LinkedList` 时，可能出现数据覆盖、读到脏数据，甚至抛出异常。

常见方案：

| 方式 | 特点 | 适用场景 |
|---|---|---|
| `Collections.synchronizedList(list)` | 给普通 List 包一层同步壳 | 临时兼容旧代码 |
| `CopyOnWriteArrayList` | 写时复制，读不加锁 | 读多写少，比如监听器列表、配置快照 |

**CopyOnWriteArrayList** 的核心是：读操作不加锁，直接读取当前数组快照；写操作通过 `ReentrantLock` 加锁，复制一份新数组，在新数组上修改，最后用新数组替换旧数组引用。

**为什么需要它**：解决多线程遍历 List 时，另一个线程修改集合导致的并发问题。

**什么时候用**：适合读多写少的场景；如果写操作很频繁，不适合用它，因为每次写都会复制数组，内存和性能开销都比较大。

---

### HashMap

**HashMap** 是基于哈希表实现的键值对容器，用来根据 **key** 快速定位 **value**。平均情况下，`put()` / `get()` 接近 O(1)，但它不保证遍历顺序，也不是线程安全的。

#### 底层结构

```
JDK 7：数组 + 链表（头插法）
JDK 8：数组 + 链表（尾插法） + 红黑树
```

- **默认容量**：16（`1 << 4`）
- **加载因子**：0.75
- **树化阈值**：链表长度 ≥ 8 且数组长度 ≥ 64 → 转红黑树
  - 链表短时遍历成本低，转红黑树反而有额外维护成本；数组长度小于 64 时，优先扩容让元素重新分散，而不是急着树化
- **退化阈值**：红黑树节点 ≤ 6 → 退化为链表
- **红黑树**：一种自平衡二叉搜索树，通过旋转和变色保持近似平衡，把桶内查询从 O(n) 降到 O(log n)

#### 哈希函数如何设计

```java
hash = key.hashCode() ^ (key.hashCode() >>> 16);
index = (n - 1) & hash;
```

`HashMap` 会先取 key 的 `hashCode()`，再用高 16 位异或低 16 位做一次**扰动**。因为数组长度是 2 的幂，定位下标时主要看低位；让高位也参与计算，可以减少低位相同导致的冲突。

#### 如何减少和解决哈希冲突

**哈希冲突** 是指不同 key 算出了相同数组下标。常见解决方法有开放寻址法、链地址法、再哈希法、公共溢出区；`HashMap` 使用的是**链地址法**。

`HashMap` 减少冲突主要靠这几件事：
- 好的 `hashCode()` 尽量让 key 分布均匀
- 扰动函数让高位信息参与下标计算
- 加载因子 0.75 控制扩容时机，避免桶过满
- 链表过长时转红黑树，避免查询退化太严重

#### put 流程

```java
put(key, value):
  1. 计算 hash = key.hashCode() ^ (key.hashCode() >>> 16)
  2. 计算槽位 index = (n - 1) & hash
  3. 若槽位为空 → 直接插入
  4. 若槽位不为空 → 判断 key 是否 equals:
     - 相同 → 覆盖 value
     - 不同 → 尾插法追加到链表 / 红黑树
  5. 链表长度 ≥ 8 且数组长度 ≥ 64 → 树化
  6. size > threshold（capacity × loadFactor）→ resize
```

#### get 流程

```java
get(key):
  1. 计算 hash 和槽位
  2. 槽位为空 → 返回 null
  3. 槽位不为空 → 遍历链表/红黑树，equals 匹配
  4. 匹配到 → 返回 value，否则返回 null
```

#### 扩容（resize）

- **触发条件**：`size > threshold`，其中 `threshold = capacity × loadFactor`
- **新容量**：`oldCapacity << 1`（2 倍）
- **JDK 8 优化**：不需要重新计算完整 hash，只需要判断 `(hash & oldCap)`：
  - 等于 0 → 留在原位置
  - 不等于 0 → 移到 `原位置 + oldCap`
- **是否每个节点都要位运算**：需要遍历每个节点，并做一次 `(hash & oldCap)` 判断；但不需要重新算 `hashCode()` 或完整取模

#### 为什么容量是 2 的幂？

- `(n - 1) & hash` 等价于 `hash % n`，但位运算更快
- 扩容后元素要么在原位，要么在原位 + oldCap，方便迁移

#### 加载因子为什么是 0.75？

0.75 是时间和空间的折中：太小会频繁扩容、浪费空间；太大又会让桶内元素变多、冲突增加。

#### JDK 8 对 HashMap 做了哪些优化

- **链表转红黑树**：链表过长时降低查询成本
- **头插法改尾插法**：避免 JDK 7 并发扩容时更容易出现链表成环
- **扩容迁移优化**：用 `(hash & oldCap)` 判断新位置，不再完整重算 hash
- **懒初始化**：table 首次 `put()` 时才真正创建

#### HashMap 是否线程安全

`HashMap` **不是线程安全的**。多线程同时 `put()`、`remove()` 或 `resize()` 时，可能出现数据覆盖、数据丢失、读到脏数据等问题。JDK 8 虽然改了尾插法，降低了 JDK 7 并发扩容链表成环的风险，但并不代表它线程安全；并发场景应使用 `ConcurrentHashMap`。
### ConcurrentHashMap

| 版本 | 锁粒度 | 实现方式 |
|---|---|---|
| JDK 7 | Segment（分段锁） | 继承 ReentrantLock，默认 16 个 Segment |
| JDK 8 | 数组槽位（细粒度锁） | synchronized + CAS，锁住链表头节点 |

**JDK 8 核心**：
- put：槽位为空 → CAS 插入；不为空 → `synchronized` 锁头节点，遍历插入
- get：**不加锁**（value 和 next 用 volatile 保证可见性）
- 扩容：多线程协助扩容（`ForwardingNode`）

### HashSet

- **底层**：基于 HashMap，value 固定为一个 `PRESENT` 对象（`new Object()`）
- **无序**：不保证插入顺序（如需有序用 `LinkedHashSet`）

### LinkedHashMap

- **继承 HashMap**，额外维护一条**双向链表**记录顺序
- **accessOrder**：`false`（默认）按插入顺序；`true` 按访问顺序（可用作 LRU 缓存）
- **LRU 实现**：重写 `removeEldestEntry()`，当容量超限时删除链表头部

### TreeMap

**TreeMap** 是基于红黑树实现的有序 `Map`，会按照 key 的自然顺序或传入的 `Comparator` 排序。

| 对比 | HashMap | TreeMap |
|---|---|---|
| 底层 | 哈希表 | 红黑树 |
| 顺序 | 不保证顺序 | 按 key 排序 |
| 性能 | 平均 O(1) | O(log n) |
| key 要求 | 依赖 `hashCode()` / `equals()` | key 可比较或提供 `Comparator` |
| 使用场景 | 快速查找 | 有序遍历、范围查询 |

**什么时候用**：只关心快速查找时优先用 `HashMap`；需要按 key 排序、取最大/最小 key、做范围查询时用 `TreeMap`。

---

### fail-fast vs fail-safe

| | fail-fast | fail-safe |
|---|---|---|
| 检测时机 | 修改结构时立即抛出 | 修改时不抛异常 |
| 实现原理 | modCount 计数器 | 拷贝原集合的快照 |
| 示例 | ArrayList、HashMap 的迭代器 | ConcurrentHashMap、CopyOnWriteArrayList |
| 说明 | 迭代过程中检测到结构修改 → `ConcurrentModificationException` | 遍历的是快照，代价是内存和一致性 |

### Collections 工具类

常用方法：
- `Collections.sort(list)` → 排序
- `Collections.binarySearch(list, key)` → 二分查找
- `Collections.reverse(list)` → 反转
- `Collections.shuffle(list)` → 打乱
- `Collections.unmodifiableList(list)` → 返回不可变视图
- `Collections.synchronizedList(list)` → 返回同步包装（已不推荐，性能差）


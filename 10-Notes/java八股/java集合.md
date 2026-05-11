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

### HashMap

#### 底层结构

```
JDK 7：数组 + 链表（头插法）
JDK 8：数组 + 链表（尾插法） + 红黑树
```

- **默认容量**：16（`1 << 4`）
- **加载因子**：0.75
- **树化阈值**：链表长度 ≥ 8 且数组长度 ≥ 64 → 转红黑树
- **退化阈值**：红黑树节点 ≤ 6 → 退化为链表

#### put 流程

```java
put(key, value):
  1. 计算 hash = key.hashCode() ^ (key.hashCode() >>> 16)  // 扰动函数
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

- **新容量**：`oldCapacity << 1`（2 倍）
- **重哈希**：JDK 7 全部重算；JDK 8 优化：`(hash & oldCap) == 0` 的留在原位置，否则移到 `原位置 + oldCap`
- **尾插法**：JDK 8 改为尾插法，解决了 JDK 7 头插法在并发扩容时的死循环问题

#### 为什么容量是 2 的幂？

- `(n - 1) & hash` 等价于 `hash % n`（位运算更快）
- 扩容后元素要么在原位，要么在原位 + oldCap，无需重算 hash

#### 加载因子为什么是 0.75？

时间与空间的平衡：0.75 时泊松分布下链表长度 ≥ 8 的概率极低（约 0.00000006），保证了红黑树几乎不会被触发

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


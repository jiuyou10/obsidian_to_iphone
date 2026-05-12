### 内存泄漏可能由哪些原因导致？



内存泄漏指不再使用的对象仍被 GC Roots 引用，导致 GC 无法回收。

**常见原因**：

1. **静态集合类**（如 `static List`、`static Map`）
   - 生命周期 = JVM 生命周期，只增不减
   - 解决：用 `WeakHashMap` 或及时 remove
1. **未关闭的资源**
   - `InputStream`、`Connection`、`Socket` 等未 close
   - 解决：try-with-resources 自动关闭
1. **equals / hashCode 实现不当**
   - 对象放入 HashSet/HashMap 后修改了 hashCode 字段 → 无法删除，成为"脏"对象
   - 解决：不要用可变字段参与 hashCode；或者用 `TreeSet`/`TreeMap`

4. **内部类持有外部类隐式引用**
   - 非静态内部类隐式持有外部类 `this`
   - 外部类无法 GC 直到内部类也被释放
   - 解决：用静态内部类

5. **ThreadLocal 未清理**
   - ThreadLocalMap 的 key 是弱引用（自动清理），但 value 是强引用
   - 线程池复用线程时 value 一直残留
   - 解决：每次用完调用 `ThreadLocal.remove()`

6. **缓存 / 注册监听器未反注册**
   - 添加了 `addListener` 但忘记 `removeListener`
   - 解决：弱引用监听器或用 `WeakHashMap` 做缓存

7. **JIT 相关**
   - JIT 编译后的代码存储在 **Code Cache**（属于 Metaspace / Native Memory）
   - 类卸载时 JIT 编译代码未及时清理 → Code Cache 泄漏
   - 常见于热部署（类加载器泄漏导致 JIT 代码也无法释放）

8. **垃圾收集相关**
   - **Finalizer 堆积**：重写 `finalize()` 的对象需至少两次 GC 才能回收，队列处理不及时会堆积
   - **大对象直接进入老年代**：如果大对象创建速率 > GC 回收速率，老年代持续增长
   - **Concurrent Mode Failure**：CMS GC 时老年代被快速填满，触发 Full GC 频率升高

**检测工具**：
- `jmap -histo:live` 查看堆中存活对象
- `jstack` + MAT / JProfiler 分析引用链
- `-XX:+PrintGCDetails` 观察 GC 日志

---

### 垃圾收集（GC）

#### 判断对象是否存活

| 算法 | 原理 | 问题 |
|---|---|---|
| **引用计数法** | 每对象维护引用计数器，为 0 则回收 | 无法解决循环引用（Python 用，Java 不用） |
| **可达性分析** | 从 GC Roots 向下搜索，不可达的对象可回收 | Java 采用 |

#### GC Roots

**概念**：可达性分析的起点，从这些根对象出发向下搜索引用链，不可达的对象判定为可回收。

**为什么叫 Roots**？类比植物根系：从根部出发能顺着引用链到达的对象都是"存活"的，到达不了的就是"垃圾"。

**GC Roots 有哪些**：

| GC Root | 说明 | 示例 |
|---|---|---|
| **栈帧局部变量** | 正在执行的方法中声明的对象引用，方法结束即移除 | `main()` 中的局部对象 |
| **静态变量** | 类变量，生命周期 = JVM 生命周期 | `private static List list` |
| **JNI 引用** | native 方法中创建的全局/局部引用 | JNI 中 `NewGlobalRef` |
| **活跃线程** | 正在运行的 Thread 对象本身 | `Thread.currentThread()` |
| **synchronized 持有** | 被 synchronized 锁住的对象 | `synchronized(obj)` 中的 obj |

> **注意**：GC Roots 不是固定的集合，不同类型的 GC（Minor GC / Full GC）会选取不同的 Roots。Minor GC 只需扫描新生代 Roots + Card Table 记录的跨代引用，Full GC 才全量扫描。

**GC 如何找到 Roots？**

每次 GC 时不可能遍历所有内存去找引用，Java 通过 **OopMap** 解决：
- JIT 编译时在 **Safe Point** 处记录 OopMap，标明栈上和寄存器中哪些位置是对象引用
- GC 发生时，所有线程必须跑到最近的 Safe Point 停下（STW），然后直接读取 OopMap 中的 Roots
- 避免全栈扫描，大幅提升 GC 效率

**引用类型**：

| 类型 | 回收时机 | 用途 |
|---|---|---|
| 强引用 | 永不回收 | `new` 普通对象 |
| 软引用 | OOM 前回收 | 缓存（`SoftReference`） |
| 弱引用 | 下次 GC 即回收 | `ThreadLocalMap` key、`WeakHashMap` |
| 虚引用 | 任何时候 | 跟踪对象被回收（`PhantomReference` + `ReferenceQueue`） |

#### 垃圾收集算法

| 算法 | 描述 | 优缺点 |
|---|---|---|
| **标记-清除** | 标记存活对象 → 清除未标记的 | 产生内存碎片 |
| **标记-复制** | 将存活对象复制到另一块空间，原空间整块清空 | 无碎片；浪费一半空间（新生代用此法） |
| **标记-整理** | 标记存活 → 将所有存活对象向一端移动 | 无碎片，但移动开销大（老年代用此法） |
| **分代收集** | 新生代用复制算法，老年代用标记-清除/整理 | 各取所长 |

#### 分代结构（默认 G1 之前）

```
 ┌──────────┬──────────┬─────────────┐
 │  Eden    │ Survivor │   老年代     │
 │  (80%)   │  (20%)   │  (Full GC)  │
 ├──────────┤          │             │
 │ 新生代   │──────────│             │
 │ Minor GC │  复制    │             │
 └──────────┴──────────┴─────────────┘
```

- **新生代**：Eden（80%）+ 两个 Survivor（各 10%），Minor GC 用复制算法
- **老年代**：对象年龄足够大（默认 15）后晋升，Major / Full GC
- **元空间**（Metaspace，JDK 8+）：替代永久代，存储类元数据，使用本地内存

#### 垃圾收集器

| 收集器 | 代 | 算法 | 线程 | STW | 适用场景 |
|---|---|---|---|---|---|---|
| **Serial** | 新生代 | 复制 | 单线程 | 较长 | 客户端模式、单核 |
| **ParNew** | 新生代 | 复制 | 多线程 | 较短 | CMS 搭档 |
| **Parallel Scavenge** | 新生代 | 复制 | 多线程 | 可控 | 吞吐量优先（后台计算） |
| **Serial Old** | 老年代 | 标记-整理 | 单线程 | 较长 | Serial 的老年代搭档 |
| **Parallel Old** | 老年代 | 标记-整理 | 多线程 | 可控 | Parallel Scavenge 的老年代搭档 |
| **CMS** | 老年代 | 标记-清除 | 并发 | 短 | 低延迟（已废弃） |
| **G1** | 全代 | 分区 + 复制 | 并发/并行 | 可预测 | 默认（JDK 9+），大堆 |
| **ZGC** | 全代 | 染色指针 | 并发 | < 10ms | 超大堆，低延迟 |
| **Shenandoah** | 全代 | 并发整理 | 并发 | < 10ms | 低延迟（Red Hat） |

**CMS 的问题**（为什么被 G1 替代）：
- 标记-清除 → 内存碎片 → 提前 Full GC
- 并发阶段占用 CPU，降低吞吐量
- **Concurrent Mode Failure**：老年代在 CMS 完成前被填满 → 退化为 Serial Old Full GC

**G1 核心特点**：
- 堆划分为多个 Region（约 2048 个），每个 Region 可扮演 Eden / Survivor / Old
- **可预测的停顿时间**：`-XX:MaxGCPauseMillis`（默认 200ms）
- 维护 **Remembered Set** 记录跨 Region 引用，避免全堆扫描
- 分为 Young GC（新生代满）和 Mixed GC（老年代达到阈值）

#### 关键概念

| 概念 | 说明 |
|---|---|
| **STW**（Stop The World） | GC 时所有用户线程暂停，必须尽可能短 |
| **Safe Point** | 线程可暂停的位置（方法调用、循环末尾等），GC 需要线程跑到 Safe Point 才能 STW |
| **OopMap** | 记录栈上哪些位置是对象引用，供 GC 扫描 Roots 用 |
| **Card Table** | 老年代 Region 中记录哪些卡页有跨代引用，避免全堆扫描 |
| **三色标记** | 黑（已扫描子对象）/ 灰（自身已标记，子对象未扫描完）/ 白（未标记） |
| **SATB**（Snapshot At The Beginning） | G1 的并发标记算法，记录开始时的快照，防止漏标 |

#### GC 调优常用参数

```
-Xms4g -Xmx4g                     # 堆大小（建议设相等避免扩容）
-Xmn2g                            # 新生代大小
-XX:MetaspaceSize=256m            # 元空间初始大小
-XX:+UseG1GC                      # 使用 G1（JDK 9+ 默认）
-XX:MaxGCPauseMillis=200          # G1 目标停顿时间
-XX:ParallelGCThreads=8           # 并行 GC 线程数
-XX:+PrintGCDetails               # 打印 GC 日志（JDK 8）
-Xlog:gc*                         # 打印 GC 日志（JDK 9+）
```

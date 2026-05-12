jvmJVM 可以自动管理内存，通过垃圾回收器回收不再使用的对象并释放内存空间。

②、JVM 包含一个即时编译器 JIT，它可以在运行时将热点代码缓存到 codeCache 中，下次执行的时候不用再一行一行的解释，而是直接执行缓存后的机器码，执行效率会大幅提高。


任何可以通过 Java 编译的语言，比如说 Groovy、Kotlin、Scala 等，都可以在 JVM 上运行。

jvm的组织结构
### [一个操作系统有两个Java程序的话，有几个虚拟机？有没有单独的JVM进程存在？启动一个hello world编译的时候，有几个进程]

jvm内存区域
#### [一个什么都没有的空方法，空的参数都没有，那局部变量表里有没有变量？](https://javabetter.cn/sidebar/sanfene/jvm.html#%E4%B8%80%E4%B8%AA%E4%BB%80%E4%B9%88%E9%83%BD%E6%B2%A1%E6%9C%89%E7%9A%84%E7%A9%BA%E6%96%B9%E6%B3%95-%E7%A9%BA%E7%9A%84%E5%8F%82%E6%95%B0%E9%83%BD%E6%B2%A1%E6%9C%89-%E9%82%A3%E5%B1%80%E9%83%A8%E5%8F%98%E9%87%8F%E8%A1%A8%E9%87%8C%E6%9C%89%E6%B2%A1%E6%9C%89%E5%8F%98%E9%87%8F)

对于[静态方法](https://javabetter.cn/oo/static.html)，由于不需要访问实例对象 this，因此在局部变量表中不会有任何变量。

对于非静态方法，即使是一个完全空的方法，局部变量表中也会有一个用于存储 this 引用的变量。this 引用指向当前实例对象，在方法调用时被隐式传入。

java内存，堆栈方法区，以及变量/静态变量都存在什么地方
对象创建的过程以及销毁
堆分配内存的方式，分配空间时堆会抢占吗

对象的内存布局是由 Java 虚拟机规范定义的，但具体的实现细节各有不同，如 HotSpot 和 OpenJ9 就不一样。

就拿我们常用的 HotSpot 来说吧。对象在内存中包括三部分：对象头、实例数据和对齐填充

堆的内存分区
新生代的区域，以及对象什么时候会进入老年代
#### [大对象如何判断？](https://javabetter.cn/sidebar/sanfene/jvm.html#%E5%A4%A7%E5%AF%B9%E8%B1%A1%E5%A6%82%E4%BD%95%E5%88%A4%E6%96%AD)

大对象是指占用内存较大的对象，如大数组、长字符串等。

```
int[] array = new int[1000000];
String str = new String(new char[1000000]);
```

其大小由 JVM 参数 `-XX:PretenureSizeThreshold` 控制，但在 JDK 8 中，默认值为 0，也就是说默认情况下，对象仅根据 GC 存活的次数来判断是否进入老年代。

![二哥的 Java 进阶之路：PretenureSizeThreshold](https://cdn.paicoding.com/stutymore/jvm-20250113102243.png)
![[Pasted image 20260512154136.png]]
G1 垃圾收集器中，大对象会直接分配到 HUMONGOUS 区域。当对象大小超过一个 Region 容量的 50% 时，会被认为是大对象。
JVM 进行垃圾回收的过程中，会涉及到对象的移动，为了保证对象引用在移动过程中不被修改，必须暂停所有的用户线程，像这样的停顿，我们称之为`Stop The World`。简称 STW。

#### [如何暂停线程呢？](https://javabetter.cn/sidebar/sanfene/jvm.html#%E5%A6%82%E4%BD%95%E6%9A%82%E5%81%9C%E7%BA%BF%E7%A8%8B%E5%91%A2)

JVM 会使用一个名为安全点（Safe Point）的机制来确保线程能够被安全地暂停，其过程包括四个步骤：
默认情况下，Java 对象是在堆中分配的，但 JVM 会进行逃逸分析，来判断对象的生命周期是否只在方法内部，如果是的话，这个对象可以在栈上分配。
### [21.有没有处理过内存溢出问题？](https://javabetter.cn/sidebar/sanfene/jvm.html#_21-%E6%9C%89%E6%B2%A1%E6%9C%89%E5%A4%84%E7%90%86%E8%BF%87%E5%86%85%E5%AD%98%E6%BA%A2%E5%87%BA%E9%97%AE%E9%A2%98)

有。

				当时在做[技术派](https://javabetter.cn/zhishixingqiu/paicoding.html)的时候，由于上传的文件过大，没有正确处理，导致一下子撑爆了内存，程序直接崩溃了。

我记得是通过导出堆转储文件进行分析发现的。

第一步，使用 jmap 命令手动生成 Heap Dump 文件：

```
jmap -dump:format=b,file=heap.hprof <pid>
```

然后使用 MAT、JProfiler 等工具进行分析，查看内存中的对象占用情况。

一般来说：

如果生产环境的内存还有很多空余，可以适当增大堆内存大小来解决，例如 `-Xmx4g` 参数。

或者检查代码中是否存在内存泄漏，如未关闭的资源、长生命周期的对象等。

之后，在本地进行压力测试，模拟高负载情况下的内存表现，确保修改有效，且没有引入新的问题。
栈溢出发生在程序调用栈的深度超过 JVM 允许的最大深度时。

栈溢出的本质是因为线程的栈空间不足，导致无法再为新的栈帧分配内存。

垃圾收集
GC Roots 包括以下几种：

- 虚拟机栈中的引用（方法的参数、局部变量等）
- 本地方法栈中 JNI 的引用
- 类静态变量
- 运行时常量池中的常量（String 或 Class 类型）
minor gc，major gc mixed gc  full gc

cms和g1区别
### [37.用过哪些性能监控的命令行工具？](https://javabetter.cn/sidebar/sanfene/jvm.html#_37-%E7%94%A8%E8%BF%87%E5%93%AA%E4%BA%9B%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E7%9A%84%E5%91%BD%E4%BB%A4%E8%A1%8C%E5%B7%A5%E5%85%B7)

操作系统层面，我用过 top、vmstat、iostat、netstat 等命令，可以监控系统整体的资源使用情况，比如说内存、CPU、IO 使用情况、网络使用情况。

JDK 自带的命令行工具层面，我用过 jps、jstat、jinfo、jmap、jhat、jstack、jcmd 等，可以查看 JVM 运行时信息、内存使用情况、堆栈信息等。

#### [你一般都怎么用jmap？](https://javabetter.cn/sidebar/sanfene/jvm.html#%E4%BD%A0%E4%B8%80%E8%88%AC%E9%83%BD%E6%80%8E%E4%B9%88%E7%94%A8jmap)
### [38.了解哪些可视化的性能监控工具？](https://javabetter.cn/sidebar/sanfene/jvm.html#_38-%E4%BA%86%E8%A7%A3%E5%93%AA%E4%BA%9B%E5%8F%AF%E8%A7%86%E5%8C%96%E7%9A%84%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E5%B7%A5%E5%85%B7)

我自己用过的可视化工具主要有：
### [40.做过 JVM 调优吗？](https://javabetter.cn/sidebar/sanfene/jvm.html#_40-%E5%81%9A%E8%BF%87-jvm-%E8%B0%83%E4%BC%98%E5%90%97)

做过。

JVM 调优是一个复杂的过程，调优的对象包括堆内存、垃圾收集器和 JVM 运行时参数等。
![[Pasted image 20260512154622.png]]

### [CPU 占用过高怎么排查？](https://javabetter.cn/sidebar/sanfene/jvm.html#_41-cpu-%E5%8D%A0%E7%94%A8%E8%BF%87%E9%AB%98%E6%80%8E%E4%B9%88%E6%8E%92%E6%9F%A5)

答：首先，使用 top 命令查看 CPU 占用情况，找到占用 CPU 较高的进程 ID。接着，使用 jstack 命令查看对应进程的线程堆栈信息。然后再使用 top 命令查看进程中线程的占用情况，找到占用 CPU 较高的线程 ID。

接着在 jstack 的输出中搜索这个十六进制的线程 ID，找到对应的堆栈信息。最后，根据堆栈信息定位到具体的业务方法，查看是否有死循环、频繁的垃圾回收、资源竞争导致的上下文频繁切换等问题。
### [42.内存飙高问题怎么排查？](https://javabetter.cn/sidebar/sanfene/jvm.html#_42-%E5%86%85%E5%AD%98%E9%A3%99%E9%AB%98%E9%97%AE%E9%A2%98%E6%80%8E%E4%B9%88%E6%8E%92%E6%9F%A5)

内存飚高一般是因为创建了大量的 J
### [43.频繁 minor gc 怎么办？](https://javabetter.cn/sidebar/sanfene/jvm.html#_43-%E9%A2%91%E7%B9%81-minor-gc-%E6%80%8E%E4%B9%88%E5%8A%9E)

频繁的 Minor GC 通常意味着新生代中的对象频繁地被垃圾回收，可能是因为新生代空间设置的过小，或者是因为程序中存在大量的短生命周期对象（如临时变量）。

可以使用 GC 日志进行分析，查看 GC 的频率和耗时，找到频繁 GC 的原因。
### [44.频繁 Full GC 怎么办？](https://javabetter.cn/sidebar/sanfene/jvm.html#_44-%E9%A2%91%E7%B9%81-full-gc-%E6%80%8E%E4%B9%88%E5%8A%9E)

频繁的 Full GC 通常意味着老年代中的对象频繁地被垃圾回收，可能是因为老年代空间设置的过小，或者是因为程序中存在大量的长生命周期对象。

#### [该怎么排查 Full GC 频繁问题？](https://javabetter.cn/sidebar/sanfene/jvm.html#%E8%AF%A5%E6%80%8E%E4%B9%88%E6%8E%92%E6%9F%A5-full-gc-%E9%A2%91%E7%B9%81%E9%97%AE%E9%A2%98)

其中最重要的三个概念就是：类加载器、类加载过程和双亲委派模型。

- **类加载器**：负责加载类文件，将类文件加载到内存中，生成 Class 对象。
- **类加载过程**：包括加载、验证、准备、解析和初始化等步骤。
- **双亲委派模型**：当一个类加载器接收到类加载请求时，它会把请求委派给父——类加载器去完成，依次递归，直到最顶层的类加载器，如果父——类加载器无法完成加载请求，子类加载器才会尝试自己去加载。

#### [说说类的加载过程？](https://javabetter.cn/sidebar/sanfene/jvm.html#%E8%AF%B4%E8%AF%B4%E7%B1%BB%E7%9A%84%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B)
类装载过程包括三个阶段：载入、链接和初始化。

①、载入：将类的二进制字节码加载到内存中。

②、链接可以细分为三个小的阶段：

- 验证：检查类文件格式是否符合 JVM 规范
- 准备：为类的静态变量分配内存并设置默认值。
- 解析：将符号引用替换为直接引用。

③、初始化：执行静态代码块和静态变量初始化。

在准备阶段，静态变量已经被赋过默认初始值了，在初始化阶段，静态变量将被赋值为代码期望赋的值。比如说 `static int a = 1;`，在准备阶段，`a` 的值为 0，在初始化阶段，`a` 的值为 1。

换句话说，初始化阶段是在执行类的构造方法，也就是 [javap](https://javabetter.cn/jvm/bytecode.html) 中看到的 `<clinit>()`。

#### [载入过程 JVM 会做什么？](https://javabetter.cn/sidebar/sanfene/jvm.html#%E8%BD%BD%E5%85%A5%E8%BF%87%E7%A8%8B-jvm-%E4%BC%9A%E5%81%9A%E4%BB%80%E4%B9%88)

![三分恶面渣逆袭：载入](https://cdn.paicoding.com/tobebetterjavaer/images/sidebar/sanfene/jvm-45.png)

三分恶面渣逆袭：载入

- 1）通过一个类的全限定名来获取定义此类的二进制字节流。
- 2）将这个字节流所代表的静态存储结构转化为方法区的运行时数据结构。
- 3）在内存中生成一个代表这个类的 `java.lang.Class` 对象，作为这个类的访问入口。

![[Pasted image 20260512154811.png]]
双亲委派模型要求类加载器在加载类时，先委托父加载器尝试加载，只有父加载器无法加载时，子加载器才会加载。
### [49.为什么要用双亲委派模型？](https://javabetter.cn/sidebar/sanfene/jvm.html#_49-%E4%B8%BA%E4%BB%80%E4%B9%88%E8%A6%81%E7%94%A8%E5%8F%8C%E4%BA%B2%E5%A7%94%E6%B4%BE%E6%A8%A1%E5%9E%8B)

**①、避免类的重复加载**：父加载器加载的类，子加载器无需重复加载。

**②、保证核心类库的安全性**：如 `java.lang.*` 只能由 Bootstrap ClassLoader 加载，防止被篡改。
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

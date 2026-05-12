# 多线程

### 进程、线程、协程

**一句话定义**：**进程**是资源分配的基本单位，**线程**是 CPU 调度的基本单位，**协程**是由程序自己调度的更轻量执行单元。

进程之间默认相互隔离，一个进程崩了通常不会直接影响另一个进程；线程属于进程内部，多个线程共享同一份堆内存和进程资源，所以通信方便但也更容易出现线程安全问题。协程通常运行在线程之上，不直接由操作系统调度，切换成本更低，适合大量 IO 等待场景，但 Java 传统并发面试里主要还是围绕线程展开。

| 概念 | 调度者 | 资源隔离 | 切换成本 | 常见用途 |
|---|---|---|---|---|
| 进程 | 操作系统 | 强，进程间默认隔离 | 高 | 独立应用、服务隔离 |
| 线程 | 操作系统 | 弱，共享进程资源 | 中 | 并发执行任务 |
| 协程 | 程序/运行时 | 取决于实现 | 低 | 高并发 IO、异步任务 |

**为什么需要它**：单线程一次只能做一件事，遇到 IO 等待时 CPU 会被浪费；多线程可以把任务拆开，让 CPU、网络、磁盘等资源更充分地并行工作。

**什么时候用**：CPU 密集型任务一般控制线程数接近 CPU 核心数；IO 密集型任务可以适当增加线程数，或者使用异步/协程模型减少线程切换成本。

---

### 进程/线程之间的通信

**一句话定义**：**通信**就是多个执行单元之间交换数据、传递信号或协调执行顺序。

进程之间默认内存隔离，所以通信一般要借助操作系统提供的机制，比如管道、消息队列、共享内存、Socket 等。线程之间共享同一进程的堆内存，所以可以直接通过共享变量通信，但共享变量会带来可见性、原子性和有序性问题，通常要配合 `synchronized`、`volatile`、`Lock`、阻塞队列等同步手段。

| 场景 | 常见通信方式 | 特点 |
|---|---|---|
| 进程间通信 | 管道、消息队列、Socket、共享内存 | 更安全，但成本更高 |
| 线程间通信 | 共享变量、`wait/notify`、`Lock/Condition`、阻塞队列 | 更方便，但要处理线程安全 |
| 任务结果传递 | `Future`、`CompletableFuture` | 适合异步任务拿结果 |
| 线程协作 | `CountDownLatch`、`Semaphore`、`CyclicBarrier` | 适合控制执行顺序或并发数量 |

**为什么需要它**：并发任务很少是完全独立的，常见场景是一个线程生产数据，另一个线程消费数据，或者主线程等待多个子任务完成。

**什么时候用**：简单状态标记可以用 `volatile`；生产者消费者模型优先用 `BlockingQueue`；复杂条件等待可以用 `Condition`；跨机器或跨进程通信通常用 Socket、HTTP、RPC 或消息队列。

---

### 线程创建方式

**一句话定义**：**线程创建**就是把一段任务包装成 `Thread` 能执行的形式，并交给 JVM 和操作系统调度。

Java 常见创建方式有四种：继承 `Thread`、实现 `Runnable`、实现 `Callable` 配合 `FutureTask`、通过线程池提交任务。前三种更像是“创建一个任务或线程”的语法形式，线程池才是实际开发中更推荐的方式，因为它能复用线程、限制线程数量，并统一管理任务队列和拒绝策略。

| 方式 | 是否有返回值 | 是否能抛受检异常 | 是否推荐 |
|---|---|---|---|
| 继承 `Thread` | 否 | 否 | 不太推荐，耦合线程和任务 |
| 实现 `Runnable` | 否 | 否 | 可用于简单任务 |
| `Callable` + `FutureTask` | 是 | 是 | 适合需要结果的任务 |
| `ExecutorService` 线程池 | 可有 | 可有 | 生产环境更推荐 |

```java
ExecutorService pool = Executors.newFixedThreadPool(4);
Future<Integer> future = pool.submit(() -> 1 + 1);
System.out.println(future.get());
pool.shutdown();
```

**为什么需要它**：并发程序需要把不同任务拆给不同线程执行，但直接频繁 `new Thread()` 成本高，也容易创建过多线程拖垮系统。

**什么时候用**：学习或临时测试可以直接创建 `Thread`；实际项目中优先使用线程池，并且通常建议手动创建 `ThreadPoolExecutor`，不要无脑使用 `Executors` 的快捷方法。

---

### 线程调度方法及区别

---

### 线程状态

---

### 守护线程

---

# Java 内存模型

### Java 内存模型

---

### `i++` 是原子操作吗

---

### 指令重排

---

### happens-before

---

### `volatile` 关键字

---

### `volatile` 加在引用数据类型和基本数据类型上的区别

---

### `synchronized` 关键字、monitor 和可重入

---

### 锁升级

---

### `synchronized` 和 `ReentrantLock` 的区别

---

### `ReentrantLock` 的实现

---

### AQS

---

### CAS、CAS 问题与悲观锁

---

### Java 保证原子性的方法

---

### 原子操作类

---

# 线程安全与死锁

### 怎么保证线程安全

---

### 线程死锁的条件以及破坏条件

---

### 死锁怎么排查

---

# 并发容器与工具类

### `Condition`、`ReentrantLock`、`Exchanger`

---

### `sleep` 和 `wait` 的区别

---

### `Hashtable` 底层

---

### `ThreadLocal` 原理、继承与问题

---

### 强引用、软引用、弱引用、虚引用

---

### CountDownLatch

---

### Semaphore、Exchanger、CountDownLatch、CyclicBarrier、Phaser

参考：[Semaphore、Exchanger、CountDownLatch、CyclicBarrier、Phaser](https://javabetter.cn/thread/CountDownLatch.html)

---

### ConcurrentHashMap 的底层实现（JDK 7 / JDK 8）

对于读操作，ConcurrentHashMap 使用了 `volatile` 变量来保证内存可见性。

对于写操作，ConcurrentHashMap 优先使用 CAS 尝试插入，如果成功就直接返回；否则使用 `synchronized` 代码块进行加锁处理。

参考：[为什么 ConcurrentHashMap 比 Hashtable 效率高（补充）](https://javabetter.cn/sidebar/sanfene/javathread.html#_50-%E4%B8%BA%E4%BB%80%E4%B9%88-concurrenthashmap-%E6%AF%94-hashtable-%E6%95%88%E7%8E%87%E9%AB%98-%E8%A1%A5%E5%85%85)

---

### CopyOnWriteArrayList 的实现原理

内部使用 `volatile` 变量来修饰数组 `array`，以确保读操作的内存可见性。

```java
private transient volatile Object[] array;
```

写操作的时候使用 `ReentrantLock` 来保证线程安全。写操作的时候会复制一个新数组，如果数组很大，写操作的性能会受到影响。

---

# 线程池

### 线程池工作流程、参数、拒绝策略

---

### 线程池阻塞队列

---

### 线程池的线程数应该怎么配置

参考：[线程池的线程数应该怎么配置？](https://javabetter.cn/sidebar/sanfene/javathread.html#_61-%E7%BA%BF%E7%A8%8B%E6%B1%A0%E7%9A%84%E7%BA%BF%E7%A8%8B%E6%95%B0%E5%BA%94%E8%AF%A5%E6%80%8E%E4%B9%88%E9%85%8D%E7%BD%AE)

---

### 常见的线程池

---

### 线程池状态

---

### 线程池调优

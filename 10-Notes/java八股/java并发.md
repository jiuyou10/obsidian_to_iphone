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

---

### 线程创建方式

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

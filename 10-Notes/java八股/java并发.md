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

| 场景     | 常见通信方式                                       | 特点            |
| ------ | -------------------------------------------- | ------------- |
| 进程间通信  | 管道、消息队列、Socket、共享内存                          | 更安全，但成本更高     |
| 线程间通信  | 共享变量、`wait/notify`、`Lock/Condition`、阻塞队列     | 更方便，但要处理线程安全  |
| 任务结果传递 | `Future`、`CompletableFuture`                 | 适合异步任务拿结果     |
| 线程协作   | `CountDownLatch`、`Semaphore`、`CyclicBarrier` | 适合控制执行顺序或并发数量 |

补充：`Future` 可以理解成“异步任务的结果占位符”，任务提交后先返回一个 `Future`，之后通过 `get()` 阻塞等待结果；`CompletableFuture` 更像是增强版 `Future`，支持链式回调、组合多个异步任务，适合把“拿到结果后继续做什么”也写进异步流程里。

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

简单例子：

```java
// 1. 继承 Thread：把任务写进 run 方法
class MyThread extends Thread {
    @Override
    public void run() {
        int result = 1 + 1;
    }
}
new MyThread().start();

// 2. 实现 Runnable：只有任务，没有返回值
Runnable runnable = new Runnable() {
    @Override
    public void run() {
        int result = 2 + 2;
    }
};
//注意这里不要直接写runnable.run();这只是普通方法调用，不会创建新的线程去执行runnable
new Thread(runnable).start();

// 3. Callable + FutureTask：任务有返回值
Callable<Integer> callable = new Callable<Integer>() {
    @Override
    public Integer call() {
        return 3 + 3;
    }
};
FutureTask<Integer> futureTask = new FutureTask<>(callable);
new Thread(futureTask).start();
Integer result1 = futureTask.get();

// 4. 线程池：把任务交给线程池执行
ExecutorService pool = Executors.newFixedThreadPool(4);
Future<Integer> future = pool.submit(new Callable<Integer>() {
    @Override
    public Integer call() {
        return 4 + 4;
    }
});
Integer result2 = future.get();
pool.shutdown();

// 5. CompletableFuture：异步任务完成后继续处理结果
CompletableFuture<Integer> cf = CompletableFuture
        .supplyAsync(() -> 5 + 5)
        .thenApply(x -> x * 10);
Integer result3 = cf.get();
```

补充：`() ->` 是 Lambda 简写，比如 `() -> 5 + 5` 等价于一个没有参数、返回 `5 + 5` 的 `Callable` 或 `Supplier`。如果刚开始看不习惯，可以先按上面 `new Callable<>() { ... }` 的完整写法理解。

**为什么需要它**：并发程序需要把不同任务拆给不同线程执行，但直接频繁 `new Thread()` 成本高，也容易创建过多线程拖垮系统。

**什么时候用**：学习或临时测试可以直接创建 `Thread`；实际项目中优先使用线程池，并且通常建议手动创建 `ThreadPoolExecutor`，不要无脑使用 `Executors` 的快捷方法。

---

### 线程调度方法及区别

**一句话定义**：**线程调度方法**是用来控制线程等待、让出 CPU、唤醒或等待其他线程结束的一组方法。

常见方法有 `sleep`、`wait`、`yield`、`join`、`notify/notifyAll`。其中最容易混的是 `sleep` 和 `wait`：`sleep` 是让当前线程暂停一段时间，不释放已经持有的锁；`wait` 是让当前线程进入对象等待队列，并释放当前对象的 monitor 锁。

| 方法 | 所属 | 是否释放锁 | 作用 |
|---|---|---|---|
| `sleep` | `Thread` | 否 | 当前线程休眠一段时间 |
| `wait` | `Object` | 是 | 等待其他线程唤醒 |
| `yield` | `Thread` | 否 | 提示调度器让出 CPU，不保证生效 |
| `join` | `Thread` | 内部基于等待 | 等待另一个线程执行结束 |
| `notify/notifyAll` | `Object` | 不立即释放，退出同步块才释放 | 唤醒等待队列中的线程 |

**为什么需要它**：线程之间经常需要控制执行顺序，比如主线程等子线程结束，消费者等生产者放入数据。

**什么时候用**：等待条件变化用 `wait/notify` 或 `Condition`；等待任务完成用 `join`、`Future.get()` 或 `CountDownLatch`；不要用 `sleep` 硬凑线程同步。

---

### 线程状态

**一句话定义**：**线程状态**描述一个线程从创建到结束的生命周期位置。

Java 里 `Thread.State` 包括 `NEW`、`RUNNABLE`、`BLOCKED`、`WAITING`、`TIMED_WAITING`、`TERMINATED`。要注意，Java 的 `RUNNABLE` 同时包含操作系统层面的“就绪”和“运行中”，所以看到 `RUNNABLE` 不代表一定正在占用 CPU。

| 状态 | 含义 | 常见来源 |
|---|---|---|
| `NEW` | 创建后未启动 | `new Thread()` 后还没 `start()` |
| `RUNNABLE` | 可运行或正在运行 | 正常执行、等待 CPU |
| `BLOCKED` | 等待进入同步代码块 | 竞争 `synchronized` 锁 |
| `WAITING` | 无限期等待 | `wait()`、`join()`、`park()` |
| `TIMED_WAITING` | 带时间的等待 | `sleep()`、`wait(timeout)` |
| `TERMINATED` | 执行结束 | `run()` 结束或异常退出 |

**为什么需要它**：排查线上卡死、死锁、线程池打满时，线程状态是判断问题位置的第一手信息。

**什么时候用**：看 `jstack`、Arthas `thread`、IDE 线程面板时，重点区分 `BLOCKED`、`WAITING` 和高 CPU 的 `RUNNABLE`。

---

### 守护线程

**一句话定义**：**守护线程**是为用户线程提供后台服务的线程，JVM 不会为了它单独存活。

普通线程也叫用户线程，只要还有用户线程存在，JVM 就不会退出；当 JVM 中只剩守护线程时，JVM 会直接结束。守护线程适合做后台辅助工作，但不适合承担必须完成的数据写入、事务提交、文件关闭等关键逻辑。

```java
Thread t = new Thread(() -> System.out.println("daemon"));
t.setDaemon(true);
t.start();
```

**为什么需要它**：有些后台任务只是辅助性质，比如监控、清理、GC，不应该阻止程序退出。

**什么时候用**：后台心跳、缓存清理、监控线程可以考虑守护线程；涉及数据一致性的任务不要依赖守护线程收尾。

---

# Java 内存模型

### Java 内存模型

**一句话定义**：**Java 内存模型**，也就是 JMM，是 Java 对多线程读写共享变量时可见性、有序性和原子性的规范。

JMM 不是堆、栈、方法区那套运行时内存结构，而是规定线程如何从主内存读取变量、如何把修改写回主内存，以及什么情况下一个线程的写入对另一个线程可见。理解 JMM 的核心，是理解 `happens-before`、`volatile`、锁和指令重排。

| 问题 | 含义 | 常见保证方式 |
|---|---|---|
| 原子性 | 操作不可被中途打断 | 锁、CAS、原子类 |
| 可见性 | 一个线程修改后，其他线程能看到 | `volatile`、锁、线程启动/结束规则 |
| 有序性 | 执行顺序满足并发语义 | `volatile`、锁、`happens-before` |

**为什么需要它**：CPU 缓存、编译器优化和指令重排会让多线程执行结果和代码顺序看起来不一致。

**什么时候用**：分析 `volatile`、双重检查锁、线程安全、锁释放和获取之间的数据可见性时，都要回到 JMM。

---

### `i++` 是原子操作吗

**一句话定义**：`i++` 不是原子操作，它至少包含读取、加一、写回三个步骤。

多线程同时执行 `i++` 时，两个线程可能读到同一个旧值，然后各自加一并写回，最后结果只增加了一次，这就是丢失更新。即使 `i` 被 `volatile` 修饰，也只能保证可见性，不能让复合操作变成原子操作。

```java
// 非线程安全
count++;

// 线程安全
AtomicInteger count = new AtomicInteger();
count.incrementAndGet();
```

**为什么需要它**：很多并发 bug 都来自“看起来是一行代码，其实底层是多个步骤”。

**什么时候用**：低并发计数可用 `AtomicInteger`；高并发热点计数更适合 `LongAdder`；复合业务逻辑需要加锁。

---

### 指令重排

**一句话定义**：**指令重排**是编译器或 CPU 在不改变单线程结果的前提下调整指令执行顺序。

单线程里重排通常不可感知，但多线程下如果没有同步约束，另一个线程可能观察到“半初始化”或乱序状态。经典例子是双重检查锁单例：对象引用可能先赋值，再完成初始化，其他线程看到引用非空后拿到的却是不完整对象。

```java
private static volatile Singleton instance;
```

**为什么需要它**：重排是性能优化手段，但并发下会破坏我们对代码顺序的直觉。

**什么时候用**：共享变量跨线程读写时，用 `volatile`、锁或并发工具建立有序性约束。

---

### happens-before

**一句话定义**：**happens-before** 是 JMM 判断“前一个操作的结果是否对后一个操作可见”的规则。

它不是简单的时间先后，而是内存语义上的先后。常见规则包括：程序顺序规则、监视器锁规则、`volatile` 规则、线程启动规则、线程终止规则、传递性规则。比如一个线程释放锁，happens-before 另一个线程随后获取同一把锁。

| 规则 | 含义 |
|---|---|
| 程序顺序规则 | 同一线程内，前面的操作 happens-before 后面的操作 |
| 锁规则 | 解锁 happens-before 后续对同一锁的加锁 |
| `volatile` 规则 | 写 `volatile` happens-before 后续读同一变量 |
| 线程启动规则 | `start()` happens-before 新线程中的操作 |
| 线程终止规则 | 线程内操作 happens-before 其他线程检测到它结束 |

**为什么需要它**：它是判断并发代码是否安全的标准语言。

**什么时候用**：当你问“线程 A 写的数据，线程 B 是否一定能看到”时，就看两者之间有没有 happens-before 关系。

---

### `volatile` 关键字

**一句话定义**：`volatile` 用来保证变量的**可见性**和一定程度的**有序性**，但不保证复合操作的原子性。

写 `volatile` 变量会把修改刷新到主内存，读 `volatile` 变量会从主内存读取最新值；同时它会通过内存屏障限制相关指令重排。它适合“一个线程写，多个线程读”的状态标记，不适合 `count++` 这种读改写复合操作。

```java
private volatile boolean running = true;

while (running) {
    // do work
}
```

**为什么需要它**：没有可见性保证时，一个线程改了变量，另一个线程可能一直读到旧值。

**什么时候用**：开关标记、状态发布、双重检查锁中的实例引用可以用 `volatile`；需要互斥修改时用锁或原子类。

---

### `volatile` 加在引用数据类型和基本数据类型上的区别

**一句话定义**：`volatile` 修饰基本类型时保证这个变量值可见，修饰引用类型时保证“引用地址”可见，不保证对象内部字段都线程安全。

例如 `volatile User user` 能保证一个线程把 `user` 指向新对象后，其他线程能看到这个新引用；但如果多个线程同时修改 `user.name`、`user.age`，这些字段本身并不会因为 `user` 是 `volatile` 就自动安全。

| 修饰对象 | 保证什么 | 不保证什么 |
|---|---|---|
| 基本类型 | 变量值的可见性 | `i++` 这类复合操作原子性 |
| 引用类型 | 引用指向的可见性 | 对象内部字段的线程安全 |

**为什么需要它**：很多人误以为 `volatile` 引用能让整个对象都线程安全。

**什么时候用**：引用整体替换可以用 `volatile`；对象内部多个字段要保持一致时，应该用锁、不可变对象或线程安全结构。

---

### `synchronized` 关键字、monitor 和可重入

**一句话定义**：`synchronized` 是 Java 内置锁，通过对象的 **monitor** 实现互斥，并且是可重入锁。

每个对象都可以关联一个 monitor，线程进入 `synchronized` 代码块时要先获取这个 monitor，退出时释放。可重入指同一个线程已经拿到锁后，可以再次进入同一把锁保护的代码，不会把自己阻塞住。

```java
synchronized (this) {
    // 临界区
}
```

**为什么需要它**：多个线程同时修改共享状态时，需要互斥来保证原子性，同时锁释放和获取还能建立可见性。

**什么时候用**：临界区简单、锁竞争不复杂时用 `synchronized` 足够；需要可中断、超时、公平锁等能力时考虑 `ReentrantLock`。

---

### 锁升级

**一句话定义**：**锁升级**是 JVM 为了降低 `synchronized` 成本，根据竞争程度把锁从轻到重逐步调整的过程。

传统理解中，锁状态大致经历无锁、偏向锁、轻量级锁、重量级锁。偏向锁适合总是同一个线程进入同步块；轻量级锁适合短时间少量竞争；重量级锁会让线程阻塞和唤醒，成本更高。注意偏向锁在较新 JDK 中已经被废弃/移除趋势，面试时说清楚版本差异更稳妥。

| 锁状态 | 适合场景 | 成本 |
|---|---|---|
| 无锁 | 没有同步需求 | 最低 |
| 偏向锁 | 基本只有一个线程访问 | 低 |
| 轻量级锁 | 少量竞争，持锁时间短 | 中 |
| 重量级锁 | 竞争激烈 | 高 |

**为什么需要它**：如果所有 `synchronized` 一开始都是重量级锁，性能会很差。

**什么时候用**：面试解释 `synchronized` 性能优化时使用；实际编码不要依赖具体锁升级细节来写业务逻辑。

---

### `synchronized` 和 `ReentrantLock` 的区别

**一句话定义**：`synchronized` 是 JVM 内置锁，`ReentrantLock` 是 JUC 提供的显式可重入锁。

二者都能保证互斥和可见性，但 `ReentrantLock` 功能更丰富，比如支持公平锁、可中断获取锁、超时尝试获取锁、多个 `Condition` 条件队列。`synchronized` 写法更简单，退出代码块自动释放锁，不容易忘记释放。

| 对比 | `synchronized` | `ReentrantLock` |
|---|---|---|
| 实现层面 | JVM 内置 | Java 代码，基于 AQS |
| 释放方式 | 自动释放 | 必须 `finally unlock()` |
| 公平锁 | 不支持手动设置 | 支持 |
| 可中断/超时获取 | 不灵活 | 支持 |
| 条件队列 | 一个对象等待队列 | 可创建多个 `Condition` |

**为什么需要它**：不同并发场景对锁的能力要求不一样。

**什么时候用**：普通同步优先 `synchronized`；需要复杂等待条件、公平性或可中断锁时用 `ReentrantLock`。

---

### `ReentrantLock` 的实现

**一句话定义**：`ReentrantLock` 底层主要基于 **AQS**，用 `state` 表示锁状态，用队列管理等待线程。

非公平锁获取锁时会先 CAS 抢占 `state`，失败后再进入 AQS 队列；公平锁会先检查队列前面是否已有等待线程，尽量按排队顺序获取锁。可重入通过记录当前持锁线程和重入次数实现，同一个线程重复加锁时增加 `state`，释放时逐步减少。

```java
lock.lock();
try {
    // 临界区
} finally {
    lock.unlock();
}
```

**为什么需要它**：相比内置锁，它提供更强的锁控制能力。

**什么时候用**：需要 `tryLock()`、`lockInterruptibly()`、公平锁或多个 `Condition` 时使用。

---

### AQS

**一句话定义**：**AQS** 是 JUC 中很多同步器的基础框架，用一个 `state` 状态值和一个 FIFO 等待队列来管理线程同步。

AQS 的核心思路是：线程先尝试通过 CAS 修改 `state` 获取同步状态；失败则封装成节点进入等待队列，并在合适时被唤醒。`ReentrantLock`、`Semaphore`、`CountDownLatch`、`ReentrantReadWriteLock` 都和 AQS 有关，只是它们对 `state` 的含义定义不同。

| 工具 | `state` 大致含义 |
|---|---|
| `ReentrantLock` | 锁重入次数 |
| `Semaphore` | 剩余许可证数量 |
| `CountDownLatch` | 还需要倒数的次数 |
| `ReentrantReadWriteLock` | 读锁/写锁状态 |

**为什么需要它**：如果每个同步器都自己实现排队、阻塞、唤醒，会重复且容易出错。

**什么时候用**：理解 JUC 工具底层原理时重点掌握；业务代码一般直接用现成同步器，不自己继承 AQS。

---

### CAS、CAS 问题与悲观锁

**一句话定义**：**CAS** 是一种乐观锁思想：先比较内存中的值是否还是旧值，是就更新，不是就失败重试。

CAS 的全称是 Compare And Swap，常用于原子类和并发容器。它不用阻塞线程，性能通常比悲观锁好，但也有问题：ABA 问题、自旋过久浪费 CPU、只能天然保证单个变量的原子更新。悲观锁则假设一定会冲突，所以先加锁再操作。

| 方式 | 思想 | 优点 | 问题 |
|---|---|---|---|
| CAS/乐观锁 | 先操作，失败再重试 | 少阻塞，性能好 | ABA、自旋开销、单变量限制 |
| 悲观锁 | 先加锁，再操作 | 逻辑简单，适合复杂临界区 | 阻塞、上下文切换成本 |

**为什么需要它**：高并发下如果每次都阻塞，吞吐会下降；CAS 能减少阻塞。

**什么时候用**：简单计数、状态更新用 CAS/原子类；多个变量要保持一致时用锁更清晰。

---

### Java 保证原子性的方法

**一句话定义**：**原子性**就是一个操作要么完整执行，要么完全不执行，中间状态不会被其他线程看到。

Java 保证原子性的常见方式有：使用 `synchronized` 或 `Lock` 包住临界区；使用原子类如 `AtomicInteger`；使用 CAS；使用线程封闭避免共享。`volatile` 只能保证可见性，不能保证 `i++` 这种复合操作原子性。

| 方法 | 适合场景 |
|---|---|
| `synchronized` | 简单临界区、复合操作 |
| `ReentrantLock` | 复杂锁控制 |
| 原子类 | 单变量原子更新 |
| `LongAdder` | 高并发计数 |
| 线程封闭 | 每个线程独享变量 |

**为什么需要它**：没有原子性，多个线程交错执行会导致数据丢失或状态错乱。

**什么时候用**：能不共享就不共享；单变量用原子类，复杂业务状态用锁。

---

### 原子操作类

**一句话定义**：**原子操作类**是 `java.util.concurrent.atomic` 包里基于 CAS 提供线程安全更新能力的一组类。

常见类有 `AtomicInteger`、`AtomicLong`、`AtomicBoolean`、`AtomicReference`、`AtomicStampedReference`、`LongAdder`。`AtomicInteger` 适合普通计数，`LongAdder` 在高并发下通过分段累加降低竞争，`AtomicStampedReference` 可以解决一部分 ABA 问题。

```java
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet();
```

**为什么需要它**：很多场景只需要安全地更新一个变量，直接加锁显得太重。

**什么时候用**：计数器、状态标记、引用替换可以用原子类；涉及多个变量一致性时不要硬凑原子类，应该用锁或事务。

---

# 线程安全与死锁

### 怎么保证线程安全

**一句话定义**：**线程安全**是指多个线程同时访问共享数据时，程序结果仍然正确。

保证线程安全可以从三个方向入手：不共享、不可变、正确同步。不共享就是线程封闭，例如局部变量和 `ThreadLocal`；不可变就是对象创建后状态不变；正确同步包括锁、`volatile`、原子类、并发容器和 JUC 工具。

| 问题 | 解决方法 |
|---|---|
| 原子性 | 锁、CAS、原子类 |
| 可见性 | `volatile`、锁、并发容器 |
| 有序性 | `volatile`、锁、happens-before |
| 共享可变状态 | 不可变对象、线程封闭、减少共享 |

**为什么需要它**：多线程读写共享变量时，可能出现丢失更新、脏读、状态不一致。

**什么时候用**：先判断有没有共享可变状态；如果有，再选择锁、原子类、并发容器或不可变设计。

---

### 线程死锁的条件以及破坏条件

**一句话定义**：**死锁**是多个线程互相等待对方持有的资源，导致谁也无法继续执行。

死锁有四个必要条件：互斥、占有且等待、不可抢占、循环等待。只要破坏其中任意一个条件，就可以避免死锁。比如一次性申请所有资源可以破坏“占有且等待”，按固定顺序加锁可以破坏“循环等待”。

| 死锁条件 | 含义 | 破坏方式 |
|---|---|---|
| 互斥 | 资源一次只能被一个线程持有 | 尽量使用无锁或共享资源 |
| 占有且等待 | 拿着一个资源等待另一个 | 一次性申请资源 |
| 不可抢占 | 资源不能被强制释放 | 使用超时锁、可中断锁 |
| 循环等待 | 形成等待环 | 固定加锁顺序 |

**为什么需要它**：死锁会让线程永久卡住，接口无响应但 CPU 不一定高。

**什么时候用**：涉及多把锁、多个资源转账、库存扣减等场景，要提前设计加锁顺序和超时策略。

---

### 死锁怎么排查

**一句话定义**：**死锁排查**就是找出哪些线程互相持有锁、互相等待锁。

常见方式是用 `jstack`、Arthas、JConsole、VisualVM 查看线程 dump。线程 dump 中如果出现 `Found one Java-level deadlock`，通常会直接列出参与死锁的线程和锁对象。没有明确提示时，也可以看大量线程是否停在 `BLOCKED`，以及它们等待的 monitor 是谁持有的。

```bash
jps
jstack <pid>
```

**为什么需要它**：死锁发生后业务可能完全卡住，必须快速定位是哪几把锁和哪几段代码造成的。

**什么时候用**：线上接口一直无响应、线程池任务不推进、CPU 不高但服务卡死时，优先抓线程 dump。

---

# 并发容器与工具类

### `Condition`、`ReentrantLock`、`Exchanger`

**一句话定义**：`ReentrantLock` 是显式可重入锁，`Condition` 是它的条件队列，`Exchanger` 用于两个线程之间交换数据。

`Condition` 类似 `wait/notify`，但一个 `ReentrantLock` 可以创建多个条件队列，所以能把“队列不空”和“队列不满”分开等待。`Exchanger` 则要求两个线程在交换点相遇，双方都到达后交换各自携带的数据。

```java
Lock lock = new ReentrantLock();
Condition notEmpty = lock.newCondition();
```

**为什么需要它**：内置锁只有一个等待队列，复杂线程协作时表达能力有限。

**什么时候用**：生产者消费者的复杂等待条件用 `Condition`；两个线程配对交换数据时用 `Exchanger`。

---

### `sleep` 和 `wait` 的区别

**一句话定义**：`sleep` 是线程休眠方法，`wait` 是对象等待队列方法，核心区别是 `wait` 会释放锁而 `sleep` 不会。

`Thread.sleep()` 不要求当前线程持有锁，只是让当前线程进入限时等待；`obj.wait()` 必须在 `synchronized(obj)` 内调用，因为它要释放并重新竞争这个对象的 monitor。`wait` 通常要放在 `while` 循环里，防止虚假唤醒或条件变化。

| 对比 | `sleep` | `wait` |
|---|---|---|
| 所属类 | `Thread` | `Object` |
| 是否释放锁 | 否 | 是 |
| 是否必须持有锁 | 否 | 是 |
| 唤醒方式 | 时间到或中断 | `notify/notifyAll`、中断、超时 |

**为什么需要它**：二者都会让线程暂停，但语义完全不同，混用容易导致锁迟迟不释放。

**什么时候用**：定时暂停用 `sleep`；等待共享条件变化用 `wait/notify` 或更推荐的并发工具。

---

### `Hashtable` 底层

**一句话定义**：`Hashtable` 是早期线程安全哈希表，底层是数组加链表，并通过方法级 `synchronized` 保证线程安全。

它的 key 和 value 都不允许为 `null`。因为很多操作直接锁整张表，所以并发性能较差；相比之下，`ConcurrentHashMap` 通过更细粒度的并发控制提升了吞吐。

| 对比 | `Hashtable` | `ConcurrentHashMap` |
|---|---|---|
| 锁粒度 | 整张表/方法级 | 更细粒度，JDK 8 主要是 CAS + 桶级锁 |
| 并发性能 | 低 | 高 |
| 是否允许 `null` | 不允许 | 不允许 |
| 新代码推荐 | 不推荐 | 推荐 |

**为什么需要它**：它解决了早期 `HashMap` 多线程不安全的问题。

**什么时候用**：现在基本不用它，新代码优先选择 `ConcurrentHashMap`。

---

### `ThreadLocal` 原理、继承与问题

**一句话定义**：`ThreadLocal` 是线程隔离变量，同一个 `ThreadLocal` 在不同线程中保存不同副本。

值实际存在线程对象的 `ThreadLocalMap` 中，key 是 `ThreadLocal` 的弱引用，value 是业务对象。`ThreadLocalMap` 不是 `HashMap`，它是 `ThreadLocal` 自己实现的开放寻址结构。普通 `ThreadLocal` 不能被子线程继承；如果要继承父线程值，可以用 `InheritableThreadLocal`，但在线程池里要特别小心线程复用导致的脏数据。

```java
LOCAL.set(userId);
try {
    // 使用上下文
} finally {
    LOCAL.remove();
}
```

**为什么需要它**：有些上下文只属于当前线程，比如用户 ID、traceId、事务上下文。

**什么时候用**：保存线程上下文时使用；在线程池中用完必须 `remove()`，否则可能内存泄漏或串数据。

---

### 强引用、软引用、弱引用、虚引用

**一句话定义**：Java 引用强度从高到低大致是**强引用**、**软引用**、**弱引用**、**虚引用**。

强引用只要还可达就不会被回收；软引用在内存不足时可能被回收，常被提到用于缓存；弱引用只要发生 GC 就可能被回收，`ThreadLocalMap` 的 key 就是弱引用；虚引用不能通过 `get()` 拿到对象，主要用于接收对象回收通知。

| 类型 | 回收特点 | 常见用途 |
|---|---|---|
| 强引用 | 可达就不回收 | 普通对象引用 |
| 软引用 | 内存不足时回收 | 缓存场景 |
| 弱引用 | GC 时容易回收 | 避免 key 阻止回收 |
| 虚引用 | 不影响生命周期 | 回收通知、堆外内存清理 |

**为什么需要它**：不同引用强度能让对象生命周期更灵活。

**什么时候用**：普通业务基本都是强引用；缓存优先用成熟缓存框架；理解 `ThreadLocal` 泄漏时要知道弱引用。

---

### CountDownLatch

**一句话定义**：`CountDownLatch` 是一个倒计时门闩，用来让一个或多个线程等待其他线程完成。

它内部基于 AQS，初始化时设置计数，每调用一次 `countDown()` 计数减一，调用 `await()` 的线程会等待计数归零。它是一次性的，计数归零后不能重置。

```java
CountDownLatch latch = new CountDownLatch(3);
latch.countDown();
latch.await();
```

**为什么需要它**：主线程经常需要等待多个子任务都完成后再继续。

**什么时候用**：多任务并行加载、压测同时起跑、服务启动等待多个组件初始化时使用。

---

### Semaphore、Exchanger、CountDownLatch、CyclicBarrier、Phaser

**一句话定义**：这些都是 JUC 提供的线程协作工具，用来控制并发数量、交换数据或协调多个线程的阶段推进。

`Semaphore` 用许可证控制并发数；`Exchanger` 让两个线程交换数据；`CountDownLatch` 让线程等待倒计时归零；`CyclicBarrier` 让一组线程互相等待到齐后继续，并且可重复使用；`Phaser` 更灵活，支持多阶段和动态注册参与者。

| 工具 | 作用 | 是否可复用 |
|---|---|---|
| `Semaphore` | 控制同时访问资源的线程数 | 是 |
| `Exchanger` | 两个线程交换数据 | 是 |
| `CountDownLatch` | 等待计数归零 | 否 |
| `CyclicBarrier` | 一组线程到齐再继续 | 是 |
| `Phaser` | 多阶段任务协调 | 是 |

参考：[Semaphore、Exchanger、CountDownLatch、CyclicBarrier、Phaser](https://javabetter.cn/thread/CountDownLatch.html)

**为什么需要它**：线程协作不应该全靠手写 `wait/notify`，工具类更安全、表达更清楚。

**什么时候用**：限流用 `Semaphore`；阶段同步用 `CyclicBarrier` 或 `Phaser`；等待多个任务完成用 `CountDownLatch`。

---

### ConcurrentHashMap 的底层实现（JDK 7 / JDK 8）

**一句话定义**：`ConcurrentHashMap` 是线程安全的哈希表，通过更细粒度的并发控制提高读写性能。

JDK 7 主要是 **Segment 分段锁**，每个 Segment 类似一个小 HashMap，写操作锁住某个段。JDK 8 取消 Segment，结构接近 `HashMap` 的数组 + 链表 + 红黑树；读操作主要依赖 `volatile` 保证可见性，写操作优先 CAS，失败或发生冲突时对桶头使用 `synchronized` 加锁。

| 版本 | 核心结构 | 并发控制 |
|---|---|---|
| JDK 7 | Segment + HashEntry | 分段锁 |
| JDK 8 | Node 数组 + 链表/红黑树 | CAS + `synchronized` 桶级锁 |

对于读操作，ConcurrentHashMap 使用了 `volatile` 变量来保证内存可见性。

对于写操作，ConcurrentHashMap 优先使用 CAS 尝试插入，如果成功就直接返回；否则使用 `synchronized` 代码块进行加锁处理。

参考：[为什么 ConcurrentHashMap 比 Hashtable 效率高（补充）](https://javabetter.cn/sidebar/sanfene/javathread.html#_50-%E4%B8%BA%E4%BB%80%E4%B9%88-concurrenthashmap-%E6%AF%94-hashtable-%E6%95%88%E7%8E%87%E9%AB%98-%E8%A1%A5%E5%85%85)

**为什么需要它**：`HashMap` 线程不安全，`Hashtable` 锁粒度太粗，`ConcurrentHashMap` 在安全和性能之间做了更好的平衡。

**什么时候用**：多线程共享 Map 时优先用它；如果需要复合操作，注意使用 `compute`、`putIfAbsent` 等原子方法。

---

### CopyOnWriteArrayList 的实现原理

**一句话定义**：`CopyOnWriteArrayList` 是写时复制的线程安全 List，读不加锁，写时复制新数组。

内部使用 `volatile` 修饰数组 `array`，保证读线程能看到最新数组引用。写操作会加锁，然后复制一份新数组，在新数组上修改，最后把引用指向新数组。所以它读性能好，写成本高，并且读到的可能是旧快照。

```java
private transient volatile Object[] array;
```

写操作的时候使用 `ReentrantLock` 来保证线程安全。写操作的时候会复制一个新数组，如果数组很大，写操作的性能会受到影响。

**为什么需要它**：读多写少场景下，给每次读都加锁会浪费性能。

**什么时候用**：配置列表、监听器列表这类读多写少场景；写频繁或数据量很大时不要用。

---

# 线程池

### 线程池工作流程、参数、拒绝策略

**一句话定义**：**线程池**是复用线程执行任务的组件，用少量长期存在的线程管理大量短任务。

`ThreadPoolExecutor` 的核心参数包括：核心线程数、最大线程数、空闲线程存活时间、阻塞队列、线程工厂、拒绝策略。任务提交后，线程池大致按“核心线程未满先创建核心线程 → 队列未满先入队 → 队列满且线程数未达最大值则创建非核心线程 → 还处理不了就拒绝”的流程执行。

| 参数 | 作用 |
|---|---|
| `corePoolSize` | 核心线程数 |
| `maximumPoolSize` | 最大线程数 |
| `keepAliveTime` | 非核心线程空闲存活时间 |
| `workQueue` | 存放等待执行的任务 |
| `threadFactory` | 创建线程，方便命名 |
| `handler` | 拒绝策略 |

常见拒绝策略：`AbortPolicy` 抛异常，`CallerRunsPolicy` 让提交任务的线程自己执行，`DiscardPolicy` 直接丢弃，`DiscardOldestPolicy` 丢弃队列最老任务。

**为什么需要它**：频繁创建和销毁线程成本高，线程无限增长会拖垮系统。

**什么时候用**：只要有批量异步任务或并发任务，就应该考虑线程池，并根据业务配置参数。

---

### 线程池阻塞队列

**一句话定义**：**阻塞队列**是线程池中保存等待执行任务的队列，它影响线程池扩容和任务堆积行为。

常见队列有 `ArrayBlockingQueue`、`LinkedBlockingQueue`、`SynchronousQueue`、`PriorityBlockingQueue`、`DelayQueue`。有界队列能限制任务堆积，避免 OOM；无界队列可能让最大线程数失去意义，因为任务一直入队，线程数不容易扩到最大。

| 队列 | 特点 | 常见场景 |
|---|---|---|
| `ArrayBlockingQueue` | 有界数组队列 | 固定容量任务缓冲 |
| `LinkedBlockingQueue` | 链表队列，可近似无界 | 固定线程池常见 |
| `SynchronousQueue` | 不存任务，直接移交 | 缓存线程池 |
| `PriorityBlockingQueue` | 支持优先级 | 优先级任务 |
| `DelayQueue` | 延迟到期后才能取 | 延迟任务 |

**为什么需要它**：任务生产速度可能大于消费速度，队列用于削峰填谷。

**什么时候用**：生产环境优先使用有界队列，并配合监控队列长度和拒绝次数。

---

### 线程池的线程数应该怎么配置

**一句话定义**：线程数配置要看任务是 CPU 密集型还是 IO 密集型，而不是固定背公式。

CPU 密集型任务主要消耗 CPU，线程数通常接近 CPU 核心数，过多线程只会增加上下文切换。IO 密集型任务大量时间在等待网络、磁盘、数据库，线程数可以比核心数多一些。常见估算公式是：线程数 = CPU 核心数 × CPU 利用率 × (1 + 等待时间 / 计算时间)。

| 任务类型 | 配置思路 |
|---|---|
| CPU 密集型 | 接近 CPU 核心数，避免过多切换 |
| IO 密集型 | 可以适当大于核心数 |
| 混合型 | 压测后根据 CPU、响应时间、队列长度调 |

参考：[线程池的线程数应该怎么配置？](https://javabetter.cn/sidebar/sanfene/javathread.html#_61-%E7%BA%BF%E7%A8%8B%E6%B1%A0%E7%9A%84%E7%BA%BF%E7%A8%8B%E6%95%B0%E5%BA%94%E8%AF%A5%E6%80%8E%E4%B9%88%E9%85%8D%E7%BD%AE)

**为什么需要它**：线程太少吞吐上不去，线程太多会导致切换开销、内存压力和下游被打爆。

**什么时候用**：初始值按任务类型估算，最终必须结合压测和线上监控调整。

---

### 常见的线程池

**一句话定义**：Java 通过 `Executors` 提供几种快捷线程池，但生产环境更推荐手动创建 `ThreadPoolExecutor`。

常见线程池包括 `newFixedThreadPool`、`newCachedThreadPool`、`newSingleThreadExecutor`、`newScheduledThreadPool`。它们用起来方便，但有些默认队列可能是无界的，任务堆积时容易 OOM，所以阿里规约等实践通常建议显式指定参数。

| 线程池 | 特点 | 风险 |
|---|---|---|
| `newFixedThreadPool` | 固定线程数 | 无界队列可能堆积 |
| `newCachedThreadPool` | 线程数可快速增长 | 最大线程数过大 |
| `newSingleThreadExecutor` | 单线程顺序执行 | 无界队列堆积 |
| `newScheduledThreadPool` | 定时/周期任务 | 任务异常要处理 |

**为什么需要它**：不同任务对线程数量、队列、调度方式要求不同。

**什么时候用**：学习可以用 `Executors`；项目里建议手动创建线程池，给线程命名，设置有界队列和拒绝策略。

---

### 线程池状态

**一句话定义**：**线程池状态**描述线程池是否接收新任务、是否处理队列任务、是否已经终止。

`ThreadPoolExecutor` 主要有 `RUNNING`、`SHUTDOWN`、`STOP`、`TIDYING`、`TERMINATED` 五种状态。`shutdown()` 会进入 `SHUTDOWN`，不再接收新任务，但会处理队列中已有任务；`shutdownNow()` 会进入 `STOP`，尝试中断正在执行的任务，并返回队列里未执行的任务。

| 状态 | 是否接收新任务 | 是否处理队列任务 |
|---|---|---|
| `RUNNING` | 是 | 是 |
| `SHUTDOWN` | 否 | 是 |
| `STOP` | 否 | 否，并尝试中断执行中任务 |
| `TIDYING` | 否 | 否，准备结束 |
| `TERMINATED` | 否 | 否，已结束 |

**为什么需要它**：优雅关闭线程池时，要知道任务是否还会继续执行。

**什么时候用**：服务停机、应用关闭、任务取消时，优先 `shutdown()`，必要时再 `shutdownNow()`。

---

### 线程池调优

**一句话定义**：**线程池调优**是根据任务类型、系统资源和运行指标调整线程数、队列和拒绝策略。

调优不要只盯线程数，还要看 CPU 使用率、队列长度、任务耗时、拒绝次数、下游响应时间。线程池不是越大越好，过大的线程池可能把数据库、Redis、第三方接口打爆。比较稳的做法是：先设置有界队列和合理拒绝策略，再通过压测观察瓶颈。

| 指标 | 说明 |
|---|---|
| 活跃线程数 | 是否长期接近最大线程数 |
| 队列长度 | 是否持续堆积 |
| 拒绝次数 | 是否已经过载 |
| 任务耗时 | 是否有慢任务拖住线程 |
| 下游耗时 | 是否瓶颈在 DB/Redis/外部接口 |

**为什么需要它**：线程池参数不合理，会造成吞吐低、延迟高、OOM 或雪崩。

**什么时候用**：上线前压测要调；线上出现队列堆积、拒绝任务、响应变慢时也要调。

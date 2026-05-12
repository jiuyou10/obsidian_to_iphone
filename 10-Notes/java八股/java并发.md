<<<<<<< HEAD
多线程
进程线程协程
进程/线程之间的通信
线程创建方式
线程调度方法，以及部分的区别
线程状态

守护 线程
=======



contion ,reentrantlock exchanger
sleep wat 区别
怎么保证线程安全
hashtable底层
threadlocal,以及怎么实现的，以及能够被子线程继承？
以及会出现什么问题，怎么解决？
以及其实现结构是hashmap吗
强软弱虚引用

java内存模型
i++是原子操作吗
指令重排
happensbefore
volatile关键字，synchronized关键字
volatile加在引用数据类型和基本数据类型

synchronized关键字如何实现，以及monitor，以及可重入
锁升级
synchronized和reentrantlock的区别

reentrantlock的实现
AQS
CAS以及问题，悲观锁
java保证原子性的方法
原子操作类这里我不是很清楚
线程死锁的条件以及破坏条件
死锁怎么排查

countdownlatch
[Semaphore、Exchanger、CountDownLatch、CyclicBarrier、Phaser](https://javabetter.cn/thread/CountDownLatch.html)

concurrenthashmap的底层实现（jdk7/8)
对于读操作，ConcurrentHashMap 使用了 volatile 变量来保证内存可见性。

对于写操作，ConcurrentHashMap 优先使用 CAS 尝试插入，如果成功就直接返回；否则使用 synchronized 代码块进行加锁处理
### [为什么 ConcurrentHashMap 比 Hashtable 效率高（补充）](https://javabetter.cn/sidebar/sanfene/javathread.html#_50-%E4%B8%BA%E4%BB%80%E4%B9%88-concurrenthashmap-%E6%AF%94-hashtable-%E6%95%88%E7%8E%87%E9%AB%98-%E8%A1%A5%E5%85%85)
CopyOnWriteArrayList的实现原理
内部使用 volatile 变量来修饰数组 array，以确保读操作的内存可见性。

```
private transient volatile Object[] array;
```

写操作的时候使用 ReentrantLock 来保证线程安全。写操作的时候会复制一个新数组，如果数组很大，写操作的性能会受到影响。



线程池，工作流程，参数，拒绝策略
线程池阻塞队列
### [线程池的线程数应该怎么配置？](https://javabetter.cn/sidebar/sanfene/javathread.html#_61-%E7%BA%BF%E7%A8%8B%E6%B1%A0%E7%9A%84%E7%BA%BF%E7%A8%8B%E6%95%B0%E5%BA%94%E8%AF%A5%E6%80%8E%E4%B9%88%E9%85%8D%E7%BD%AE)


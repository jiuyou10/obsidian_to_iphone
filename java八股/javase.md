# JavaSE

## 1. Java 基础

### JDK、JRE、JVM

**JVM**：也就是 Java 虚拟机，是 Java 实现跨平台的关键所在，不同的操作系统有不同的 JVM 实现。JVM 负责将 Java 字节码转换为特定平台的机器码，并执行。

**JRE**：也就是 Java 运行时环境，包含了运行 Java 程序所必需的库，以及 JVM。

**JDK**：一套完整的 Java SDK，包括 JRE，编译器 javac、Java 文档生成工具 javadoc、Java 字节码工具 javap 等。为开发者提供了开发、编译、调试 Java 程序的一整套环境。

---

### 字节码 & 跨平台

在 Java 中，JVM 可以理解的代码就叫做字节码（即扩展名为 `.class` 的文件），它不面向任何特定的处理器，只面向虚拟机。

解决了传统解释型语言执行效率低的问题，同时又保留了解释型语言可移植的特点。

---

### 编译 vs 解释

**编译型**：会通过编译器将源代码一次性翻译成可被该平台执行的机器码。一般情况下，编译语言的执行速度比较快，开发效率比较低。常见的编译性语言有 C、C++、Go、Rust 等等。

**解释型**：会通过解释器一句一句的将代码解释（interpret）为机器代码后再执行。解释型语言开发效率比较快，执行速度比较慢。常见的解释性语言有 Python、JavaScript、PHP 等等。

Java 程序要经过先编译，后解释两个步骤，由 Java 编写的程序需要先经过编译步骤，生成字节码（`.class` 文件），这种字节码必须由 Java 解释器来解释执行。

---

### 基本数据类型

byte、boolean、char、short、int、float、long、double

移位操作符实际上支持的类型只有 `int` 和 `long`，编译器在对 `short`、`byte`、`char` 类型进行移位前，都会将其转换为 `int` 类型再操作，最大支持 31 位，多余就对 32 取余。

---

### 基本类型和包装类型的区别

- 基本类型用于存储简单数据，而包装类型是对象，可以用于集合和泛型
- 基本类型直接存储值（局部变量，栈），而包装类型存储的是对象（堆）
- 基本类型占用空间更小，效率更高
- 基本类型成员变量有默认值，而包装类型默认值是 null
- 基本类型使用 == 比较值，而包装类型 == 比较地址，一般需要使用 equals 比较值

> **所有整型包装类对象之间值的比较，全部使用 equals 方法比较**

**包装类的缓存机制**：
- Integer 缓存范围 [-128, 127]，可通过 JVM 参数扩大上限
- Byte、Long、Short 范围同样 [-128, 127]，但没有参数控制扩展
- Character 缓存范围 [0, 127]
- 在这个范围内不会创建新对象，而是返回已经存在对象的引用

---

### 自动拆箱装箱

装箱：调用了包装类的 `valueOf()` 方法。
拆箱：调用了 `xxxValue()` 方法（如 `intValue()`）。

```java
Integer a = 1;          // 自动装箱 → Integer.valueOf(1)
Integer b = 2;
Integer c = 3;          // 自动装箱 → Integer.valueOf(3)

Integer d = a + b;      // a 和 b 先自动拆箱为 int，相加后再自动装箱
// 相当于：
int tmp = a.intValue() + b.intValue();
Integer d = Integer.valueOf(tmp);
```

---

### 数据类型转换

一个范围较小的数值或变量赋给另外一个范围较大的变量时，会进行自动类型转换；反之，需要强制转换。

---

### & 和 &&

- `&`：逻辑与，两边表达式都会执行
- `&&`：短路与，左边为 false 时右边不再执行（短路）
- 类似地：`|` 和 `||`

---

### switch

- Java 5 以前：expr 只能是 byte、short、char、int
- Java 5 起：支持 enum 类型
- Java 7 起：支持 String 类型
- Java 21 起：支持 long、任意对象类型、null，可通过 when 子句添加复杂判断条件

```java
switch (obj) {
    case null -> System.out.println("是空的");
    case String s -> System.out.println("是字符串：" + s);
    default -> System.out.println("其他类型");
}
```

---

### BigDecimal

保证数据准确性有两种方案，一种使用 `BigDecimal`，一种将浮点数转换为整数 int 进行计算。

不能使用 `float` 和 `double`，它们无法避免浮点数运算中常见的精度问题，因为这些数据类型采用二进制浮点数来表示，无法准确地表示。

`BigDecimal` 可以实现对浮点数的运算，不会造成精度丢失。通常情况下，大部分需要浮点数精确运算结果的业务场景（比如涉及到钱的场景）都是通过 `BigDecimal` 来做的。

`BigInteger` 内部使用 `int[]` 数组来存储任意大小的整形数据，运算的效率会相对较低。

---

### 访问修饰符

| 修饰符 | 同一类内 | 同一包内 | 子类 | 所有类 |
|--------|:--------:|:--------:|:----:|:------:|
| **private** | ✅ | ❌ | ❌ | ❌ |
| **default**（不写） | ✅ | ✅ | ❌ | ❌ |
| **protected** | ✅ | ✅ | ✅ | ❌ |
| **public** | ✅ | ✅ | ✅ | ✅ |

注意：private 和 protected 不能修饰外部类（只能修饰成员变量和方法）。

---

### 成员变量 vs 局部变量

| | 成员变量 | 局部变量 |
|--|---------|---------|
| 位置 | 类中方法外 | 方法内或参数 |
| 默认值 | 有默认值（保证了对象状态的安全和可预测性） | 无默认值，必须手动赋值 |
| 作用域 | 整个类 | 方法内 |

**为什么成员变量有默认值？**

局部变量只活在一个方法里，编译器能清楚地看到它是否在使用前被赋值，所以编译器会强制你必须手动赋值，否则就报错。

成员变量是跟着对象走的，它的值可能在构造函数里赋，也可能在后面的某个 setter 方法里赋。编译器在编译时无法预测它到底什么时候会被赋。如果一个变量没有被初始化，它的内存里存放的就是"垃圾值"，也就是之前的不相关的值。

---

### static 关键字

可以用来修饰变量、方法、代码块和内部类，以及导入包。

| 修饰对象 | 作用 |
|---------|------|
| **变量** | 静态变量，类级别变量，所有实例共享同一份数据 |
| **方法** | 静态方法，类级别方法，与实例无关 |
| **代码块** | 在类加载时初始化一些数据，只执行一次 |
| **内部类** | 与外部类绑定但独立于外部类实例 |

**静态变量**：只会被分配一次内存，无论一个类创建了多少个对象，它们都共享同一份静态变量。静态变量是通过类名来访问的。

**静态方法 vs 实例方法**：
- 调用方式：静态方法可以用 `类名.方法名` 或 `对象.方法名`，实例方法只能用 `对象.方法名`
- 访问限制：静态方法只允许访问静态成员（变量和方法），不允许访问实例成员
- 原因：静态方法在类加载时就存在，此时非静态成员还不存在

---

### final 关键字

- 修饰 **类**：该类不能被继承（如 String、Integer 等包装类）
- 修饰 **方法**：该方法不能被重写（Override）
- 修饰 **变量**：该变量的值一旦被初始化就不能被修改
  - 基本数据类型：数值不能改
  - 引用类型：引用不能指向另一个对象，但引用指向的对象内容可以改变

**final、finally、finalize 的区别**：
- **final**：关键字，用于修饰类、方法、变量
- **finally**：异常处理的关键字，try 块后保证执行的代码块
- **finalize**：Object 类的方法，GC 回收对象前调用（已废弃）

---

### 值传递

Java 只有值传递。

- 如果参数是基本类型：传递的是基本类型的字面量值的拷贝（创建副本）
- 如果参数是引用类型：传递的是实参所引用的对象在堆中地址值的拷贝（也创建副本）

---

### 深拷贝 vs 浅拷贝 vs 引用拷贝

- **浅拷贝**：在堆上创建一个新对象，但如果原对象内部的属性是引用类型，浅拷贝会直接复制内部对象的引用地址，堆上的拷贝对象和原对象共用同一个内部对象
- **深拷贝**：完全复制整个对象，包括这个对象所包含的内部对象，内部对象完全独立
- **引用拷贝**：两个不同的引用指向同一个对象

---

## 2. 面向对象

### 面向对象编程 vs 面向过程编程

**面向过程编程（POP）**：把解决问题的过程拆分成一个个步骤（方法），通过依次执行这些步骤来解决问题。

**面向对象编程（OOP）**：先抽象出对象，然后让对象调用自己的方法来解决问题。

**相比 POP，OOP 的优点**：
- **易维护**：良好的结构和封装性使程序更容易维护
- **易复用**：通过继承和多态提高代码复用性
- **易扩展**：模块化设计使系统扩展更加容易

---

### 封装（Encapsulation）

封装是指将对象的属性（状态信息）隐藏在对象内部，外部对象不能直接访问这些属性。外部只能通过提供的公共方法（getter / setter）来访问或修改属性。

---

### 继承（Inheritance）

子类拥有父类的所有属性和方法（包括 private），但 private 属性和方法子类无法访问，只是拥有。

**为什么要多组合少继承？**
继承破坏封装性，父类的实现细节暴露给子类；组合则通过持有引用的方式复用功能，更灵活、耦合更低。

---

### 多态（Polymorphism）

多态表示同一个对象具有多种形态。核心：**父类引用指向子类对象**。

```java
Animal a = new Dog();
```

**前置条件**：
1. 子类继承父类
2. 子类重写父类的方法
3. 父类引用指向子类的对象

**方法执行规则**：
- 如果子类重写了父类方法 → 执行子类方法
- 如果子类没有重写父类方法 → 执行父类方法
- 多态不能调用只存在于子类而父类没有的方法

---

### 抽象类和接口

| | 抽象类 | 接口 |
|--|--------|------|
| 实例化 | ❌ 不能直接实例化 | ❌ 不能直接实例化 |
| 抽象方法 | ✅ 可以包含 | ✅ 可以包含 |
| 设计目的 | 代码复用，强调所属关系（is-a） | 行为约束（has-a / 能力） |
| 继承/实现 | 单继承（一个类只能继承一个抽象类） | 多实现（一个类可实现多个接口） |
| 成员变量 | 任何修饰符 | 只能是 `public static final` |
| 构造方法 | ✅ 可以有 | ❌ 不能有 |

普通类不能有抽象方法。

---

### 重载和重写

**重载（Overload）**：发生在同一个类中（或父类和子类之间），方法名相同，参数类型不同、个数不同、顺序不同（至少一个不同），返回值和访问修饰符可以不同。

**重写（Override）**：发生在运行期，子类对父类的允许访问的方法进行重新编写。

重写规则：
- 方法名、参数列表必须相同
- 子类返回值类型应比父类更小或相等（协变返回类型）
- 子类抛出的异常范围小于等于父类
- 子类访问修饰符范围大于等于父类
- 父类方法为 `private/final/static` 时子类不能重写，但 static 方法可以被再次声明

方法的重写要遵循 **"两同两小一大"**。构造方法无法被重写，但可以被重载。

---

## 3. String

### String 对象的创建

```java
String a = "ab";              // 字面量 → 从常量池取，没有则创建
String b = new String("ab");  // new → 堆上新对象，常量池有则复用值
```

- 字面量创建：虚拟机会在常量池中查找有没有已存在的相同值，有就复用，没有就在常量池中创建
- new 创建：总是在堆内存中创建一个新的对象，并用常量池中的值进行初始化

### String 的特点（不可变性）

String 类的对象是**不可变**的，一旦创建，内容不可改变。

#### 如何实现不可变？

```java
public final class String
    implements java.io.Serializable, Comparable<String>, CharSequence {
    private final byte[] value;  // JDK 9+ 用 byte[]（JDK 8 是 char[]）
    private final int coder;     // 编码标识（LATIN1 / UTF16）
    // ...
}
```

- **类声明为 `final`**：防止子类破坏不可变性
- **底层数组 `private final`**：引用不可变 + 私有不暴露，外部无法修改
- **没有提供 setter / 修改方法**：所有看似修改的方法（`concat()`、`replace()`、`substring()`）都返回新 String 对象
- **防御性拷贝**：构造方法不对外来数组做引用共享（JDK 9 之前 `new String(char[])` 会拷贝数组）

> **注意**：通过反射可以暴力修改 `value` 数组的内容（`Field.setAccessible(true)`），但这是运行时破坏约定，不属于语言层面的不可变保障。

#### 为什么设计成不可变？

| 原因 | 说明 |
|---|---|
| **字符串常量池** | 多个引用共享常量池中同一个 String 对象，若可变则一个引用修改会波及所有引用 |
| **线程安全** | 不可变对象天然线程安全，无需同步即可在多线程间共享 |
| **HashCode 缓存** | String 的 `hashCode` 在首次调用后缓存到 `private int hash` 字段，若可变则缓存失效 |
| **类加载安全** | 类名、包名、路径等关键信息以 String 传递，可变会引入安全漏洞 |
| **网络 / 数据库安全** | 连接 URL、用户名密码等若可变，攻击者可篡改 |

#### 如果 String 可变会怎样？

```java
// 假设 String 可变
String s = "abc";
HashMap<String, Integer> map = new HashMap<>();
map.put(s, 123);
s.set(1, 'd');  // 修改后 hashCode 变了
map.get("abc"); // → null（hashCode 不匹配）
map.get("adc"); // → 123（但"adc"在桶里不存在）
```

- HashMap 中作为 key 的 String 修改后无法正确索引，导致内存泄漏
- 常量池中所有引用 String 的变量都会受影响

### StringBuilder

- 提供了一系列方法进行字符串的增删改查操作，直接在原有字符串对象的底层数组上进行，不生成新对象
- **不是线程安全**的，不适用于多线程环境
- 相比 String，在频繁修改字符串时性能更好。Java 中的字符串拼接 `+` 操作底层就是通过 StringBuilder 实现的

```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i);
}
String result = sb.toString();
```

### StringBuffer

- 和 StringBuilder 类似，但 StringBuffer 是线程安全的（方法前加了 `synchronized` 关键字）
- 现在已不常用，因为一般不会在多线程场景下频繁修改字符串

| | String | StringBuilder | StringBuffer |
|--|--------|---------------|--------------|
| 可变性 | ❌ 不可变 | ✅ 可变 | ✅ 可变 |
| 线程安全 | ✅（不可变天然安全） | ❌ | ✅（synchronized） |
| 性能 | 修改时产生新对象，慢 | 快 | 慢于 StringBuilder |

---

### intern 方法

`intern()` 方法的作用：从字符串常量池中获取字符串的引用。如果常量池中已有相同内容的字符串，直接返回其引用；否则在常量池中创建并返回引用。

---

### String 转 Integer

主要有两个方法：
- `Integer.parseInt(String s)` → 返回 int
- `Integer.valueOf(String s)` → 返回 Integer（利用了缓存机制）

---

## 4. 异常机制

### try-catch-finally

```java
// 情况 1：try 返回 1，finally 打印 "3"
public static int test() {
    try {
        return 1;
    } catch (Exception e) {
        return 2;
    } finally {
        System.out.print("3");
    }
}

// 情况 2：finally 中的 return 会覆盖 try 中的 return
public static int test1() {
    try {
        return 2;
    } finally {
        return 3;  // 覆盖 try 的返回值
    }
}

// 情况 3：finally 修改变量不影响 try 的返回值
public static int test1() {
    int i = 0;
    try {
        i = 2;
        return i;   // 返回值已确定（2），finally 中修改 i 不影响
    } finally {
        i = 3;      // 只修改了局部变量 i，不影响已确定的返回值
    }
}
```

**如果 catch 和 finally 都抛异常**：最终抛出的是 finally 块中的异常，catch 块中的异常被丢弃。

为避免异常被覆盖，可在 catch 中用一个变量保存异常，finally 中处理完自身逻辑后再抛出。

**finally 不执行的三种特殊情况**：
1. 程序所在的线程死亡
2. 关闭 CPU（如 `System.exit()`）
3. 某些致命 Error（如下）

### Error 与 Exception 的区别

**Throwable** 有两子类：
- **Exception**：程序可恢复的异常，应被 try-catch 处理
- **Error**：严重的系统级问题，程序通常不应捕获

**常见 Error**：

| Error | 说明 |
|---|---|
| `StackOverflowError` | 递归过深，栈空间耗尽 |
| `OutOfMemoryError` | 堆/元空间/直接内存耗尽 |
| `NoClassDefFoundError` | JVM 找不到类的定义 |
| `UnsatisfiedLinkError` | native 方法加载失败 |

**finally 遇到 Error**：
- Error 可以被 try-catch 捕获，此时 finally **仍然会执行**
- 但某些致命 Error 会导致 finally **不执行**（对应上面第 3 点）：
  - `StackOverflowError`：栈已满，finally 块来不及运行
  - `OutOfMemoryError`：连 finally 中的代码都无法分配内存

**最佳实践**：不要捕获 Error。Error 意味着 JVM 已处于不可恢复状态，catch 也无法让程序恢复正常，应让其向上传播导致 JVM 退出。

### Checked vs Unchecked 异常

- **Unchecked Exception**（如 NullPointerException）：本质是代码 Bug，最好让 Bug 暴露出来去修复代码，而不是用 try-catch 掩盖
- **Checked Exception**（如 IOException）：适用于异常是业务逻辑的一部分，调用方必须处理的情况。比如"余额不足异常"不是 Bug，而是正常的业务分支，用 Checked Exception 强制调用者去处理

---

## 5. equals 和 hashCode

**为什么重写 equals() 时必须重写 hashCode()？**

因为两个相等的对象的 hashCode 值必须是相等的。如果 equals 判断两个对象相等而 hashCode 不同，在使用 HashMap 等散列集合时会出现问题（同一个 key 放在不同桶里，导致查到两个不同的值）。

**规则**：
- hashCode 相等 → 两个对象不一定相等（哈希碰撞）
- hashCode 相等且 equals 为 true → 两个对象相等
- hashCode 不相等 → 两个对象一定不相等

---

## 6. 反射

反射允许 Java 在运行时检查和操作类的方法和字段。通过反射，可以动态地获取类的字段、方法、构造方法等信息，并在运行时调用方法或访问字段。

### 原理

每个类在加载到 JVM 后，都会在方法区生成一个对应的 Class 对象，这个对象包含了类的所有元信息，比如字段、方法、构造器、注解等。通过这个 Class 对象，我们就能在运行时动态地创建对象、调用方法、访问字段。

### 优缺点

**优点**：
- 能够在运行时动态操作类和对象
- 能够编写通用的代码，一套代码可以处理不同类型的对象
- 能够突破访问限制，访问 private 字段和方法

**缺点**：
- 性能问题：反射操作比直接调用要慢很多（需要在运行时解析类信息、类型检查、权限验证等）
- 安全问题：反射能绕过访问控制，破坏类的封装

### 使用场景

- Spring 框架大量使用反射来动态加载和管理 Bean
- Java 动态代理机制使用反射来创建代理类
- JUnit 和 TestNG 等测试框架使用反射发现和执行测试方法
- 通用工具类，如 BeanUtils、MapStruct 等对象拷贝工具

---

## 7. 泛型

泛型主要用于提高代码的类型安全，它允许在定义类、接口和方法时使用类型参数，这样可以在编译时检查类型一致性，避免不必要的类型转换和类型错误。

没有泛型的时候，像 List 这样的集合类存储的是 Object 类型，导致从集合中读取数据时，必须进行强制类型转换，否则会引发 ClassCastException。

```java
List list = new ArrayList();
list.add("hello");
String str = (String) list.get(0); // 必须强制类型转换
```

### 泛型擦除

所谓的泛型擦除，官方名叫"类型擦除"。Java 的泛型是伪泛型，这是因为 Java 在编译期间，所有的类型信息都会被擦掉。在运行的时候是没有泛型的。

### 泛型与重载

```java
public class GenericTypes {
    public static void method(List<String> list) { ... }
    public static void method(List<Integer> list) { ... }
}
```

上面这段代码编译不通过。因为 `List<String>` 和 `List<Integer>` 编译之后都被擦除了，变成了相同的原生类型 `List`，导致特征签名重复。

### 泛型与静态变量

```java
class GT<T> {
    public static int var = 0;
}

GT<Integer>.var = 1;
GT<String>.var = 2;
System.out.println(GT<Integer>.var); // 输出 2
```

由于经过类型擦除，所有的泛型类实例都关联到同一份字节码上，泛型类的静态变量是共享的。`GT<Integer>.var` 和 `GT<String>.var` 其实是同一个变量。

---

## 8. 注解

**本质上是一个标记**，反射是"读取标记的工具"。通过反射获取注解信息，动态执行逻辑（如 Spring 扫描 @Controller 注解创建 Bean）。

注解可以标记在类上、方法上、属性上等，标记自身也可以设置一些值。

**注解生命周期**：
- `SOURCE`：仅源码存在，编译成 class 文件后消失（如 @Override）
- `CLASS`：编译后保留在 class 文件，但运行时 JVM 不加载（默认）
- `RUNTIME`：运行时保留，可通过反射获取（框架核心，如 Spring 注解）

---

## 9. IO

### BIO、NIO、AIO 之间的区别

| | BIO（Blocking IO） | NIO（Non-blocking IO） | AIO（Async IO） |
|--|:--:|:--:|:--:|
| 模型 | 同步阻塞 | 同步非阻塞 | 异步非阻塞 |
| 线程模型 | 一个连接一个线程 | 一个线程处理多个连接（Selector） | OS 处理完通知回调 |
| 适用场景 | 连接数少、固定架构 | 连接数多、短连接 | 连接数多、长时间连接 |

### 序列化与反序列化

- **序列化**：将数据结构或对象转换成可以存储或传输的形式，通常是二进制字节流，也可以是 JSON、XML 等文本格式
- **反序列化**：将在序列化过程中所生成的数据转换为原始数据结构或者对象的过程

### Socket 与 RPC

- **Socket**：网络通信的基础，表示两台设备之间通信的一个端点。Socket 通常用于建立 TCP 或 UDP 连接，实现进程间的网络通信
- **RPC**：一种协议，允许程序调用位于远程服务器上的方法，就像调用本地方法一样。RPC 通常基于 Socket 通信实现

---

## 10. 其他高频题

### Java 语言的特点

- **跨平台**：一次编写，到处运行（JVM 屏蔽 OS 差异）
- **面向对象**：封装、继承、多态
- **自动内存管理**：GC 自动回收无用对象
- **健壮**：强类型、异常处理机制、没有指针
- **多线程**：内置对多线程编程的支持

### 自增自减

```java
int i = 0;
System.out.println(i++);  // 0（先返回 i，再 i = i + 1）
System.out.println(++i);  // 2（先 i = i + 1，再返回 i）
```

- `i++`：先取 i 的值参与表达式，然后 i 自增
- `++i`：先 i 自增，然后取 i 的新值参与表达式

**字节码层面**：

| 操作 | 字节码 |
|---|---|
| `i++` | `iload`（加载）→ `iinc`（自增） |
| `++i` | `iinc`（自增）→ `iload`（加载） |

### this 关键字

- 指向当前对象的引用，编译器隐式传入每个非静态方法
- 用于区分成员变量和局部变量（如 `this.name = name`）
- 构造方法中调用另一个构造方法：`this(args)`（必须在第一行）
- 返回当前对象：`return this`（链式调用）

### Object 类的常见方法

| 方法 | 作用 |
|---|---|
| `equals(Object)` | 判断对象是否"相等"（默认比较引用，可重写） |
| `hashCode()` | 返回哈希值（与 equals 一致约定） |
| `toString()` | 返回字符串表示，默认：`类名@哈希码` |
| `clone()` | 创建并返回对象的浅拷贝（需实现 Cloneable） |
| `finalize()` | GC 回收前调用（JDK 9 起已废弃） |
| `getClass()` | 返回运行时类（`Class<?>`） |
| `notify()` / `notifyAll()` / `wait()` | 线程间通信（配合 synchronized 使用） |

### Java 创建对象的方式

| 方式 | 说明 | 是否调用构造方法 |
|---|---|---|
| `new` 关键字 | `new String("abc")` | ✅ |
| `Class.newInstance()` | `clazz.newInstance()`（JDK 9 起标记废弃） | ✅ |
| `Constructor.newInstance()` | `constructor.newInstance(args)` | ✅ |
| `clone()` | `obj.clone()` | ❌（直接复制内存） |
| 反序列化 | `ObjectInputStream.readObject()` | ❌ |
| Unsafe.allocateInstance | `unsafe.allocateInstance(clazz)` | ❌（跳过构造方法） |

### 类和父类的静态代码块、构造方法执行顺序

**执行顺序**（单类）：

```
静态代码块（类加载时执行一次） → 构造代码块 → 构造方法
```

**继承关系**：

```java
// 执行顺序：
// 1. 父类静态代码块
// 2. 子类静态代码块
// 3. 父类构造代码块
// 4. 父类构造方法
// 5. 子类构造代码块
// 6. 子类构造方法
```

**规律**：先静态，再父子；先父后子；构造代码块在构造方法之前执行。

---

## 11. 集合框架

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

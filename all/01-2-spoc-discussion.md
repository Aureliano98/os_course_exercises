# lec1: 操作系统概述

---

## **提前准备**

（请在上课前完成）

* 完成lec1的视频学习和提交对应的在线练习
* git pull ucore\_os\_lab, ucore\_os\_docs, os\_tutorial\_lab, os\_course\_exercises in github repos。这样可以在本机上完成课堂练习。
* 知道OS课程的入口网址，会使用在线视频平台，在线练习/实验平台，在线提问平台\(piazza\)
  * [http://os.cs.tsinghua.edu.cn/oscourse/OS2019spring](http://os.cs.tsinghua.edu.cn/oscourse/OS2019spring)


* 会使用linux shell命令，如ls, rm, mkdir, cat, less, more, gcc等，也会使用linux系统的基本操作。
* 在piazza上就学习中不理解问题进行提问。



# 思考题

## 填空题

* 当前常见的操作系统主要用**C，C++，汇编**编程语言编写。
* "Operating system"这个单词起源于**operator**。
* 在计算机系统中，控制和管理**系统资源**、有效地组织**程序**运行的系统软件称作**操作系统**。
* 允许多用户将若干个作业提交给计算机系统集中处理的操作系统称为**批处理**操作系统
* 你了解的当前世界上使用最多的操作系统是**Android** (since 2017)。
* 应用程序通过**系统调用**接口获得操作系统的服务。
* 现代操作系统的特征包括**并发（concurrency）**，**共享（sharing）**、**虚拟（virtualization）**，**异步（asynchronism）（，持久性（persistency））**。
* 操作系统内核的架构包括**宏内核（monolithic kernel）**，**微内核（microkernel）**，**外核（exokernel）**。


## 问答题

- 请总结你认为操作系统应该具有的特征有什么？并对其特征进行简要阐述。

	并发（concurrency）：程序为每个程序建立进程。多个进程之间可以并发执行和交换信息。（进程：系统中能独立运行并作为资源分配的基本单位，是一个活动的实体）

	共享（sharing）：系统中的资源可供内存中多个并发执行的进程共同使用。根据资源的属性不同多个进程对资源的共享方式不同，分为互斥共享方式和同时共享方式。

	虚拟（virtualization）：把一个物理实体变成若干个逻辑上的对应物。虚拟内存属于空间虚拟化，CPU虚拟化属于时间虚拟化。

	异步（asynchronization）：进程之间以异步的方式运行，每个进程何时执行、暂停、运行时间不可预知；但只要运行环境相同，确定性的程序会获得相同的结果。

	持久性（persistency）：操作系统的文件系统支持数据的持久化存储。

	[Ref: https://blog.csdn.net/xieyutian1990/article/details/38414951](https://blog.csdn.net/xieyutian1990/article/details/38414951)

- 为什么现在的操作系统基本上用C语言来实现？为什么没有人用python，java来实现操作系统？

	1. 后者不够底层（Python需要PVM，Java需要JVM），直接操作内存、与汇编结合能力受限
	2. 后者需要一些操作才能达到较好的性能，一般较慢

---

## 可选练习题

---

- 请分析并理解[v9\-computer](https://github.com/chyyuu/os_tutorial_lab/blob/master/v9_computer/docs/v9_computer.md)以及模拟v9\-computer的em.c。理解：在v9\-computer中如何实现时钟中断的；v9 computer的CPU指令，关键变量描述有误或不全的情况；在v9\-computer中的跳转相关操作是如何实现的；在v9\-computer中如何设计相应指令，可有效实现函数调用与返回；OS程序被加载到内存的哪个位置,其堆栈是如何设置的；在v9\-computer中如何完成一次内存地址的读写的；在v9\-computer中如何实现分页机制。


- 请编写一个小程序，在v9-cpu下，能够输出字符


- 输入的字符并输出你输入的字符


- 请编写一个小程序，在v9-cpu下，能够产生各种异常/中断


- 请编写一个小程序，在v9-cpu下，能够统计并显示内存大小



- 请分析并理解[RISC-V CPU](http://www.riscvbook.com/chinese/)以及会使用模拟RISC\-V(简称RV)的qemu工具。理解：RV的特权指令，CSR寄存器和在RV中如何实现时钟中断和IO操作；OS程序如何被加载运行的；在RV中如何实现分页机制。
  - 请编写一个小程序，在RV下，能够输出字符
  - 输入的字符并输出你输入的字符
  - 请编写一个小程序，在RV下，能够产生各种异常/中断
  - 请编写一个小程序，在RV下，能够统计并显示内存大小

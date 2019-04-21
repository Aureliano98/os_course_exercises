# lec16: lab6 spoc 思考题

- 有"spoc"标记的题是要求拿清华学分的同学在实体课上完成的，对于学堂在线的选课同学是可选题目。


## 视频相关思考题

### 16.1 总体介绍

1. 进程控制块中与调度相关的字段有哪些？在什么情况下会对其进行修改？

   ```C
   volatile bool need_resched;    		// bool value: need to be rescheduled to release CPU?
   uint32_t wait_state;               	// waiting state
   list_entry_t run_link;              // the entry linked in run queue
   int time_slice;                     // time slice for occupying the CPU
   skew_heap_entry_t lab6_run_pool;  	// FOR LAB6 ONLY: the entry in the run pool
   uint32_t lab6_stride;              	// FOR LAB6 ONLY: the current stride of the process
   uint32_t lab6_priority;   			// FOR LAB6 ONLY: the priority of process, 
   									// set by lab6_set_priority(uint32_t)
   ```

2. ucore的就绪队列数据结构在哪定义？在哪进行修改？

   `kern/schedule/sched.c`中定义。它将具体修改工作主要分派给某个实现类，例如`kern/schedule/default_sched.c`，自身也承担部分修改功能.

   定义：

   ```C
   static struct run_queue *rq;
   ```
   修改：

   * `sched_init`中进行必要初始化
   * `sched_class_enqueue`, `sched_class_dequeue`入队、出队

3. ucore的等待队列数据结构在哪定义？在哪进行修改？

   `kern/schedule/sched.c`中定义。

   定义：

   ```C
   static list_entry_t timer_list;
   ```
   修改：暂时未作修改（除了`sched_init`中初始化）。

4. 尝试跟踪ucore中的调度过程。

   中断响应、线程的中断现场保存、中断处理、调度触发、当前线程入队、选取下一个运行线程、下一个运行线程出队、线程切换、新线程的中断现场恢复、新线程的继续执行

### 16.2 调度算法支撑框架

1. 调度算法支撑框架中的各个函数指针的功能是啥？会被谁在何种情况下调用？

   初始化、触发、选取、出队、入队、切换

2. 调度函数schedule()的调用函数分析，了解进程调度的原因。请分析ucore中所有可能的调度位置，并说明可能的调用原因。

   * do_exit：进程推出
   * do_wait：父进程等待子进程
   * cpu_idle：没有其他就绪进程时执行`cpu_idle`，轮询驱动`scheudle`
   * lock：线程获取锁失败时进入睡眠状态
   * init_main：所有用户进程的祖先 完成对孤儿进程的资源回收
   * trap：时钟中断时更新调度算法参数、进程时间片用尽后做好切换的标志

### 16.3 时间片轮转调度算法

1. 时间片轮转调度算法是如何基于调度算法支撑框架实现的？

   `sched_class`用函数指针方式提供调度类的interface，通过设置`default_sched_class`可以提供不同实现。

2. 时钟中断如何调用RR_proc_tick()的？

   时钟中断时会检查时间片的计数，到达零（时间片用完）时，设置可调度标志（`need_resched`）。

### 16.4 stride调度算法

1. stride调度算法的思路？

  * 步长值stride
  * 步进值pass

  以步长为优先级的动态优先级调度算法；每次执行一个时间片，时间片用完时，优先级增加量为“步进”值。

2. stride算法的特征是什么？
   * 动态优先级调度算法
   * 确定的调度顺序
   * 线程的执行时间与步进值的倒数成正比

3. stride调度算法是如何避免stride溢出问题的？

   利用无符号数的有符号比较，从而避免步长值修改时的溢出处理。这是由于`stride`是循环计数，且实际值（不考虑溢出）两两间差值有界，因此将`stride`作为有符号整数作差可以反映相对大小。

4. 无符号数的有符号比较会产生什么效果？

   有符号数会提升为无符号数比较。例如`int(-1) > unsigned(0)`.

   > [无符号数的有符号比较会产生什么效果？](https://piazza.com/class/i5j09fnsl7k5x0?cid=357)

5. 什么是斜堆(skew heap)？斜堆在stride算法的实现中有什么用？

   类似leftist heap，但不用记录高度，每次合并后一路向上交换左右子树，直观上来看把变高的最右路径甩到左侧。用于高效实现优先队列，且编码容易、所需空间小。

   > 参考文档：[Skew heap](https://en.wikipedia.org/wiki/Skew_heap) [斜堆](http://baike.baidu.com/link?url=BYMgWi8gT5sZE2sG0ndX1CoYZVhe5NJig5s9-u1gO7ldVIxRwLzUpL9pvqN5qEOk_8nGUuJ7VSZNU8pGSicUnK)
   >

   > 斜堆的堆顶是优先级最小的节点；斜堆的合并时间开销为**amortized** O(logN)，删除最小节点操作和插入操作都可以转换成合并操作，开销很小；

## 小组练习与思考题

### (1)(spoc) 跟踪和展现ucore的处理机调度过程

基于对“视频相关思考题”中16.2节第2小题的回答，在ucore执行处理机调度时，选择一种调度情况进行跟踪并显示上一个让出CPU线程的暂停代码位置和下一个进入执行状态线程的开始执行位置。

### (2)(spoc) 理解调度算法支撑框架的执行过程

即在ucore运行过程中通过`cprintf`函数来完整地展现出来多个进程在调度算法和框架的支撑下，在相关调度点如何动态调度和执行的细节。(越全面细致越好)

请完成如下练习，完成代码填写，并形成spoc练习报告
> 需写练习报告和简单编码，完成后放到git server 对应的git repo中

### 练习用的[lab6 spoc exercise project source code](https://github.com/chyyuu/ucore_lab/tree/master/labcodes_answer/lab6_result)



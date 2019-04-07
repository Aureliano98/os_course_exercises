#lec12: 进程／线程控制spoc练习

## 视频相关思考题
### 12.1 进程切换

1. 进程切换的可能时机有哪些？

   进程等待，进程被高优先级进程抢先，进程时间片用完，进程结束

   

2. 分析ucore的进程切换代码，说明ucore的进程切换触发时机和进程切换的判断时机都有哪些。

    在lab4中`switch_to`的调用链只有以下一条：

    `schedule > proc_run > switch_to`

    在`kern_init`完成后，`cpu_idle`中不断轮询检查当前进程控制块`proc_struct->need_reshced`，若条件成立则展开上述调用链。

    

3. ucore的进程控制块数据结构是如何组织的？主要字段分别表示什么？

    ```C
    struct proc_struct {
        enum proc_state state;                      // Process state
        int pid;                                    // Process ID
        int runs;                                   // the running times of Proces
        uintptr_t kstack;                           // Process kernel stack
        volatile bool need_resched;                 // bool value: need to be rescheduled to release CPU?
        struct proc_struct *parent;                 // the parent process
        struct mm_struct *mm;                       // Process's memory management field
        struct context context;                     // Switch here to run process
        struct trapframe *tf;                       // Trap frame for current interrupt
        uintptr_t cr3;                              // CR3 register: the base addr of Page Directroy Table(PDT)
        uint32_t flags;                             // Process flag
        char name[PROC_NAME_LEN + 1];               // Process name
        list_entry_t list_link;                     // Process link list 
        list_entry_t hash_link;                     // Process hash list
    };
    ```

    其中`link_list`将`proc_struct`组织成链表；而`hash_link`对应hash表中PID对应的链表中的一个表项（开链定址法），方便根据PID查找。

    

### 12.2 进程创建

1. fork()的返回值是唯一的吗？父进程和子进程的返回值是不同的。请找到相应的赋值代码。

   `fork`若成功，父进程返回子进程的PID（唯一，>0），子进程中返回0；否则，父进程返回-1，并且`errno`被设置。

   ucore中在`do_fork`中设置。

   

2. 新进程创建时的进程标识是如何设置的？请指明相关代码。

   `get_pid`查找`proc_list`分配一个唯一的PID；但是`idleproc`的PID是硬编码的。

   

3. 请通过fork()的例子中进程标识的赋值顺序说明进程的执行顺序。

   `idleproc -> initproc > int_main`

   

4. 请在ucore启动时显示空闲进程（idleproc）和初始进程（initproc）的进程标识。

5. 请在ucore启动时显示空闲线程（idleproc）和初始进程(initproc)的进程控制块中的“pde_t *pgdir”的内容。它们是否一致？为什么？

### 12.3 进程加载

1. 加载进程后，新进程进入就绪状态，它开始执行时的第一条指令的位置，在elf中保存在什么地方？在加载后，保存在什么地方？

   ELF header中有一个`uint32_t entry`指定程序入口的虚拟地址。

   `load_icode`读取ELF header，将第一条指令位置放在`trapframe`中。

   

2. 第一个用户进程执行的代码在哪里？它是什么时候加载到内存中的？

   `user_main`内核线程中调用`KERNEL_EXECVE`加载用户进程。

   

### 12.4 进程等待与退出

1. 试分析wait()和exit()的结果放在什么地方？exit()是在什么时候放进去的？wait()在什么地方取到出的？

   放在PCB也即`proc_struct`中。`exit`是在`do_exit`中放进去的（见下一问），`wait`是在`do_wait`中取出的。

   子进程在`do_exit`中操作，其功能如下：

   ```C
   // do_exit - called by sys_exit
   //   1. call exit_mmap & put_pgdir & mm_destroy to free the almost all memory space of process
   //   2. set process' state as PROC_ZOMBIE, then call wakeup_proc(parent) to ask parent reclaim itself.
   //   3. call scheduler to switch to other process
   ```

   在第2步中有这么几行，设置PCB的内容

   ```C
   current->state = PROC_ZOMBIE;
   current->exit_code = error_code;
   ```

   之后父进程在`do_wait`中就得到返回值。

   父进程在`do_wait`中根据PID找到子进程的PCB也即`proc_struct`后，从中取出`exit_code`，放到`code_store`中。

   

2. 试分析ucore操作系统内核是如何把子进程exit()的返回值传递给父进程wait()的？

   见第1问。

   

3. 什么是僵尸进程和孤儿进程？

   僵尸进程：子进程结束了，但父进程没有等待，该子进程称为僵尸进程

   孤儿进程：父进程完成执行或被终止后仍继续运行的一类进程

   

4. 试分析sleep()系统调用的实现。在什么地方设置的定时器？它对应的等待队列是哪个？它的唤醒操作在什么地方？

   1. 在`do_sleep`中会设置`timer_t`结构。

   2. ucore中没有严格区分等待和就绪状态，似乎只有一个`run_queue`保存了目前不在运行而runnable的进程的PCB，应该就是它了。

   3. `kern/schedule/sched`中有一个`timer_list`唤醒操作在定时器中断的ISR中。

   

5. 通常的函数调用和函数返回都是一一对应的。有不是一一对应的例外情况？如果有，请举例说明。

* `sys_exit`不返回

* `fork`对应2次函数返回

  

## 小组思考题

(1) (spoc)设计一个简化的进程管理子系统，可以管理并调度支持“就绪”和“等待”状态的简化进程。给出了[参考代码](https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab5/process-cpuio-homework.py)，请理解代码，并完成＂YOUR CODE"部分的内容．　可２个人一组

### 进程的状态 
```
 - RUNNING - 进程正在使用CPU
 - READY   - 进程可使用CPU
 - WAIT    - 进程等待I/O完成
 - DONE    - 进程结束
```

### 进程的行为
```
 - 使用CPU, 
 - 发出YIELD请求,放弃使用CPU
 - 发出I/O操作请求,放弃使用CPU
```

### 进程调度
 - 使用FIFO/FCFS：先来先服务, 只有进程done, yield, io时才会执行切换
   - 先查找位于proc_info队列的curr_proc元素(当前进程)之后的进程(curr_proc+1..end)是否处于READY态，
   - 再查找位于proc_info队列的curr_proc元素(当前进程)之前的进程(begin..curr_proc-1)是否处于READY态
   - 如都没有，继续执行curr_proc直到结束

### 关键模拟变量
 - io_length : IO操作的执行时间
 - 进程控制块
```
PROC_CODE = 'code_'
PROC_PC = 'pc_'
PROC_ID = 'pid_'
PROC_STATE = 'proc_state_'
```
 - 当前进程 curr_proc 
 - 进程列表：proc_info是就绪进程的队列（list），
 - 在命令行（如下所示）需要说明每进程的行为特征：（１）使用CPU ;(2)等待I/O
```
   -l PROCESS_LIST, --processlist= X1:Y1,X2:Y2,...
   X 是进程的执行指令数; 
   Ｙ是执行yield指令（进程放弃CPU,进入READY状态）的比例(0..100) 
   Ｚ是执行I/O请求指令（进程放弃CPU,进入WAIT状态）的比例(0..100)
```
 - 进程切换行为：系统决定何时(when)切换进程:进程结束或进程发出yield请求

### 进程执行
```
instruction_to_execute = self.proc_info[self.curr_proc][PROC_CODE].pop(0)
```

### 关键函数
 - 系统执行过程：run
 - 执行状态切换函数:　move_to_ready/running/done　
 - 调度函数：next_proc

### 执行实例

#### 例1
```
$./process-simulation.py  -l 5:30:30,5:40:30 -c
Produce a trace of what would happen when you run these processes:
Process 0
  io
  io
  yld
  cpu
  yld

Process 1
  yld
  io
  yld
  yld
  yld

Important behaviors:
  System will switch when the current process is FINISHED or ISSUES AN YIELD or IO
Time     PID: 0     PID: 1        CPU        IOs 
  1      RUN:io      READY          1            
  2     WAITING    RUN:yld          1          1 
  3     WAITING     RUN:io          1          1 
  4     WAITING    WAITING                     2 
  5     WAITING    WAITING                     2 
  6*     RUN:io    WAITING          1          1 
  7     WAITING    WAITING                     2 
  8*    WAITING    RUN:yld          1          1 
  9     WAITING    RUN:yld          1          1 
 10     WAITING    RUN:yld          1          1 
 11*    RUN:yld       DONE          1            
 12     RUN:cpu       DONE          1            
 13     RUN:yld       DONE          1            
```

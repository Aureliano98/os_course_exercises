# lec14: lab5 spoc 思考题

- 有"spoc"标记的题是要求拿清华学分的同学要在实体课上完成，并按时提交到学生对应的ucore_code和os_exercises的git repo上。


## 视频相关思考题

### 14.1 总体介绍

1. 第一个用户进程创建有什么特殊的？

   用户态代码段的初始化

2. 系统调用的参数传递过程？

   eax中存储系统调用编号，edx, ecx, ebx, edi, esi依次存储参数

   参见：用户态函数syscall()中的汇编代码；

   Ref: https://www.ibm.com/developerworks/library/l-ia/index.html

3. getpid的返回值放在什么地方了？

   `current->tf->tf_regs.reg_eax`

   参见：用户态函数syscall()中的汇编代码；

### 14.2 进程的内存布局

1. ucore的内存布局中，页表、用户栈、内核栈在逻辑地址空间中的位置？

   页表：内核页表位于0xfafeb000 (= VPT + (VPT >> 10))；用户页表由alloc_page得到，不固定

   用户栈：0xb0000000以下，不超过256 * 4K (KSTACKSIZE = KSTACKPAGE * PGSIZE)

   内核栈：除了bootstack之外（位于0xfafeb000以下2 * 4K的空间），都由alloc_pages得到，不固定


```C
     #define VPT 0xFAC00000
     #define KSTACKPAGE 2 // # of pages in kernel stack
     #define KSTACKSIZE (KSTACKPAGE * PGSIZE) // sizeof kernel stack
     #define USERTOP 0xB0000000
     #define USTACKTOP USERTOP
     #define USTACKPAGE 256 // # of pages in user stack
     #define USTACKSIZE (USTACKPAGE * PGSIZE) // sizeof user stack
```

1. (spoc)尝试在panic函数中获取并输出用户栈和内核栈的函数嵌套信息和函数调用参数信息，然后在你希望的地方人为触发panic函数，并输出上述信息。

1. (spoc)尝试在panic函数中获取和输出页表有效逻辑地址空间范围和在内存中的逻辑地址空间范围，然后在你希望的地方人为触发panic函数，并输出上述信息。

1. 尝试在进程运行过程中获取内核空间中各进程相同的页表项（代码段）和不同的页表项（内核堆栈）？

### 14.3 执行ELF格式的二进制代码-do_execve的实现

1. 在do_execve中的的当前进程如何清空地址空间内容的？在什么时候开始使用新加载进程的地址空间？

   清空进程地址空间是在initproc所在进程地址空间

   CR3设置成新建好的页表地址后，开始使用新的地址空间

   特殊地，如果原先的`mm_struct`引用计数减少到0，要依次清楚原先进程中页表和页目录表的内容（不知道后者意义何在）、释放页表空间、释放`mm_struct`的空间。

   ```C
   if (mm != NULL) {
       lcr3(boot_cr3);
       if (mm_count_dec(mm) == 0) {
           exit_mmap(mm);
           put_pgdir(mm);
           mm_destroy(mm);
       }
       current->mm = NULL;
   }
   ```

2. 新加载进程的第一级页表的建立代码在哪？

   `sys_exec > do_execve > load_icode > setup_pgdir `，它会通过`alloc_page`分配一个PDT，复制`boot_pgdir`内容，并设置自映射。

3. do_execve在处理中是如何正确区分出用户进程和线程的？并为此采取了哪些不同的处理？

   应该是`do_fork`要区分？

   `do_fork`声明如下：

   ```C
   int do_fork(uint32_t clone_flags, uintptr_t stack, struct trapframe *tf);
   ```

   具体而言，`sys_fork`调用`do_fork`时`clone_flags & CLONE_VM == 0`, 而`kernel_thread`调用`do_fork`时`clone_flags & CLONE_VM == 1`

### 14.4 执行ELF格式的二进制代码-load_icode的实现

1. 第一个内核线程和第一个用户进程的创建有什么不同？

   相应线程的内核栈创建时，多了SS和ESP的设置；

   用户进程需要创建用户地址空间，并把用户代码复制到用户地址空间；

2. 尝试跟踪分析新创建的用户进程的开始执行过程？

   首先进行进程切换，`schedule > proc_run > switch_to`.

   然后通过`forkrets`跳转到用户态程序入口`user_main`. 其中`kernel_execve`调用`sys_exec`系统调用；Trap handler最终将其分派给`do_execve`.

### 14.5 进程复制

1. 为什么新进程的内核堆栈可以先于进程地址空间复制进行创建？

   内核栈在进程的内核地址空间，而各进程的内核地址空间是共享的；

2. 进程复制的代码在哪？复制了哪些内容？

   do_fork > copy_mm

   页表项，内存控制相关的mm_struct，trapframe的大多数内容（除了eax设置为0，eflags的interrupt flag FL_IF要置1）。

3. 进程复制过程中有哪些修改？为什么要修改？

   * 内核栈（通过setup_kstack重新分配一个，因为每个进程要有自己的内核栈）
   * 页表（每个进程有自己的页表）
   * trapframe（eax设置为0，eflags的interrupt flag FL_IF要置1）
   * context（eip设为forkret，esp设置为trapframe，从而让进程切换后能够回到trapframe中eip）
   * PCB字段修改（proc_struct::mm, cr3）

4. 分析第一个用户进程的创建流程，说明进程切换后执行的第一条是什么。

   以lcr3为切换进程标志，则第一条是（`kern/process/proc::do_execve`）

   ```C
   if (mm_count_dec(mm) == 0) {
       exit_mmap(mm);
       put_pgdir(mm);
       mm_destroy(mm);
   }
   ```

### 14.6 内存管理的copy-on-write机制

1. 什么是写时复制？

   OS中，指fork的进程间共享物理空间，直到有写操作发生时再分配并拷贝物理空间。

2. 写时复制的页表在什么时候进行复制？共享地址空间和写时复制有什么不同？

   对内存进行写操作时。对于用户而言，后者不同进程的地址空间是独立的，而前者是共享的。

3. 存在有多个（n>2）进程具有父子关系，且采用了COW机制的情况。这个情况与只有父子两个进程的情况相比，在设计COW时，需要注意的新问题是什么？有何解决方案？

   物理页面管理需要引用计数。


## 小组练习与思考题

### (1)(spoc) 在真实机器的u盘上启动并运行ucore lab,

请准备一个空闲u盘，然后请参考如下网址完成练习

https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab1/lab1-boot-with-grub2-in-udisk.md

> 注意，grub_kernel的源码在ucore_lab的lab1_X的git branch上，位于 `ucore_lab/labcodes_answer/lab1_result`

(报告可课后完成)请理解grub multiboot spec的含义，并分析ucore_lab是如何实现符合grub multiboot spec的，并形成spoc练习报告。

### (2)(spoc) 理解用户进程的生命周期。

> 需写练习报告和简单编码，完成后放到网络学堂 OR git server 对应的git repo中

### 练习用的[lab5 spoc exercise project source code](https://github.com/chyyuu/ucore_lab/tree/master/related_info/lab5/lab5-spoc-discuss)


#### 掌握知识点
1. 用户进程的启动、运行、就绪、等待、退出
2. 用户进程的管理与简单调度
3. 用户进程的上下文切换过程
4. 用户进程的特权级切换过程
5. 用户进程的创建过程并完成资源占用
6. 用户进程的退出过程并完成资源回收

> 注意，请关注：内核如何创建用户进程的？用户进程是如何在用户态开始执行的？用户态的堆栈是保存在哪里的？

阅读代码，在现有基础上再增加一个用户进程A，并通过增加cprintf函数到ucore代码中，
能够把个人思考题和上述知识点中的内容展示出来：即在ucore运行过程中通过`cprintf`函数来完整地展现出来进程A相关的动态执行和内部数据/状态变化的细节。(约全面细致约好)

请完成如下练习，完成代码填写，并形成spoc练习报告

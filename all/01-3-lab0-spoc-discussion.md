# lec2：lab0 SPOC思考题

## **提前准备**
（请在上课前完成，option）

- 完成lec2的视频学习
- git pull ucore_os_lab, os_tutorial_lab, os_course_exercises  in github repos。这样可以在本机上完成课堂练习。
- 了解代码段，数据段，执行文件，执行文件格式，堆，栈，控制流，函数调用,函数参数传递，用户态（用户模式），内核态（内核模式）等基本概念。思考一下这些基本概念在linux, ucore, v9-cpu中是如何具体体现的。
- 安装好ucore实验环境，能够编译运行ucore labs中的源码。
- 会使用linux中的shell命令:objdump，nm，file, strace，gdb等，了解这些命令的用途。
- 会编译，运行，使用v9-cpu的dis,xc, xem命令（包括启动参数），阅读v9-cpu中的v9\-computer.md文档，了解汇编指令的类型和含义等，了解v9-cpu的细节。
- 了解基于v9-cpu的执行文件的格式和内容，以及它是如何加载到v9-cpu的内存中的。
- 在piazza上就学习中不理解问题进行提问。

---

## 思考题

- 你理解的对于类似ucore这样需要进程/虚存/文件系统的操作系统，在硬件设计上至少需要有哪些直接的支持？至少应该提供哪些功能的特权指令？
	* 进程方面：时钟中断
	* 虚存方面：TLB，异常（TLB fault, page fault, ...）
	* 文件方面：存储介质（硬盘等），相应的I/O系统（中断/DMA/通道/外围处理机……）
	* 特权指令：操作中断mask，填充TLB项，I/O指令

- 你理解的x86的实模式和保护模式有什么区别？物理地址、线性地址、逻辑地址的含义分别是什么？
	
	区别：
	1. 寻址空间1M vs 4G；
	2. 保护模式引入内存分页机制，提供对虚拟内存以及优先级的支持
	
	逻辑地址：（应用）程序员眼中的连续内存空间
	线性地址：逻辑地址经过段式内存管理形成的地址空间	
	物理地址：访问内存硬件的真实地址，等于线性地址经页表变换的值（如果启动分页机制）或线性地址（如果不启动分页机制）

- 你理解的RV的特权模式有什么区别？不同 模式在地址访问方面有何特征？
	
	RISC-V 定义了3种工作模式/特权模式
	* Machine Mode (M Mode) 
	* Supervisor Mode (S Mode)
	* User Mode (U Mode)
	
	其中M Mode是必选的，其他2种可选。M Mode 优先级最高，U Mode 最低。U Mode、S Mode分别预设给一般用户程序和OS程序。M Mode提供了不受限制的对机器的访问。每个模式提供一些ISA的扩展，例如M Mode支持若干种地址转换和内存保护的不同标准，S Mode可以选择支持Type-2 hypervisor execution (hypervisor指RISC-V上运行多个虚拟机时每个OS底层的SBI (Supervisor Binary Interface)之下这一层，见[https://riscv.org/specifications/privileged-isa/](https://riscv.org/specifications/privileged-isa/) 1.2节).

- 理解list_entry双向链表数据结构及其4个基本操作函数和ucore中一些基于它的代码实现（此题不用填写内容）

- 对于如下的代码段，请说明":"后面的数字是什么含义

		/* Gate descriptors for interrupts and traps */
		struct gatedesc {
			unsigned gd_off_15_0 : 16;        // low 16 bits of offset in segment
			unsigned gd_ss : 16;            // segment selector
			unsigned gd_args : 5;            // # args, 0 for interrupt/trap gates
			unsigned gd_rsv1 : 3;            // reserved(should be zero I guess)
			unsigned gd_type : 4;            // type(STS_{TG,IG32,TG32})
			unsigned gd_s : 1;                // must be 0 (system)
			unsigned gd_dpl : 2;            // descriptor(meaning new) privilege level
			unsigned gd_p : 1;                // Present
			unsigned gd_off_31_16 : 16;        // high bits of offset in segment
		};
	
	
	位字段，编译器将其作为一个n位的无符号整数处理

- 对于如下的代码段，

		#define SETGATE(gate, istrap, sel, off, dpl) {            \
		    (gate).gd_off_15_0 = (uint32_t)(off) & 0xffff;        \
		    (gate).gd_ss = (sel);                                \
		    (gate).gd_args = 0;                                    \
		    (gate).gd_rsv1 = 0;                                    \
		    (gate).gd_type = (istrap) ? STS_TG32 : STS_IG32;    \
		    (gate).gd_s = 0;                                    \
		    (gate).gd_dpl = (dpl);                                \
		    (gate).gd_p = 1;                                    \
		    (gate).gd_off_31_16 = (uint32_t)(off) >> 16;        \
		}

	如果在其他代码段中有如下语句，

		unsigned intr;
		intr=8;
		SETGATE(intr, 1,2,3,0);

	请问执行上述指令后， intr的值是多少？
	
	假设
	
	1. 小端序
	2. 未引发UB（从C的角度来看，对超出intr所占32位的访问是未定义的）
	3. 最后一行改成`SETGATE((struct gatedesc) insr), 1, 2, 3, 0)`，否则会报错。
	
	instr = 0x2,0003

### 课堂实践练习

#### 练习一

请在ucore中找一段你认为难度适当的AT&T格式X86汇编代码，尝试解释其含义。

	/* *
	 * test_bit - Determine whether a bit is set
	 * @nr:     the bit to test
	 * @addr:   the address to count from
	 * */
	static inline bool
	test_bit(int nr, volatile void *addr) {
	    int oldbit;
	    asm volatile ("btl %2, %1; sbbl %0,%0" : "=r" (oldbit) : "m" (*(volatile long *)addr), "Ir" (nr));
	    return oldbit != 0;
	}

* bt: bit test, 会改变标志位CF
* sbb: subtraction with borrow，一般用于长于机器字长的整数减法
* GCC inline assembly
	* r: 动态分配的寄存器（eax, ebx, ecx, edx）
	* m: 内存
	* I: 常数（0-31）

如果指定位不为0，则CF=1，SBB使得oldbit=-1；否则oldbit=0。因此返回`oldbit != 0`.
	

  - [Intel格式和AT&T格式汇编区别](http://www.cnblogs.com/hdk1993/p/4820353.html)

  - ##### [x86汇编指令集  ](http://hiyyp1234.blog.163.com/blog/static/67786373200981811422948/)

  - ##### [PC Assembly Language, Paul A. Carter, November 2003.](https://pdos.csail.mit.edu/6.828/2016/readings/pcasm-book.pdf)

  - ##### [*Intel 80386 Programmer's Reference Manual*, 1987](https://pdos.csail.mit.edu/6.828/2016/readings/i386/toc.htm)

  - ##### [[IA-32 Intel Architecture Software Developer's Manuals](http://www.intel.com/content/www/us/en/processors/architectures-software-developer-manuals.html)]


请在rcore中找一段你认为难度适当的RV汇编代码，尝试解释其含义。

kernel/src/arch/x86_64/interrupt/trapframe::Context::switch

	impl Context {
	    /// Switch to another kernel thread.
	    ///
	    /// Defined in `trap.asm`.
	    ///
	    /// Push all callee-saved registers at the current kernel stack.
	    /// Store current rsp, switch to target.
	    /// Pop all callee-saved registers, then return to the target.
	    #[naked]
	    #[inline(never)]
	    pub unsafe extern fn switch(&mut self, _target: &mut Self) {
	        asm!(
	        "
	        // push rip (by caller)
	        // Save old callee-save registers
	        push rbx
	        push rbp
	        push r12
	        push r13
	        push r14
	        push r15
	        mov r15, cr3
	        push r15
	        // Switch stacks
	        mov [rdi], rsp      // rdi = from_rsp
	        mov rsp, [rsi]      // rsi = to_rsp
	        // Save old callee-save registers
	        pop r15
	        mov cr3, r15
	        pop r15
	        pop r14
	        pop r13
	        pop r12
	        pop rbp
	        pop rbx
	        // pop rip
	        ret"
	        : : : : "intel" "volatile" )
	    }

此处用的是Intel汇编语法。首先将所有callee-saved寄存器压栈，将旧rsp保存到[rdi]；栈段切换到[rsi]，将此处存储的callee-saved寄存器恢复，最后ret在切换后的栈段继续执行。


#### 练习二

宏定义和引用在内核代码中很常用。请枚举ucore或rcore中宏定义的用途，并举例描述其含义。

 * 利用宏进行复杂数据结构中的数据访问
	 * 一个例子是va\_list, va\_start, va\_arg, va\_end（C标准库和ucore中都有实现，后者使用gcc built-in实现）。一个利用va_list计算若干个int和的函数如下。

			int sum(int num_args, ...) {
			   int val = 0;
			   va_list ap;
			   int i;
			
			   va_start(ap, num_args);
			   for(i = 0; i < num_args; i++) {
			      val += va_arg(ap, int);
			   }
			   va_end(ap);
			 
			   return val;
			}
	 
 * 利用宏进行数据类型转换；如 to_struct
	 * 这有时候是无法用其他方式替代的，如to_struct和offsetof只能是宏
	 * offsetof(type, member) 得到struct type中member的offset
	 * to_struct(ptr, type, member)通过对应于struct type::member的地址ptr计算对应struct type的地址
	
 * 常用功能的代码片段优化；如  ROUNDDOWN, SetPageDirty
	 * 实际上可以且最好用inline function代替。
	 * kern/libs/defs.h::ROUNDOWN(a, n) 即floor(a, n)。有意思的是实现中使用了GCC的extension typeof，跟C++的decltype差不多。
	 * kern/mm/memlayot.h::SetPageReserved(page) 调用libs/atomic.h::set_bit将Page::flags第1位设为1。


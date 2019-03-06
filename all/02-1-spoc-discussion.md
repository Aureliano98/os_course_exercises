# lec 3 SPOC Discussion

## **提前准备**
（请在上课前完成）


 - 完成lec3的视频学习和提交对应的在线练习
 - git pull ucore_os_lab, v9_cpu, os_course_spoc_exercises  　in github repos。这样可以在本机上完成课堂练习。
 - 仔细观察自己使用的计算机的启动过程和linux/ucore操作系统运行后的情况。搜索“80386　开机　启动”
 - 了解控制流，异常控制流，函数调用,中断，异常(故障)，系统调用（陷阱）,切换，用户态（用户模式），内核态（内核模式）等基本概念。思考一下这些基本概念在linux, ucore, v9-cpu中的os*.c中是如何具体体现的。
 - 思考为什么操作系统需要处理中断，异常，系统调用。这些是必须要有的吗？有哪些好处？有哪些不好的地方？
 - 了解在PC机上有啥中断和异常。搜索“80386　中断　异常”
 - 安装好ucore实验环境，能够编译运行lab8的answer
 - 了解Linux和ucore有哪些系统调用。搜索“linux 系统调用", 搜索lab8中的syscall关键字相关内容。在linux下执行命令: ```man syscalls```
 - 会使用linux中的命令:objdump，nm，file, strace，man, 了解这些命令的用途。
 - 了解如何OS是如何实现中断，异常，或系统调用的。会使用v9-cpu的dis,xc, xem命令（包括启动参数），分析v9-cpu中的os0.c, os2.c，了解与异常，中断，系统调用相关的os设计实现。阅读v9-cpu中的cpu.md文档，了解汇编指令的类型和含义等，了解v9-cpu的细节。
 - 在piazza上就lec3学习中不理解问题进行提问。

## 第三讲 启动、中断、异常和系统调用-思考题

## 3.1 BIOS
-  请描述在“计算机组成原理课”上，同学们做的MIPS CPU是从按复位键开始到可以接收按键输入之间的启动过程。
	
	首先要RAM中要加载kernel程序，可以事先用工具直接加载，或者从Flash中加载。如果是后者，一般是用硬件逻辑单独写一段程序。加载完后PC跳转到第一条指令地址，开始运行监控程序。监控程序设置寄存器值，设置堆栈空间，初始化串口，然后以轮询的方式检查串口是否有数据（由于PS2键盘与32位板不兼容，串口和板上按键应该是32位板唯二的输入方式）。

-  x86中BIOS从磁盘读入的第一个扇区是是什么内容？为什么没有直接读入操作系统内核映像？
	
	主引导扇区（主引导记录，MBR）。首先，为了适应不同文件系统，需要一个加载程序；其二，在多分区的情况下为了能够选择从哪个分区启动，需要主引导记录。

- 比较UEFI和BIOS的区别。

	UEFI是BIOS的替代方案，根据2018spring-answer的总结有三大优势：安全性更强，启动配置更灵活，支持容量更大。

	BIOS和不使用Secure Boot的UEFI的核心启动过程如下。

	- Boot Process under BIOS
		1. System switched on - Power On Self Test, or POST process
		2. After POST BIOS initializes the necessary system hardware for booting (disk, keyboard controllers etc.)
		3. BIOS launches the first 440 bytes (MBR boot code region) of the first disk in the BIOS disk order
		4. The MBR boot code then takes control from BIOS and launches its next stage code (if any) (mostly bootloader code)
		5. The launched (2nd stage) code (actual bootloader) then reads its support and config files
		6. Based on the data in its config files, the bootloader loads the kernel and initramfs into system memory (RAM) and launches the kernel
		
	- Boot Process under UEFI
		1. System switched on - Power On Self Test, or POST process.
		2. UEFI firmware is loaded. Firmware initializes the hardware required for booting.
		3. Firmware then reads its Boot Manager data to determine which UEFI application to be launched and from where (i.e. from which disk and partition).
		4. Firmware then launches the UEFI application as defined in the boot entry in the firmware's boot manager.
		5. The launched UEFI application may launch another application (in case of UEFI Shell or a boot manager like rEFInd) or the kernel and initramfs (in case of a bootloader like GRUB) depending on how the UEFI application was configured.

- 理解rcore中的Berkeley BootLoader (BBL)的功能。
	- 自检，包括检查外设
	- 启动物理内存保护机制
	- 加载并运行OS

## 3.2 系统启动流程

- x86中分区引导扇区的结束标志是什么？
	
	0X55aa

- x86中在UEFI中的可信启动有什么作用？
	
	Secure Boot核心职能是利用数字签名来确认EFI驱动程序或者应用程序是否是受信任的，UEFI只启动通过认证的OS loader。

- RV中BBL的启动过程大致包括哪些内容？
	
	见3.1最后一问。

## 3.3 中断、异常和系统调用比较
- 什么是中断、异常和系统调用？
	* （硬）中断：外设发出信号，例如键盘被按下或松开；异步，发生时间不可预知
	* 异常：应用程序意想不到的行为，例如0作除数；同步，只可能在特定指令发生
	* 系统调用：应用程序主动请求操作提供服务，例如x86中int $0x80和syscall（二者的系统调用编号不同）；同步或异步，此处意思应该和中断、异常的有所不同，类似I/O操作中非异步I/O（阻塞 / 非阻塞 / 多路复用 / 信号驱动）与异步I/O的区别
	
- 中断、异常和系统调用的处理流程有什么异同？

	* 相同点
	
		三者整体过程都是保留现场（可能需要开关中断） > 跳转到处理例程 > 恢复现场 > 返回，需要切换到内核态，但处理例程不同，且处理例程并不一定在这个处理流程中就把事情做完（异步的系统调用）。
	
	* 不同点
		1. 处理例程不同
			* （硬）中断：根据特定设备驱动访问外部设备
			* 异常：根据异常种类作处理，可能杀死进程 / 忽略等
			* 系统调用：根据系统调用编号查系统调用表，跳转执行之
		2. 同步/异步
			（硬）中断异步，异常同步，系统调用同步/异步

- 以ucore/rcore lab8的answer为例，ucore的系统调用有哪些？大致的功能分类有哪些？

	有22个系统调用（如下），大致分为进程管理、文件操作、内存管理、外设输出几类。

		SYS_exit             
		SYS_fork             
		SYS_wait             
		SYS_exec             
		SYS_yield            
		SYS_kill             
		SYS_getpid           
		SYS_putc             
		SYS_pgdir            
		SYS_gettime          
		SYS_lab6_set_priority
		SYS_sleep            
		SYS_open             
		SYS_close            
		SYS_read             
		SYS_write            
		SYS_seek             
		SYS_fstat            
		SYS_fsync            
		SYS_getcwd           
		SYS_getdirentry      
		SYS_dup              

## 3.4 linux系统调用分析
- 通过分析[lab1_ex0](https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab1/lab1-ex0.md)了解Linux应用的系统调用编写和含义。(仅实践，不用回答)
- 通过调试[lab1_ex1](https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab1/lab1-ex1.md)了解Linux应用的系统调用执行过程。(仅实践，不用回答)


## 3.5 ucore/rcore系统调用分析 （扩展练习，可选）
-  基于实验八的代码分析ucore的系统调用实现，说明指定系统调用的参数和返回值的传递方式和存放位置信息，以及内核中的系统调用功能实现函数。
- 以ucore/rcore lab8的answer为例，分析ucore 应用的系统调用编写和含义。
- 以ucore/rcore lab8的answer为例，尝试修改并运行ucore OS kernel代码，使其具有类似Linux应用工具`strace`的功能，即能够显示出应用程序发出的系统调用，从而可以分析ucore应用的系统调用执行过程。

 
## 3.6 请分析函数调用和系统调用的区别
- 系统调用与函数调用的区别是什么？
	- 函数调用：无须状态切换；传参遵循ABI规范；使用call, ret
	- 系统调用：状态切换，保存、恢复现场等；传参遵循系统调用规范；使用int, iret
	
- 通过分析x86中函数调用规范以及`int`、`iret`、`call`和`ret`的指令准确功能和调用代码，比较x86中函数调用与系统调用的堆栈操作有什么不同？
	- int x: 0 <= 0 <= 255, 产生"软中断"(software interrupt)；该指令将FLAGS寄存器压栈。`int 0x80`是系统调用的老方法。
	- iret: 返回int指令的下一条地址，并弹栈恢复FLAGS寄存器
	- call funct: push (next instruction); rip += offset
	- ret: pop rip
	
	注
	* 32位中有far call, far ret, 会将段寄存器也压栈
	* call, ret有带调用参数的版本，此处略

- 通过分析RV中函数调用规范以及`ecall`、`eret`、`jal`和`jalr`的指令准确功能和调用代码，比较x86中函数调用与系统调用的堆栈操作有什么不同？
	- jal (jump and link) J型指令 rd = pc + 4, pc += offset
	- jalr (jump and link register) I型指令 rd = pc + 4, pc = (rs1 + imm[11:0]) & (~1)
	- ecall 引发系统调用，CSRs记录PC, cause等
	- mret / uret (应该是这个？手册里没查到eret) 返回至U mode

			J型指令
			imm[20] 	imm[10:1]	imm[11]		imm[19:12] 	rd 			opcode
			1			10			1			8			5			7
		
			I型指令
			imm[11:0]	rs1			func3		rd			opcode
			12			5			3			5			7

	x86中call ret int iret都涉及堆栈操作，RV中都不涉及（类似MIPS）。


## 课堂实践 （在课堂上根据老师安排完成，课后不用做）
### 练习一
通过静态代码分析，举例描述ucore/rcore键盘输入中断的响应过程。

### 练习二
通过静态代码分析，举例描述ucore/rcore系统调用过程，及调用参数和返回值的传递方法。

# lec6 SPOC思考题


NOTICE
- 有"w3l2"标记的题是助教要提交到学堂在线上的。
- 有"w3l2"和"spoc"标记的题是要求拿清华学分的同学要在实体课上完成，并按时提交到学生对应的git repo上。
- 有"hard"标记的题有一定难度，鼓励实现。
- 有"easy"标记的题很容易实现，鼓励实现。
- 有"midd"标记的题是一般水平，鼓励实现。

## 与视频相关思考题

### 6.1	非连续内存分配的需求背景
 1. 为什么要设计非连续内存分配机制？

	连续内存分配有碎片、内存利用率较低，内存分配动态修改困难；非连续内存分配能提高内存空间利用效率和管理灵活性

 1. 非连续内存分配中内存分块大小有哪些可能的选择？大小与大小是否可变?
	
	* 段式存储管理（大，可变大小）
	* 页式存储管理（小，固定大小）

 1. 为什么在大块时要设计大小可变，而在小块时要设计成固定大小？小块时的固定大小可以提供多种选择吗？
	
	大块设计成可变大小可提高灵活性，减少内碎片；小块设计成固定大小可以简化实现、提高效率。你想要当然可以。

### 6.2	段式存储管理
 1. 什么是段、段基址和段内偏移？
 
	* 段：访问方式和存储数据等属性相同的一段地址空间
	* 段基址：段地址空间开始为止
	* 段内偏移：相对段基址的偏移量

 1. 段式存储管理机制的地址转换流程是什么？为什么在段式存储管理中，各段的存储位置可以不连续？这种做法有什么好处和麻烦？

	1. 硬件得到逻辑地址(短号, 段内偏移)
	2. 硬件查找段表，通过段号查找段长度和段基址
	3. 硬件比较段内偏移与段长度，若越界则产生内存异常
	4. 硬件将段基址与段内偏移相加，得到线性地址

	各段的存储位置可以不连续，因为可以自由设置设置段表各项基址和段长度。

	* 优点：更细粒度和灵活的分离与共享
	* 缺点：增加软硬件复杂性

### 6.3	页式存储管理
 1. 什么是页（page）、帧（frame）、页表（page table）、存储管理单元（MMU）、快表（TLB, Translation Lookaside Buffer）和高速缓存（cache）？

	 * 页：虚拟页面
	 * 帧：物理页面
	 * 页表：内存中将虚页号转化为物理页号的数据结构
	 * MMU：负责处理CPU的内存访问请求的计算机硬件。它的功能包括虚拟内存管理、内存保护、Cache控制，在较为简单的计算机体系结构中，负责总线的仲裁以及存储体切换（bank switching，尤其是在8位的系统上）。（[https://zh.wikipedia.org/wiki/%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86%E5%8D%95%E5%85%83](https://zh.wikipedia.org/wiki/%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86%E5%8D%95%E5%85%83)）
	 * TLB：页表的缓存，加快地址转换速度
	 * Cache：小而快的存储器，作为主存的缓冲，加快访存速度
	 
 1. 页式存储管理机制的地址转换流程是什么？为什么在页式存储管理中，各页的存储位置可以不连续？这种做法有什么好处和麻烦？

	 1. 硬件得到逻辑地址（虚页号，页内偏移）
	 2. 如果有TLB，硬件用虚页号查找实页号，若查到跳转到4，否则引发TLB fault，exception handler查找页表并填充TLB；查到了也可能因为保护等原因引发异常
	 3. 硬件用虚页号查找页表，以某种方式得到实页号，具体方式随单级页表 / 多级页表 / 页寄存器 / 反置页表有所不同；有可能因为保护等原因引发异常
	 4. 硬件将实页号与页内偏移拼接得到物理地址

	各页的存储位置可以不连续，因为可以自由设置设置页表各项的实页号

	* 优点：更细粒度和灵活的分离与共享
	* 缺点：增加软硬件复杂性；可能降低速度

### 6.4	页表概述
 1. 每个页表项有些什么内容？有哪些标志位？它们起什么作用？

 	* 实页号 / 帧号
	* 标志位
		* 存在位：该页表项是否有效
		* 修改位：是否修改过该页中的内容（与cache一致性有关）
		* 引用位：过去一段时间是否对该页表项有引用，即是否有访问过页面中一个存储单元（与cache一致性有关）
		
	（实际上X86有更多标志位）
	
 1. 页表大小受哪些因素影响？

 	只讨论单级页表。

	页表占用空间 = 进程数 * (逻辑地址空间 / 页面大小) * 页表项大小
	页表大小 >= log2(页面大小) + 标志位大小

### 6.5	快表和多级页表
 1. 快表（TLB）与高速缓存（cache）有什么不同？
 	
	* TLB: 页表的缓存
 	* Cache: 主存（或者下一级cache）的缓存
 	
 1. 为什么快表中查找物理地址的速度非常快？它是如何实现的？为什么它的的容量很小？
 	
	TLB通常是全相连或多路组相连结构，每路中通过一个index索引（如果全相连就没有index），每一路选出项的tag与给出的tag比较（还要结合有效位等）。TLB各路之间可以并行查找，速度很快；但成本高，容量很小。

 1. 什么是多级页表？多级页表中的地址转换流程是什么？多级页表有什么好处和麻烦？

	* 优点：减少页表空间（尤其是虚拟地址空间很大的时候；必要条件是并非所有虚拟页面都存在时）
	* 缺点：查找页表更加复杂且需要更多次访存

### 6.6	反置页表
 1. 页寄存器机制的地址转换流程是什么？
	 
	* 虚拟地址
	* 计算页号hash值
	* 用hash值为索引查相应页寄存器，若不匹配则遍历查找
	* 若未查找到，产生异常

 1. 反置页表机制的地址转换流程是什么？
	 
 	与页寄存器基本相同，但是页表项目中记录PID；在hash表中查找时将PID和虚页号一起hash，判等的时候PID，帧号都要相等。另外课件上反置业表项中含next项，不匹配可以按照next项查找而不是遍历。

 1. 反置页表项有些什么内容？
 	
	PID，虚拟页号，标志位，下一条查找的反置业表索引

### 6.7	段页式存储管理
 1. 段页式存储管理机制的地址转换流程是什么？这种做法有什么好处和麻烦？
 	
	先用段表变换得到线性地址，再用页表变换得到物理地址。
	优点：结合段式存储在内存保护和页式存储在内存利用和优化转移到后备存储方面的优势
	缺点：复杂，可能慢

 1. 如何实现基于段式存储管理的内存共享？

 	不同进程的段对应相同的物理页面

 1. 如何实现基于页式存储管理的内存共享？

 	不同进程的虚拟页面指向相同的物理页面

## 个人思考题
（1） (w3l2) 请简要分析64bit CPU体系结构下的分页机制是如何实现的
		
	实际逻辑地址大小为2**48B。

	定义了3种页转换模型：4K页面，2M页面，1G页面。PC上通常使用4K页面，此时使用4级页表结构。

	最大物理地址Intel用MAXPHYADDR来表示，PC上通常为36位，可寻址64G空间。此时上一级table entry的12~35位提供下一级table物理基地址的高24位，此时36~51是保留位，必须置0，低12位补零，达到基地址在4K边界对齐。最后加上12位偏移量得36位物理地址。

## 小组思考题
（1）(spoc) 某系统使用请求分页存储管理，若页在内存中，满足一个内存请求需要150ns (10^-9s)。若缺页率是10%，为使有效访问时间达到0.5us(10^-6s),求不在内存的页面的平均访问时间。请给出计算步骤。
	
	0.9t + 0.1 * 150ns = 0.5us
	t = 538.9ns

（2）(spoc) 有一台假想的计算机，页大小（page size）为32 Bytes，支持32KB的虚拟地址空间（virtual address space）,有4KB的物理内存空间（physical memory），采用二级页表，一个页目录项（page directory entry ，PDE）大小为1 Byte,一个页表项（page-table entries
PTEs）大小为1 Byte，1个页目录表大小为32 Bytes，1个页表大小为32 Bytes。页目录基址寄存器（page directory base register，PDBR）保存了页目录表的物理地址（按页对齐）。

PTE格式（8 bit） :
```
  VALID | PFN6 ... PFN0
```
PDE格式（8 bit） :
```
  VALID | PT6 ... PT0
```
其
```
VALID==1表示，表示映射存在；VALID==0表示，表示映射不存在。
PFN6..0:页帧号
PT6..0:页表的物理基址>>5
```
在[物理内存模拟数据文件](./03-2-spoc-testdata.md)中，给出了4KB物理内存空间的值，请回答下列虚地址是否有合法对应的物理内存，请给出对应的pde index, pde contents, pte index, pte contents。
```
1) Virtual Address 6c74
   Virtual Address 6b22
2) Virtual Address 03df
   Virtual Address 69dc
3) Virtual Address 317a
   Virtual Address 4546
4) Virtual Address 2c03
   Virtual Address 7fd7
5) Virtual Address 390e
   Virtual Address 748b
```

比如答案可以如下表示： (注意：下面的结果是错的，你需要关注的是如何表示)

	Virtual Address 7570:
	  --> pde index:0x1d  pde contents:(valid 1, pfn 0x33)
	    --> pte index:0xb  pte contents:(valid 0, pfn 0x7f)
	      --> Fault (page table entry not valid)
	
	Virtual Address 21e1:
	  --> pde index:0x8  pde contents:(valid 0, pfn 0x7f)
	      --> Fault (page directory entry not valid)
	
	Virtual Address 7268:
	  --> pde index:0x1c  pde contents:(valid 1, pfn 0x5e)
	    --> pte index:0x13  pte contents:(valid 1, pfn 0x65)
	      --> Translates to Physical Address 0xca8 --> Value: 16
答：
	
	Virtual Address: 0x6c74
	  --> pde index: 0x1b  pde contents: (valid 1, pfn 0x20)
	    --> pte index: 0x3  pte contents: (valid 1, pfn 0x61)
	      --> Translates to Physical Address 0xc34 --> Value: 0x6
	Virtual Address: 0x6b22
	  --> pde index: 0x1a  pde contents: (valid 1, pfn 0x52)
	    --> pte index: 0x19  pte contents: (valid 1, pfn 0x47)
	      --> Translates to Physical Address 0x8e2 --> Value: 0x1a
	Virtual Address: 0x3df
	  --> pde index: 0x0  pde contents: (valid 1, pfn 0x5a)
	    --> pte index: 0x1e  pte contents: (valid 1, pfn 0x5)
	      --> Translates to Physical Address 0xbf --> Value: 0xf
	Virtual Address: 0x69dc
	  --> pde index: 0x1a  pde contents: (valid 1, pfn 0x52)
	    --> pte index: 0xe  pte contents: (valid 0, pfn 0x7f)
	      --> Fault (page table entry not valid)
	Virtual Address: 0x317a
	  --> pde index: 0xc  pde contents: (valid 1, pfn 0x18)
	    --> pte index: 0xb  pte contents: (valid 1, pfn 0x35)
	      --> Translates to Physical Address 0x6ba --> Value: 0x1e
	Virtual Address: 0x4546
	  --> pde index: 0x11  pde contents: (valid 1, pfn 0x21)
	    --> pte index: 0xa  pte contents: (valid 0, pfn 0x7f)
	      --> Fault (page table entry not valid)
	Virtual Address: 0x2c03
	  --> pde index: 0xb  pde contents: (valid 1, pfn 0x44)
	    --> pte index: 0x0  pte contents: (valid 1, pfn 0x57)
	      --> Translates to Physical Address 0xae3 --> Value: 0x16
	Virtual Address: 0x7fd7
	  --> pde index: 0x1f  pde contents: (valid 1, pfn 0x12)
	    --> pte index: 0x1e  pte contents: (valid 0, pfn 0x7f)
	      --> Fault (page table entry not valid)
	Virtual Address: 0x390e
	  --> pde index: 0xe  pde contents: (valid 0, pfn 0x7f)
	    --> Fault (page directory entry not valid)
	Virtual Address: 0x748b
	  --> pde index: 0x1d  pde contents: (valid 1, pfn 0x0)
	    --> pte index: 0x4  pte contents: (valid 0, pfn 0x7f)
	      --> Fault (page table entry not valid)

[链接](https://piazza.com/class/i5j09fnsl7k5x0?cid=664)有上面链接的参考答案。请比较你的结果与参考答案是否一致。如果不一致，请说明原因。

（3）请基于你对原理课二级页表的理解，并参考Lab2建页表的过程，设计一个应用程序（可基于python、ruby、C、C++、LISP、JavaScript等）可模拟实现(2)题中描述的抽象OS，可正确完成二级页表转换。

见`pt.py`.

[链接](https://piazza.com/class/i5j09fnsl7k5x0?cid=664)有上面链接的参考答案。请比较你的结果与参考答案是否一致。如果不一致，提交你的实现，并说明区别。

（4）假设你有一台支持[反置页表](http://en.wikipedia.org/wiki/Page_table#Inverted_page_table)的机器，请问你如何设计操作系统支持这种类型计算机？请给出设计方案。

 (5)[X86的页面结构](http://os.cs.tsinghua.edu.cn/oscourse/OS2019spring/lecture06)
---

## 扩展思考题

阅读64bit IBM Powerpc CPU架构是如何实现[反置页表](http://en.wikipedia.org/wiki/Page_table#Inverted_page_table)，给出分析报告。


## interactive　understand VM

[Virtual Memory with 256 Bytes of RAM](http://blog.robertelder.org/virtual-memory-with-256-bytes-of-ram/)：这是一个只有256字节内存的一个极小计算机系统。按作者的[特征描述](https://github.com/RobertElderSoftware/recc#what-can-this-project-do)，它具备如下的功能。
 - CPU的实现代码不多于500行；
 - 支持14条指令、进程切换、虚拟存储和中断；
 - 用C实现了一个小的操作系统微内核可以在这个CPU上正常运行；
 - 实现了一个ANSI C89编译器，可生成在该CPU上运行代码；
 - 该编译器支持链接功能；
 - 用C89, Python, Java, Javascript这4种语言实现了该CPU的模拟器；
 - 支持交叉编译；
 - 所有这些只依赖标准C库。
 
针对op-cpu的特征描述，请同学们通过代码阅读和执行对自己有兴趣的部分进行分析，给出你的分析结果和评价。

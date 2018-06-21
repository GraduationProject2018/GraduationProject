# 第一章：目的

分析如今计算机的计算性能发展遇到瓶颈，单机计算已无法满足计算任务的需求，引用大量的论文内容，举例】阐述多机分布式计算的重要意义，描述论文的整体结构

# 第二章：引出问题

阐述以容器为基础的分布式网络架构、单机内部的容器原理的整体思路。需要在此部分表现出对网络、操作系统的深入理解。具体讲模型时，不要提docker，直接讲就行，千万不能变成科普文

# 第三章：详细介绍多主机容器通信的设计原理

是网络层的内容，重点在于网络设计架构

- vlan tag
- vxlan 路由

两种设计方案分开讲，比较各自的特点，体现出在多容器、多网段、多租户的情况下哪一种更适合，阐述选择的理由

# 第四章：详细介绍容器的设计原理

是计算节点层的，重点在于对操作系统、Linux、虚拟化的原理理解

- 虚拟机的原理
- 容器的原

两种设计原理分开讲，比较各自特点与差异，体现出容器的轻量化、一次封装多次部署

# 第五章：总结分析

根据数据对比，体现出以分布式的多容器比传统单机计算更高效，选择此设计方案解决了问题（第一章提出的现状）

数据可以用快排、归并等大数据量的排序算法运行时间来做比较
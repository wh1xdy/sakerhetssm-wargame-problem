endbr64	
pushq	%rbp
movq	%rsp, %rbp
subq	$0x118, %rsp
movabsq	$14323345477806904192, %rax
movabsq	$14330708963063162578, %rdx
movq	%rax, -0x100(%rbp)
movq	%rdx, -0xf8(%rbp)
movabsq	$16345763023791111872, %rax
movabsq	$14905213696712104928, %rdx
movq	%rax, -0xf0(%rbp)
movq	%rdx, -0xe8(%rbp)
movabsq	$16776681305711040465, %rax
movabsq	$15840237238080421588, %rdx
movq	%rax, -0xe0(%rbp)
movq	%rdx, -0xd8(%rbp)
movabsq	$14033176675236632552, %rax
movabsq	$15631117758620099299, %rdx
movq	%rax, -0xd0(%rbp)
movq	%rdx, -0xc8(%rbp)
movl	$0x65b8bcce, -0xc0(%rbp)
movabsq	$0x617373776f72643a, %rax
movabsq	$0x6572207468652070, %rdx
movq	%rax, -0x120(%rbp)
movq	%rdx, -0x118(%rbp)
movl	$0xa456e74, -0x110(%rbp)
movabsq	$0x2816101307120842, %rax
movabsq	$0x1a0306350a0d3137, %rdx
movq	%rax, -0x170(%rbp)
movq	%rdx, -0x168(%rbp)
movabsq	$0x3d33361e38203223, %rax
movabsq	$0x2b04433c221f2d34, %rdx
movq	%rax, -0x160(%rbp)
movq	%rdx, -0x158(%rbp)
movabsq	$0x402e0c210e1b0f25, %rax
movabsq	$0x29270517002a3a2c, %rdx
movq	%rax, -0x150(%rbp)
movq	%rdx, -0x148(%rbp)
movabsq	$0x23b112415413f19, %rax
movabsq	$0x1c091d141830390b, %rdx
movq	%rax, -0x140(%rbp)
movq	%rdx, -0x138(%rbp)
movl	$0x3e012f26, -0x130(%rbp)
movl	$1, %eax
movl	$0x14, %edx
movl	$0, %r10d
movl	$0, %r8d
movl	$0, %r9d
movl	$1, %edi
leaq	-0x120(%rbp), %rcx
movq	%rcx, %rsi
syscall	
movl	$0, %eax
movl	$0x44, %edx
movl	$0, %r10d
movl	$0, %r8d
movl	$0, %r9d
movl	$0, %edi
leaq	-0x60(%rbp), %rcx
movq	%rcx, %rsi
syscall	
movl	$0, -4(%rbp)
jmp	label7
label6:	nop	
movl	-4(%rbp), %eax
cltq	
movzbl	-0x170(%rbp, %rax), %eax
movsbl	%al, %eax
cltq	
movzbl	-0x60(%rbp, %rax), %edx
movl	-4(%rbp), %eax
cltq	
movb	%dl, -0xb0(%rbp, %rax)
addl	$1, -4(%rbp)
label7:	nop	
cmpl	$0x43, -4(%rbp)
jle	label6
movb	$1, -5(%rbp)
movl	$0, -0xc(%rbp)
jmp	label8
label5:	nop	
movl	-0xc(%rbp), %eax
cltq	
movzbl	-0xb0(%rbp, %rax), %eax
movb	%al, -0xd(%rbp)
cmpl	$0x42, -0xc(%rbp)
jg	label9
movl	-0xc(%rbp), %eax
addl	$1, %eax
cltq	
movzbl	-0xb0(%rbp, %rax), %eax
movl	%eax, %edx
movzbl	-0xd(%rbp), %eax
addl	%edx, %eax
movb	%al, -0xd(%rbp)
label9:	nop	
movzbl	-5(%rbp), %edx
movl	-0xc(%rbp), %eax
cltq	
movzbl	-0x100(%rbp, %rax), %eax
cmpb	%al, -0xd(%rbp)
sete	%al
movzbl	%al, %eax
andl	%edx, %eax
testl	%eax, %eax
setne	%al
movb	%al, -5(%rbp)
addl	$1, -0xc(%rbp)
label8:	nop	
cmpl	$0x43, -0xc(%rbp)
jle	label5
movabsq	$0x20726f79616c6521, %rax
movabsq	$0xa566963746f7279, %rdx
movq	%rax, -0x180(%rbp)
movq	%rdx, -0x178(%rbp)
movabsq	$0x6963206661696c21, %rax
movq	%rax, -0x18b(%rbp)
movl	$0xa457069, -0x184(%rbp)
movl	$1, %eax
cmpb	$0, -5(%rbp)
je	label4
movl	$0x10, %edx
jmp	label1
label4:	nop	
movl	$0xb, %edx
label1:	nop	
movl	$0, %r10d
movl	$0, %r8d
movl	$0, %r9d
cmpb	$0, -5(%rbp)
je	label2
leaq	-0x180(%rbp), %rcx
jmp	label3
label2:	nop	
leaq	-0x18b(%rbp), %rcx
label3:	nop	
movl	$1, %edi
movq	%rcx, %rsi
syscall	
movl	$0x3c, %eax
movl	$0, %edx
movl	$0, %r10d
movl	$0, %r8d
movl	$0, %r9d
movl	$0, %ecx
movl	$0, %esi
movl	%ecx, %edi
syscall	
nop	
leave	

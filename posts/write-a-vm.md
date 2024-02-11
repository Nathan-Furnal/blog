---
title: "Writing a virtual machine"
date: 2022-01-26
tags: ["virtualmachine"]
categories: ["C"]
draft: false
---

# Writing a virtual machine

I stumbled upon [a tutorial to write a VM](https://justinmeiners.github.io/lc3-vm/) (virtual machine) some time ago and I
thought it would be interesting to try it for myself. The introduction outlines
a relevant point: creating a VM [introduces more abstraction](https://www.joelonsoftware.com/2002/11/11/the-law-of-leaky-abstractions/) from the machine,
which has a complexity and cognitive cost, borne by the programmer. Yet, writing
this simple virtual machine also lets us take a peek into what a computer does
under the hood as well as build a useful mental model about machines'
internals. You can explore [the version I created here](https://github.com/Nathan-Furnal/small-vm), which I'd like to break
down a bit and jot down what I've learned in the process. I'll give some
technical context first and then write about the design process itself.

As background information for anyone who would like to try to follow the
tutorial, I had written maybe 500-1000 lines of C code and 200 lines of _NASM_
code before this tutorial but a cursory knowledge of C is sufficient to get
started.


## Implementation details

The "Little Computer 3" (LC-3) is a simple machine, it has 2^16 memory
locations, each storing a 16-bit value. There are ten registers total, each
holding 16 bits as well. Among those registers, eight (R0-R7) are general
purpose registers and the last two hold a program counter and the condition
flags, which are holding the next operation's address and a
positive/negative/zero flag, respectively.

There are also two **memory** **mapped** **registers**, only accessible through
writing to their memory but were not implemented, they allow read/write
operations from the keyboard.

Moreover, there are useful routines which are akin to OS system calls, called
_trap_ routines. These are not instructions proper but rather helpful functions
for common tasks or I/O operations.

On the purely coding side, no complex data structure was used, the memory as
well as the registers are stored in arrays and all recurrent names (registers)
or notable values are stored in enumerations. You'll find declarations such as:

```C
/* 65536 memory locations */
uint16_t memory[UINT16_MAX];
```

or,

```C
/* Registers,
 * 8 general purpose (R0-R7)
 * 1 program counter (PC)
 * 1 condition flags (COND)
 */
typedef enum {
  R_R0 = 0,
  R_R1,
  R_R2,
  R_R3,
  R_R4,
  R_R5,
  R_R6,
  R_R7,
  R_PC,
  R_COND,
  R_COUNT
} registers;

/* Number of registers */
uint16_t reg[R_COUNT];
```

To be easily understandable and readable.


## About the process

I thought following the tutorial was straightforward as none of the steps
required deep C knowledge nor data structure knowledge. But I do have a very
mild gripe with the order in which the operations are presented. In the guide,
the main application loop and some of its later used components are presented
early on, which means that a lot of the implementation was not clear to me on a
first read. I prefer learning the building blocks first and then tying
everything together, which is what I tried to do my implementation: lots of
details and comments in the beginning, that wane over time once comprehension
sets in.

On the other hand, I found the steps to be pleasantly hands-on and each
instruction [from the documentation](https://justinmeiners.github.io/lc3-vm/supplies/lc3-isa.pdf) was clear and concise. The tutorial is mute
on how to structure the project or rather, it chooses to have everything into
one source file. It made more sense to me place the enumerations as well as the
relevant (`static`) arrays into a header file and write the implementations into
different source files. Which has the main advantage to only end up with a short
`main.c` file.

```C
#include "vm.h"
#include "utils.h"

int main(int argc, char *argv[]) {
  /* Load arguments */
  if (argc < 2) {
    /* show usage string */
    printf("lc3 [image-file1] ...\n");
    exit(2);
  }

  for (int j = 1; j < argc; ++j) {
    if (!read_image(argv[j])) {
      printf("failed to load image: %s\n", argv[j]);
      exit(1);
    }
  }

  /* Setup, see utils.c */
  signal(SIGINT, handle_interrupt);
  disable_input_buffering();
  /* since exactly one condition flag should be set at any given time, set the Z
     flag */
  reg[R_COND] = FL_ZRO;
  reg[R_PC] = PC_START;
  int running = 1;
  while (running) {
    /* FETCH */
    uint16_t instr = mem_read(reg[R_PC]++);
    uint16_t op = instr >> 12;

    /* OPS */
    switch (op) {
    case OP_ADD:
      op_add(instr);
      break;
    case OP_AND:
      op_and(instr);
      break;
    case OP_NOT:
      op_not(instr);
      break;
    case OP_BR:
      op_br(instr);
      break;
    case OP_JMP:
      op_jmp(instr);
      break;
    case OP_JSR:
      op_jsr(instr);
      break;
    case OP_LD:
      op_ld(instr);
      break;
    case OP_LDI:
      op_ldi(instr);
      break;
    case OP_LDR:
      op_ldr(instr);
      break;
    case OP_LEA:
      op_lea(instr);
      break;
    case OP_ST:
      op_st(instr);
      break;
    case OP_STI:
      op_sti(instr);
      break;
    case OP_STR:
      op_str(instr);
      break;
    case OP_TRAP:
      switch_trap(instr);
      break;
    case OP_RES:
    case OP_RTI:
    default:
      puts("ABORTING...");
      abort();
      break;
    }
  }
  /* See utils.c */
  restore_input_buffering();
  return 0;
}
```

What I also appreciated during the process was the constant use of bit shifting
and bit masking, it forced me to think about the size and memory addresses of
each operation. It is, of course, undesirable in higher abstractions but when
working at the assembly level, it pushes you to engage and think about what an
operation actually does.

Looking at something like the `ADD` operation is probably clearer:

```C
void op_add(uint16_t instr) {
  /* destination register (DR) */
  uint16_t r0 = (instr >> 9) & 0x7; // boolean mask of size 3 (0b0111)
  /* first operand (SR1) */
  uint16_t r1 = (instr >> 6) & 0x7;
  /* whether we are in immediate mode */
  uint16_t imm_flag = (instr >> 5) & 0x1; // boolean mask of size 1 (0b0001)
  if (imm_flag) {
    uint16_t imm5 =
        sign_extend(instr & 0x1F, 5); // boolean mask of size 5 (0b0001 1111)
    reg[r0] = reg[r1] + imm5;
  } else {
    uint16_t r2 = instr & 0x7;
    reg[r0] = reg[r1] + reg[r2];
  }
  update_flags(r0);
}
```

At first, this seemed like a lot of hard-coded values devoid of meaning but it
boils down to bits juggling in the end and after a couple more examples, I was
on my way.

For those familiar with C, this operation (`LDI`) is very close to _pointer_
indirection, for example:

```C
void op_ldi(uint16_t instr) {
  uint16_t r0 = (instr >> 9) & 0x7;
  uint16_t pc_offset = sign_extend(instr & 0x1FF, 9);
  /* add pc_offset to the current PC, look at that memory location to get
     the final address */
  reg[r0] = mem_read(mem_read(reg[R_PC] + pc_offset));
  update_flags(r0);
}
```

All in all, once the shifting and masking is understood, the operations become
easier to read.


## Takeaway

I thought the experience was interesting and the main takeaway here is that I
had to think properly about memory layout and registers use, which I rarely do
when I use low-level languages and never do when I'm writing in higher-level
environments.
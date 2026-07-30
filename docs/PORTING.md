<!-- SPDX-License-Identifier: BSD-3-Clause -->

# MSX port plan

This document defines the initial technical boundary. It will be refined as
the source audit and first executable tests settle the memory layout.

## Preserved baseline

The CP/Mish build places:

| Address | Modules |
| --- | --- |
| `0x0100` | machine boot adapter |
| `0x0200` | `main`, `exec`, `eval`, `fpp`, `sorry`, `cmos` |
| `0x3B00` | `ram` |

`main`, `exec`, `eval`, and `fpp` contain the language core. `cmos.z80`
contains the CP/M-facing operating-system and file layer.
`adm3a/boot.z80` supplies the small machine adapter.

The first milestone is to reproduce this known CP/M baseline with a
standalone, pinned toolchain. CP/Mish used `zmac` and `ld80`, but its
`build.py` imports build helpers outside this extracted directory.

## Platform boundary

The existing machine adapter exports these entry points:

| Entry | Purpose |
| --- | --- |
| `CLRSCN` | clear the display |
| `PUTCSR` | set cursor coordinates |
| `GETCSR` | read cursor coordinates |
| `PUTIME` | set the centisecond clock |
| `GETIME` | read the centisecond clock |
| `GETKEY` | read a key with timeout |
| `BYE` | leave BASIC |

The MSX port will implement those services independently and replace the
CP/M-specific operating-system layer. Console bring-up comes first; storage
commands follow only after the interpreter is stable.

## Planned milestones

1. Pin or build a reproducible `zmac`/`ld80` toolchain and reproduce the
   CP/M image.
2. Audit the core for writes into its code area, absolute-address
   assumptions, interrupt assumptions, and required writable memory.
3. Define a RainBIOS payload descriptor and a testable transfer contract.
4. Implement an MSX1 console adapter using published MSX hardware behaviour
   and independently written code.
5. Boot to the BBC BASIC prompt, exercise editing, integer and floating-point
   expressions, and run a bundled example.
6. Add MSX2 compatibility, storage, clock, and a standalone cartridge
   wrapper.

## Memory strategy under evaluation

The CP/M binary expects a contiguous writable address space beginning near
`0x0100`; an MSX ROM is not writable and MSX slot selection affects which RAM
is visible. The safest initial design is therefore likely a ROM-resident
payload which RainBIOS copies into a selected RAM layout before transferring
control. The exact addresses and minimum RAM requirement will be chosen only
after the write/relocation audit, then captured in an executable memory-map
test.

RainBIOS and standalone cartridge entry may share the interpreter image but
use different launch wrappers.

## Clean implementation policy

The port may use the openly licensed source in this repository and public
MSX hardware/interface documentation. It must not copy source, tables, data,
comments, or disassembly from proprietary MSX BIOS or BASIC implementations.
Compatibility tests should record externally observable inputs and outputs.

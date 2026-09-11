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

The known CP/M baseline is reproducible through the standalone
`tools/build_cpm_baseline.py` driver. With the recorded `zmac` and `ld80`
sources it produces a 15,616-byte image with SHA-256
`8f65a0a83d2231384b5a7f79035c2b97d748d238a924a116a84214c004cbe8f6`.
The tools stay external; see `docs/TOOLCHAIN.md`.

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

1. **Complete:** reproduce and hash the CP/M image with a standalone build
   driver and recorded external tool sources.
2. **Complete:** CP/M calls and mutable adapter state are outside the language
   core; direct core writes target the separate RAM module. A guarded runtime
   trace found zero cartridge writes in the P1 test suite.
3. **Complete:** define a RainBIOS payload descriptor and a testable transfer
   contract.
4. **Complete:** implement an MSX1 console adapter using published MSX
   interfaces and independently written code.
5. **Complete:** boot to the BBC BASIC prompt; exercise editing, integer and
   floating-point expressions, strings, a stored program, error reporting,
   the clock, and timed keyboard input.
6. **Graphics, cassette, floppy-program, media, and MSX2 slices complete:**
   the MSX1 graphics subset, sequential tape storage, RainBIOS FAT12 program
   SAVE/LOAD and `*CAT`/`*DIR` with free-space reporting, PSG sound/envelope
   approximation, controller reads, Screen 2 sprites, and MSX2 Screens 5-8
   are tested with openMSX and 1983. Random-access storage and a RainBIOS
   return contract remain later work.

## Initial memory strategy

The relocatable language core occupies 12,492 bytes. The CP/M operating-system
layer adds 2,081 bytes and the fixed RAM module is 768 bytes. Static analysis
found no reserved storage, CP/M calls, or interrupt-control instructions in
the core, and every direct write to a symbolic address targets an export from
`ram.z80`. The only direct I/O instructions implement BBC BASIC's user-facing
`INP` and `OUT` features.

That makes a 16 KiB ROM-resident core and platform adapter plausible. The
initial MSX build will target:

- payload ROM in page 1 (`4000h-7FFFh`);
- aligned BBC state at `8000h-82FFh`;
- adapter state at `8300h-833Dh` and program/dynamic memory beginning at
  `833Eh`, ending below `E6E0h` so RainBIOS can reserve a guard, a FAT12
  workspace through `EFFFh`, and disk-system state at `F000h-F2FFh`;
- initialized RAM in pages 2 and 3, requiring at least 32 KiB for the first
  supported profile.

This is now the tested P1 memory profile, not yet a broad compatibility
guarantee. The openMSX smoke test watches the cartridge ROM, boots to a prompt,
exercises expressions, editing, program flow, errors, time, and keyboard
timeouts, and fails on any attempted write. The independent 1983 test confirms
that the final ROM visibly renders the prompt. A second program exercises
Graphics II mode selection, colour selection, moves, lines, absolute plotting,
and pixel readback. A third program exercises absolute `PLOT 85` and relative
`PLOT 0` / `PLOT 81` triangles and verifies the filled shape. A cassette
fixture separately loads and runs a tokenized program through the public MSX
tape calls. C-BIOS MSX2 and the 1983 Omega RainBIOS model validate Screens
5-8, high-VRAM pixel access, Screen 6/7 packing, and full-bitmap clearing;
openMSX and 1983 also validate PSG execution and visible Screen 2 sprites.
Arbitrary user machine-code paths still require separate validation.

RainBIOS and standalone cartridge entry can share the interpreter image while
using different launch wrappers.

## Clean implementation policy

The port may use the openly licensed source in this repository and public
MSX hardware/interface documentation. It must not copy source, tables, data,
comments, or disassembly from proprietary MSX BIOS or BASIC implementations.
Compatibility tests should record externally observable inputs and outputs.

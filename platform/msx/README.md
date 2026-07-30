<!-- SPDX-License-Identifier: BSD-3-Clause -->

# MSX platform adapter

This directory contains independently written MSX and MSX2 platform code.
`cartridge.z80`, `console.z80`, `graphics.z80`, and `state.z80` form the
bootable P1 adapter. `descriptor.z80` adds the RainBIOS payload descriptor at
`7FF0h` without changing the standard cartridge header. `layout_stub.z80`
remains only as the earlier, nonfunctional address-layout proof.

The P1 adapter provides:

- a conventional `AB` cartridge entry at `4010h`;
- startup that initializes the VDP for 40-column text and BIOS-backed
  character output;
- blocking input, line editing, and keyboard polling with centisecond timeout
  semantics;
- cursor position tracking;
- a settable centisecond counter for both 50 Hz and 60 Hz machines;
- Escape polling without consuming ordinary pending keys;
- Graphics II `MODE 2`, text `MODE 7`, `CLG`, `GCOL 0,c`, `MOVE`, `DRAW`,
  absolute `PLOT` modes 4, 5, and 69, and `POINT(x,y)`;
- an explicit `Storage unsupported` error for unimplemented file and OS
  operations.

It calls only published MSX BIOS entries and published work-area variables.
The standalone build currently requires an MSX1-compatible BIOS, at least
32 KiB of initialized RAM, and a normal 16 KiB cartridge mapping:

| Window | Contents |
| --- | --- |
| `4000h-4012h` | cartridge header and entry veneer |
| `4013h-423Ah` | console adapter |
| `4400h-74C1h` | preserved BBC BASIC language core |
| `74C2h-77AAh` | Graphics II adapter and remaining explicit stubs |
| `7FF0h-7FFFh` | RainBIOS payload descriptor v1 |
| `8000h-82FFh` | BBC BASIC fixed RAM |
| `8300h-8311h` | adapter state |
| `8312h-F2FFh` | initial program/dynamic-memory window |

The `JIFFY`-derived clock wraps with the underlying 16-bit BIOS counter in P1.
MSX2 validation, sound, storage, and a RainBIOS return contract remain later
milestones.

The descriptor identifies payload type 1 (BASIC), entry `4010h`, the
`8000h-F2FFh` RAM window, two contiguous RAM pages, and required console,
keyboard, timing, and graphics services. Its 16-byte additive checksum is
zero.

BBC logical coordinates use `0..1279` by `0..1023` with the origin at bottom
left and are scaled to the 256 by 192 display. Logical colours 0 through 7
map to stable TMS9918 palette entries. Graphics II permits only one foreground
colour over the background in each eight-pixel scanline cell, so drawing a new
colour into a previously used cell changes the colour of all set pixels in
that cell. Coordinates outside the logical screen and unsupported raster
operations fail explicitly.

`tools/openmsx_smoke.tcl` boots the ROM, edits a command with Backspace,
exercises integer, floating-point, string, program-flow, error, clock, and
timeout paths, and records any attempted write while the cartridge is
selected. The 1983 check separately confirms that the banner and prompt are
actually rendered, avoiding reliance on openMSX's raw screenshot path.
`tools/openmsx_graphics.tcl` runs `examples/msx-graphics.bbc`, verifies
reference pixels and colours, checks `POINT()` result 7, captures the
Graphics II screen, and retains the same ROM-write guard.

The adapter must be based on published MSX behaviour and original code. It
must not contain code or data copied from a proprietary MSX BIOS, BASIC ROM,
or disassembly.

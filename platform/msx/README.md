<!-- SPDX-License-Identifier: BSD-3-Clause -->

# MSX platform adapter

This directory contains independently written MSX and MSX2 platform code.
`cartridge.z80`, `console.z80`, and `state.z80` form the bootable P1
console adapter. `layout_stub.z80` remains only as the earlier, nonfunctional
address-layout proof.

The P1 adapter provides:

- a conventional `AB` cartridge entry at `4010h`;
- startup that initializes the VDP for 40-column text and BIOS-backed
  character output;
- blocking input, line editing, and keyboard polling with centisecond timeout
  semantics;
- cursor position tracking;
- a settable centisecond counter for both 50 Hz and 60 Hz machines;
- Escape polling without consuming ordinary pending keys;
- an explicit `Storage unsupported` error for unimplemented file and OS
  operations.

It calls only published MSX BIOS entries and published work-area variables.
The standalone build currently requires an MSX1-compatible BIOS, at least
32 KiB of initialized RAM, and a normal 16 KiB cartridge mapping:

| Window | Contents |
| --- | --- |
| `4000h-4012h` | cartridge header and entry veneer |
| `4013h-4230h` | console adapter |
| `4400h-74CBh` | preserved BBC BASIC language core |
| `8000h-82FFh` | BBC BASIC fixed RAM |
| `8300h-8307h` | adapter state |
| `8308h-F2FFh` | initial program/dynamic-memory window |

The `JIFFY`-derived clock wraps with the underlying 16-bit BIOS counter in P1.
MSX2 validation, graphics, sound, storage, and the RainBIOS return/launch
contract remain later milestones.

`tools/openmsx_smoke.tcl` boots the ROM, edits a command with Backspace,
exercises integer, floating-point, string, program-flow, error, clock, and
timeout paths, and records any attempted write while the cartridge is
selected. The 1983 check separately confirms that the banner and prompt are
actually rendered, avoiding reliance on openMSX's raw screenshot path.

The adapter must be based on published MSX behaviour and original code. It
must not contain code or data copied from a proprietary MSX BIOS, BASIC ROM,
or disassembly.

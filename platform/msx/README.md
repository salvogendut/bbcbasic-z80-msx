<!-- SPDX-License-Identifier: BSD-3-Clause -->

# MSX platform adapter

This directory contains independently written MSX and MSX2 platform code.
`cartridge.z80`, `console.z80`, `sprite.z80`, `graphics.z80`, `storage.z80`,
and `state.z80` form the bootable P1 adapter. `sprite.z80` is linked into the
ROM gap between the console adapter and the language core. `descriptor.z80`
adds the RainBIOS payload descriptor at `7FF0h` without changing the standard
cartridge header. `layout_stub.z80` remains only as the earlier, nonfunctional
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
- `MODE n` screen selection for MSX Screen `n`: `MODE 0` text, `MODE 1`
  Graphics I, `MODE 2` Graphics II, `MODE 3` multicolor, and `MODE 5`-`8` the
  MSX2 V9938/V9958 bitmap screens (extended register programming plus the
  default 16-colour palette) plus `CLG`, `GCOL 0,c`, `MOVE`, `DRAW`,
  `POINT(x,y)`, and `PLOT`: lines and pure moves in modes 0-63 (solid for
  0-15, dotted for 16-31, with modes 32-63 rendering dotted in this
  milestone), single points in modes 64-79, and filled triangles in modes
  80-95 using the two most recently visited points; absolute modes set
  mode bit 2 and relative modes are clear;
- `SOUND channel, amplitude, pitch, duration` mapped onto the PSG: channel 0
  drives the noise channel and channels 1-3 drive tone A/B/C, amplitude 0..-15
  maps to the 4-bit volume, pitch 0-255 maps to a linear 12-bit period (a
  logarithmic BBC-pitch approximation), and a positive duration is a
  synchronous JIFFY-timed note that silences the channel afterwards;
- `ADVAL(n)` returning joystick 1/2 direction for `n` 0/2 and trigger state
  for `n` 1/3, a digital approximation of the BBC analogue channels;
- `ENVELOPE` mapping the attack time and rate onto the AY-3-8910 hardware
  envelope (period R11/R12 and shape R13); subsequent `SOUND` notes use the
  hardware envelope, while the full BBC ADSR and pitch sweep are approximated;
- `*SPRITE n,x,y,pattern,colour`, `*SPRITEOFF n`, `*SPRITEPAT n,b0..b7`, and
  `*SPRITECLR` OSCLI commands driving the Screen 2 VDP sprite attribute and
  pattern tables (visible only after `MODE 2`);
- sequential cassette program `SAVE` and `LOAD`, with case-insensitive
  six-character names and the standard MSX binary-tape envelope;
- an explicit `Storage unsupported` error for random-access channels and
  remaining file/OS operations.

It calls only published MSX BIOS entries and published work-area variables.
The standalone build currently requires an MSX1-compatible BIOS, at least
32 KiB of initialized RAM, and a normal 16 KiB cartridge mapping:

| Window | Contents |
| --- | --- |
| `4000h-4012h` | cartridge header and entry veneer |
| `4013h-423Fh` | console adapter |
| `4240h-4345h` | sprite command adapter (`*SPRITE` etc.) |
| `4400h-74C1h` | preserved BBC BASIC language core |
| `74C2h-7D3Fh` | graphics adapter (Graphics I/II, multicolor, sound) |
| `7D40h-7EE3h` | cassette program storage adapter |
| `7FF0h-7FFFh` | RainBIOS payload descriptor v1 |
| `8000h-82FFh` | BBC BASIC fixed RAM |
| `8300h-833Bh` | adapter state and cassette scratch data |
| `833Ch-F2FFh` | initial program/dynamic-memory window |

The `JIFFY`-derived clock wraps with the underlying 16-bit BIOS counter in P1.
The MSX2 bitmap screens (`MODE 5`-`8`) are programmed through the extended VDP
registers and default palette; bitmap clearing and plot/point at the MSX2
resolutions remain later work. Random-access storage and a RainBIOS return
contract are also later milestones.

The descriptor identifies payload type 1 (BASIC), entry `4010h`, the
`8000h-F2FFh` RAM window, two contiguous RAM pages, and required console,
keyboard, timing, graphics, and cassette services. Its 16-byte additive
checksum is zero.

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
reference pixels and colours, checks `POINT()` result 7, then runs a
`drawing-rectangle.bbc` program that exercises absolute `PLOT 85` and
relative `PLOT 0` / `PLOT 81` triangles, verifies the triangle shape and
final cursor history, captures the Graphics II screen, and retains the same
ROM-write guard.

Program tapes contain a long-leader header block (`D0h` repeated ten times
plus a padded six-byte name) and a short-leader data block (start, inclusive
end, zero execute address, and tokenized program bytes). `LOAD` uses the
caller's destination and validates the metadata length against available RAM.
`OPEN`, `BGET`, `BPUT`, `PTR`, and `EXT#` are deliberately not implemented by
this sequential milestone.

The adapter must be based on published MSX behaviour and original code. It
must not contain code or data copied from a proprietary MSX BIOS, BASIC ROM,
or disassembly.

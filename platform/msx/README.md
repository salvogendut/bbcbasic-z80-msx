<!-- SPDX-License-Identifier: BSD-3-Clause -->

# MSX platform adapter

This directory contains independently written MSX and MSX2 platform code.
`cartridge.z80`, `console.z80`, `sprite.z80`, `msx2.z80`, `graphics.z80`,
`storage.z80`, and `state.z80` form the bootable P1 adapter. `sprite.z80` and
`msx2.z80` are linked into the ROM gap between the console adapter and the
language core. `descriptor.z80` adds the RainBIOS payload descriptor at
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
- `MODE n` screen selection for MSX Screen `n`: `MODE 0` text, `MODE 1`
  Graphics I, `MODE 2` Graphics II, `MODE 3` multicolor, and `MODE 5`-`8` the
  MSX2 V9938/V9958 bitmap screens through the published `CHGMOD`/SUB-ROM
  interfaces, plus `CLG`, `GCOL 0,c`, `MOVE`, `DRAW`,
  `POINT(x,y)`, and `PLOT`: lines and pure moves in modes 0-63 (solid for
  0-15, dotted for 16-31, with modes 32-63 rendering dotted in this
  milestone), single points in modes 64-79, and filled triangles in modes
  80-95 using the two most recently visited points; absolute modes set
  mode bit 2 and relative modes are clear;
- `SOUND channel, amplitude, pitch, duration` mapped onto the PSG: channel 0
  drives the noise channel and channels 1-3 drive tone A/B/C, amplitudes
  -15..0 map to fixed 4-bit volume and positive amplitudes select the most
  recently defined envelope, pitch 0-255 maps to a compact octave-linear
  approximation, duration -1 leaves a note playing, and duration 0..254 is a
  synchronous JIFFY-timed note that silences the channel afterwards;
- `ADVAL(n)` returning joystick 1/2 direction for `n` 0/2 and trigger state
  for `n` 1/3, a digital approximation of the BBC analogue channels;
- `ENVELOPE` mapping the attack time and rate onto the AY-3-8910 hardware
  envelope (period R11/R12 and shape R13); a subsequent `SOUND` whose positive
  amplitude selects that envelope retriggers it, while the full BBC ADSR and
  pitch sweep are explicitly approximated;
- `*SPRITE n,x,y,pattern,colour`, `*SPRITEOFF n`, `*SPRITEPAT n,b0..b7`, and
  `*SPRITECLR` OSCLI commands driving the Screen 2 VDP sprite attribute and
  pattern tables (visible only after `MODE 2`);
- sequential cassette program `SAVE` and `LOAD`, with case-insensitive
  six-character names and the standard MSX binary-tape envelope;
- RainBIOS FAT12 program storage selected explicitly by `A:` names, using a
  private versioned bridge while retaining cassette behavior for unprefixed
  names and for standalone use on other firmware;
- RainBIOS drive-A catalogues through the equivalent `*CAT` and `*DIR`
  OSCLI commands, including a FAT-derived `Free: n KiB` summary;
- an explicit `Storage unsupported` error for random-access channels and
  remaining file/OS operations.

It calls only published MSX BIOS entries and published work-area variables.
The standalone build currently requires an MSX1-compatible BIOS, at least
32 KiB of initialized RAM, and a normal 16 KiB cartridge mapping:

| Window | Contents |
| --- | --- |
| `4000h-4012h` | cartridge header and entry veneer |
| `4013h-424Bh` | console adapter |
| `424Ch-4351h` | sprite command adapter (`*SPRITE` etc.) |
| `4352h-43F9h` | MSX2 bitmap pixel adapter |
| `4400h-74C1h` | preserved BBC BASIC language core |
| `74C2h-7E45h` | graphics adapter (Graphics I/II, multicolor, sound) |
| `7E46h-7FEFh` | cassette/RainBIOS program storage adapter |
| `7FF0h-7FFFh` | RainBIOS payload descriptor v1 |
| `8000h-82FFh` | BBC BASIC fixed RAM |
| `8300h-833Dh` | adapter state and cassette scratch data |
| `833Eh-E6DFh` | initial program/dynamic-memory window |
| `E6E0h-E7DFh` | guard between the BASIC stack ceiling and disk transfers |
| `E7E0h-EFFFh` | RainBIOS FAT12 work area |
| `F000h-F2FFh` | disk-system private state (not owned by the payload) |

The `JIFFY`-derived clock wraps with the underlying 16-bit BIOS counter in P1.
The MSX2 bitmap screens (`MODE 5`-`8`) are initialized and fully cleared by
the published main-BIOS `CHGMOD` entry. Pixel access above 16 KiB uses the
published SUB-ROM `WRTVRM`/`RDVRM` entries. `MOVE`/`DRAW`/`PLOT`/`POINT`
support Screen 5 and Screen 7 at 4bpp, Screen 6 at 2bpp, and Screen 8 at 8bpp.
Screens 6 and 7 are 512 pixels wide but currently expose the left 256-pixel
half until a 16-bit X coordinate is introduced. Screen 6 maps logical colours
to its four physical colours. In `MODE 5`-`8` BIOS character output is
suppressed so text cannot corrupt the bitmap. Random-access storage and a
RainBIOS return contract are also later milestones. Sequential FAT12 program
SAVE/LOAD and drive-A catalogues are available through the versioned RainBIOS
bridge.

The descriptor identifies payload type 1 (BASIC), entry `4010h`, the
`8000h-E6DFh` RAM window, two contiguous RAM pages, and required console,
keyboard, timing, graphics, and cassette services. Its 16-byte additive
checksum is zero.

The ordinary cartridge header's six reserved bytes publish three private
pointers used only after the payload has detected RainBIOS: cassette SAVE,
cassette LOAD, and the interpreter's extended-error entry. RainBIOS uses those
pointers to return unprefixed names to the cassette implementation and to
report disk errors without relying on hard-coded payload link addresses. The
adapter checks RainBIOS's complete four-byte signature before calling the
fixed bridge entry; other BIOSes retain cassette behavior and reject the
RainBIOS-only catalogue commands.

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
`tools/openmsx_msx2.tcl` uses the open-source C-BIOS MSX2 machine to verify
all four bitmap modes, raw Screen 6/7 packing, complete `CLG`, and distinct
pixels on opposite sides of the former 16 KiB alias boundary. The matching
1983 tests run on the Omega unified RainBIOS image and also render a hardware
sprite while executing a PSG note.

Program tapes contain a long-leader header block (`D0h` repeated ten times
plus a padded six-byte name) and a short-leader data block (start, inclusive
end, zero execute address, and tokenized program bytes). `LOAD` uses the
caller's destination and validates the metadata length against available RAM.
`OPEN`, `BGET`, `BPUT`, `PTR`, and `EXT#` are deliberately not implemented by
this sequential milestone.

The adapter must be based on published MSX behaviour and original code. It
must not contain code or data copied from a proprietary MSX BIOS, BASIC ROM,
or disassembly.

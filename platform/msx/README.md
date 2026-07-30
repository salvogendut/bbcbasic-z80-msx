<!-- SPDX-License-Identifier: BSD-3-Clause -->

# MSX platform adapter

This directory is reserved for independently written MSX and MSX2 platform
code. No adapter source has been added yet.

The first implementation will provide:

- startup and a defined return path to RainBIOS;
- VDP initialization and text output;
- keyboard polling with centisecond timeout semantics;
- cursor position tracking;
- a monotonic centisecond counter;
- a replacement for the CP/M services currently in `cmos.z80`.

The console-only milestone will deliberately return explicit
"not implemented" errors for storage operations. This keeps the first prompt
and language tests separate from disk and filesystem policy.

The adapter must be based on published MSX behaviour and original code. It
must not contain code or data copied from a proprietary MSX BIOS, BASIC ROM,
or disassembly.

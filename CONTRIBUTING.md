<!-- SPDX-License-Identifier: BSD-3-Clause -->

# Contributing

This project is developing an MSX port of the openly licensed BBC BASIC
(Z80) source in this repository.

## Source and provenance rules

- Do not copy code, tables, comments, or data from proprietary MSX BIOS,
  BASIC, firmware, ROM, or disassembly sources.
- Publicly documented behaviour and hardware interfaces may be studied and
  reimplemented independently.
- Record the public specification, test, or original reasoning behind a new
  compatibility implementation when that provenance is not obvious.
- Keep imported BBC BASIC notices intact. Altered versions of imported files
  must be plainly marked as altered, as required by `COPYING`.
- New, independently written files should carry
  `SPDX-License-Identifier: BSD-3-Clause` unless there is a documented reason
  to use another compatible license.

Tests derived from observed behaviour should describe inputs and outputs,
not reproduce proprietary implementation details.

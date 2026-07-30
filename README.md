<!-- SPDX-License-Identifier: BSD-3-Clause -->

# BBC BASIC for Z80 on MSX

This repository is adapting R. T. Russell's BBC BASIC (Z80) for MSX and
MSX2 computers. The first intended consumer is
[RainBIOS](https://github.com/salvogendut/rainbios), with a standalone
cartridge or ROM payload as a second target.

The port is at the bring-up stage. There is not yet a bootable MSX binary.
The preserved source builds as a generic CP/M program in its original
CP/Mish environment; the MSX console, storage, memory, and startup adapters
still have to be implemented.

## Repository branches

- `upstream` is the BBC BASIC-only history extracted from CP/Mish. Its tip is
  tagged `upstream-cpmish-d70c643`.
- `main` contains the MSX port, tests, documentation, and independently
  written platform code.

See [UPSTREAM.md](UPSTREAM.md) for the exact source revision, tree identity,
and commit mapping. The source tree on `upstream` is byte-for-byte identical
to `third_party/bbcbasic` in the recorded CP/Mish revision.

## Current checks

Run:

```sh
make check
```

This validates the source layout and the preserved upstream history. The
legacy CP/M build requires `zmac` and `ld80`; `make toolcheck` reports whether
they are installed. `build.py` is retained for provenance but depends on
CP/Mish's build helper modules and is not yet a standalone build entry point.

The port plan and platform boundary are documented in
[docs/PORTING.md](docs/PORTING.md) and
[platform/msx/README.md](platform/msx/README.md).

## Licensing

The imported BBC BASIC sources are distributed under the notice in
[COPYING](COPYING). That notice must remain intact, and altered source
versions must be plainly marked as altered.

New, independently written project files use the
[BSD 3-Clause license](LICENSES/BSD-3-Clause.txt), identified with SPDX
headers. The two licenses apply file-by-file; the BSD license does not
replace the imported source notice.

No proprietary MSX BIOS or BASIC code is included or may be copied into this
repository.

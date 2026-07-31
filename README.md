<!-- SPDX-License-Identifier: BSD-3-Clause -->

# BBC BASIC for Z80 on MSX

This repository is adapting R. T. Russell's BBC BASIC (Z80) for MSX and
MSX2 computers. The first intended consumer is
[RainBIOS](https://github.com/salvogendut/rainbios), with a standalone
cartridge or ROM payload as a second target.

The cassette milestone is bootable. It packages the unchanged language
core with an independently written MSX adapter in a deterministic 16 KiB
cartridge ROM. On MSX1 it reaches the interactive prompt, supports line
editing, integer and floating-point expressions, strings, stored programs,
`TIME`, timed `INKEY`, an initial TMS9918 Graphics II subset, and sequential
program `SAVE`/`LOAD` on cassette. Random-access file channels remain future
work and report `Storage unsupported`.

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
legacy CP/M build requires external `zmac` and `ld80` executables. With those
available, reproduce the baseline with:

```sh
make cpm-baseline ZMAC=/path/to/zmac LD80=/path/to/ld80
```

The result is `build/cpm/bbcbasic_adm3a.com`: 15,616 bytes with SHA-256
`8f65a0a83d2231384b5a7f79035c2b97d748d238a924a116a84214c004cbe8f6`.
The build fails if the output differs. [docs/TOOLCHAIN.md](docs/TOOLCHAIN.md)
records the exact tool sources used for this reproduction and an important
licensing caveat about `zmac`.

The imported `build.py` is retained for provenance but depends on CP/Mish's
build helper modules. The new build driver is standalone.

The same external tools can build the nonfunctional MSX layout proof:

```sh
make msx-layout ZMAC=/path/to/zmac LD80=/path/to/ld80
```

`build/msx-layout/bbcbasic_msx_layout.rom` is for address-map testing only. It
must not be distributed or presented as a usable interpreter.

Build the usable cartridge with:

```sh
make msx-console ZMAC=/path/to/zmac LD80=/path/to/ld80
```

The result is `build/msx-console/bbcbasic_msx_console.rom`: 16,384 bytes with
SHA-256
`82b0ff999ae85d4105875ad6e8c5a33f37662fbcde1642044c56a430de9759a6`.
The build validates its link map and fails if the ROM differs.

The final 16 bytes contain RainBIOS payload descriptor v1 while the ordinary
MSX `AB` header and standalone cartridge entry remain unchanged.

The interactive openMSX test checks the displayed results and watches the
selected cartridge window for writes:

```sh
make test-msx-console-openmsx \
  ZMAC=/path/to/zmac LD80=/path/to/ld80
```

Use a normal 16 KiB mapper (`-romtype Normal`) if launching the ROM manually.
The independent rendering check in the sibling 1983 emulator is:

```sh
make test-msx-console-1983 \
  ZMAC=/path/to/zmac LD80=/path/to/ld80
```

The Graphics II test types and runs `examples/msx-graphics.bbc`, checks
`MODE`, `GCOL`, `MOVE`, `DRAW`, `PLOT`, and `POINT`, then runs a
`drawing-rectangle.bbc` program covering absolute and relative `PLOT`
triangles, and guards the cartridge window against writes:

```sh
make test-msx-graphics-openmsx \
    ZMAC=/path/to/zmac LD80=/path/to/ld80
```

The cassette adapter stores a six-character uppercase name in the standard
MSX binary-tape two-block envelope. The sibling RainBIOS suite loads and runs
a tokenized fixture in 1983 and records a real `SAVE` waveform in openMSX.
`tools/make_msx_tape_fixture.py` generates the deterministic load fixture.

These emulator targets are optional integration checks; `make check` needs no
assembler or emulator.

The port plan and platform boundary are documented in
[docs/PORTING.md](docs/PORTING.md) and
[platform/msx/README.md](platform/msx/README.md).
The static interpreter audit and its deliberately limited conclusions are in
[docs/CORE_AUDIT.md](docs/CORE_AUDIT.md). Public compatibility references are
recorded in [docs/REFERENCES.md](docs/REFERENCES.md).

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

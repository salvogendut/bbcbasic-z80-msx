<!-- SPDX-License-Identifier: BSD-3-Clause -->

# BBC BASIC for Z80 on MSX

This repository is adapting R. T. Russell's BBC BASIC (Z80) for MSX and
MSX2 computers. The first intended consumer is
[RainBIOS](https://github.com/salvogendut/rainbios), with a standalone
cartridge or ROM payload as a second target.

The port is at the bring-up stage. There is not yet a bootable MSX binary.
The preserved source now has a standalone, verified build for its generic
CP/M baseline; the MSX console, storage, memory, and startup adapters still
have to be implemented. A deterministic 16 KiB MSX link-layout artifact now
proves the proposed ROM and RAM addresses, but its adapter is deliberately
nonfunctional.

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

The port plan and platform boundary are documented in
[docs/PORTING.md](docs/PORTING.md) and
[platform/msx/README.md](platform/msx/README.md).
The static interpreter audit and its deliberately limited conclusions are in
[docs/CORE_AUDIT.md](docs/CORE_AUDIT.md).

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

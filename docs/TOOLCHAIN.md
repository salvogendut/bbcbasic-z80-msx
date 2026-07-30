<!-- SPDX-License-Identifier: BSD-3-Clause -->

# CP/M baseline toolchain

The CP/M baseline was reproduced on 2026-07-30 from the tool sources bundled
with CP/Mish snapshot
`d70c643a5db24007ad6533f92b701fd714a99b7f`.

## zmac

- reported version: `18oct2022`
- CP/Mish source path: `third_party/zmac`
- source tree object: `670a111cdab9140ee485405bc680c225cf7704a3`
- latest tool-tree commit in that snapshot:
  `f14269e66a38803d7e4ea22532fb2175d61becb2`
- tested compiler: GCC/G++ 16.1.1
- tested parser generator: Bison 3.8.2
- locally built executable SHA-256:
  `2fa92f6d0270e2eceb8c1c6bfeff2bf7266c9d67118462f9021f2f18301a4816`

The historical copyright status of `zmac` is not completely clear.
CP/Mish carries both a waiver from later contributor George Phillips and a
historical `COPYING.publicdomain` discussion which explicitly describes the
uncertainty around older contributions. For that reason this project does not
vendor or redistribute `zmac`, and its hash is recorded only as evidence of
the executable used for the baseline. Contributors must obtain and assess
their build tool independently.

Replacing this baseline dependency with a clearly licensed assembler/linker
path is desirable before a release build depends on it.

## ld80

- CP/Mish source path: `third_party/ld80`
- source tree object: `d844fa8c61cac6c158dd86c167b8faac9929a6a0`
- reported source version: `0.5-dg-1`
- license file: `COPYING` states that the software is in the public domain
- tested compiler: GCC 16.1.1
- locally built executable SHA-256:
  `b31637136a4459589c951aa3cbc83ca9af03241fdab1b773ce67bb6f485319c9`

## Verified output

The standalone driver assembles the same modules and applies the same link
addresses as the preserved CP/Mish `build.py`, then removes the unused first
256 bytes from the linker's absolute image:

| Address | Input |
| --- | --- |
| `0x0100` | `adm3a/boot.z80` |
| `0x0200` | `main`, `exec`, `eval`, `fpp`, `sorry`, `cmos` |
| `0x3B00` | `ram` |

The verified `bbcbasic_adm3a.com` output is 15,616 bytes and has SHA-256:

```text
8f65a0a83d2231384b5a7f79035c2b97d748d238a924a116a84214c004cbe8f6
```

The executable-tool hashes can vary with compiler and platform. The final
image hash is the compatibility check that matters.

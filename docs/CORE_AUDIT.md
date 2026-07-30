<!-- SPDX-License-Identifier: BSD-3-Clause -->

# Language-core dependency audit

This is a static audit of the preserved source at port revision
`f926bd6fb40ed6ca17da1ecae27274a7fac956f0`. It narrows the MSX port boundary;
it does not replace a runtime write trace.

Run the executable checks with:

```sh
make audit-core
```

## Link-map facts

The verified CP/M link map reports:

| Region | Size | Contents |
| --- | ---: | --- |
| language core | 12,492 bytes | `main`, `exec`, `eval`, `fpp`, `sorry` |
| CP/M OS layer | 2,081 bytes | `cmos` |
| fixed RAM state | 768 bytes | `ram` |

The core plus an adapter comparable in size to the current CP/M layer fits in
a 16 KiB payload ROM.

The link-layout target confirms the concrete placement: the cartridge veneer
is at `4000h`, the unchanged core occupies `4100h-71CBh`, and the 768-byte RAM
module occupies `8000h-82FFh`. The resulting 16 KiB layout ROM has SHA-256
`b92d38754db7451e3e14acd0c1ae05efea2c50c99a2b920ee36e35bfc906be11`.
Its service routines are nonfunctional stubs.

The subsequent MSX build keeps the cartridge veneer at `4000h`, places the
independently written console adapter at `4013h-423Ah`, the unchanged core at
`4400h-74C1h`, and the independently written graphics adapter at
`74C2h-77AAh`, followed by cassette storage at `77ABh-794Eh`. RainBIOS payload
descriptor v1 remains at `7FF0h-7FFFh`, fixed RAM at `8000h-82FFh`, and 34
adapter-state bytes at `8300h-8321h`. Its 16 KiB ROM
has SHA-256
`14733ea4ae0b7956dfcf9ab9ec4d6f1be838ec1f6efc6da83887fb0c69a7b817`.
The build driver parses the linker map and rejects boundary overlap.

`ram.z80` requires `ACCS`, `BUFFER`, and `STAVAR` to be page-aligned. Linking
the module at `8000h` satisfies that requirement. The platform state follows
the fixed RAM, so `OSINIT` exposes the first user byte at `8322h`.

## Platform interface

After resolving symbols supplied by the language core, the new graphics
adapter (including the remaining sound/device stubs), and `ram.z80`, the
console adapter must provide these 26 symbols:

```text
CLRSCN  GETCSR  GETEXT  GETIME  GETPTR  LTRAP  OSBGET
OSBPUT  OSCALL  OSCLI   OSINIT  OSKEY   OSLINE OSLOAD
OSOPEN  OSRDCH  OSSAVE  OSSHUT  OSSTAT  OSWRCH PROMPT
PUTCSR  PUTIME  PUTPTR  RESET   TRAP
```

The cassette slice implements `OSLOAD` and `OSSAVE`; remaining channel and
random-access calls retain explicit unsupported errors. All symbols have
documented flag and register behaviour.

## Static findings

- Active CP/M `BDOS` references are confined to `cmos.z80` and
  `adm3a/boot.z80`; `patch.z80` is an unused historical machine adapter.
- The language core contains no `DEFS` storage and no active `DI`, `EI`, `IM`,
  or `RST` instruction.
- Every direct core write of the form `LD (symbol),...` targets a symbol
  exported by `ram.z80`.
- The core has exactly two direct port instructions: `IN L,(C)` in the `INP`
  evaluator and `OUT (C),L` in the `OUT` statement. These are language
  features, not hidden platform dependencies.
- `cmos.z80` contains its own mutable `TABLE`, `FLAGS`, `INKEY`, `EDPTR`,
  `OPTVAL`, and `TRPCNT` state. It cannot be placed unchanged in ROM.

The static check intentionally cannot prove where every indirect `LD (HL),...`
or block transfer points at runtime. It also does not exercise user machine
code through `CALL`, `USR`, or `OSCALL`.

## Initial conclusion

Keep the relocatable language core in ROM and place all interpreter state and
user memory in RAM for the first MSX experiment. Replace the CP/M layer rather
than linking `cmos.z80` unchanged.

The openMSX integration test now:

1. watches `4000h-7FFFh` whenever the cartridge is selected;
2. boots to the prompt and executes integer, floating-point, string, editing,
   program-flow, unsupported channel-storage, clock, and timed-input cases;
3. requires zero attempted ROM writes and validates the resulting screen
   text.

The separate 1983 test renders the final ROM and requires the MSX blue console
plus enough white pixels for the BBC BASIC banner and prompt. Together these
tests establish ROM safety for the exercised P1 paths, not for arbitrary
machine code invoked by `CALL`, `USR`, `INP`, `OUT`, or `OSCALL`.

The Graphics II integration test retains the cartridge write watch while
running a stored BASIC program with `MODE`, `GCOL`, `MOVE`, `DRAW`, `PLOT`,
and `POINT`. It checks mode registers, VRAM reference pixels and colours, and
pixel readback. RainBIOS also runs the same workload, while 1983 independently
checks the rendered multicolour frame.

The three page alignments and stack bound are fixed by the link map and
`OSINIT`: `ACCS=8000h`, `BUFFER=8100h`, `STAVAR=8200h`, user RAM begins at
`8322h`, and the initial stack/top-of-memory value is `F300h`.

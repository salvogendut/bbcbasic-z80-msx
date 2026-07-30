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

`ram.z80` requires `ACCS`, `BUFFER`, and `STAVAR` to be page-aligned. Linking
the module at `8000h` satisfies that requirement and places the first user
byte at `8300h`.

## Platform interface

After resolving symbols supplied by the language core, graphics/sound stubs,
and `ram.z80`, the MSX adapter must provide these 26 symbols:

```text
CLRSCN  GETCSR  GETEXT  GETIME  GETPTR  LTRAP  OSBGET
OSBPUT  OSCALL  OSCLI   OSINIT  OSKEY   OSLINE OSLOAD
OSOPEN  OSRDCH  OSSAVE  OSSHUT  OSSTAT  OSWRCH PROMPT
PUTCSR  PUTIME  PUTPTR  RESET   TRAP
```

Console-only bring-up can implement storage calls as explicit unsupported
errors, but all symbols must have documented flag and register behaviour.

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

Before this becomes the committed payload format, an emulator test must:

1. map the candidate core range read-only;
2. record every attempted write to that range;
3. boot to the prompt and execute representative integer, floating-point,
   string, editing, error, and program-flow cases;
4. verify the three required page alignments and stack bounds.

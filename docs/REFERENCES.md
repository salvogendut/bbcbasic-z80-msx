<!-- SPDX-License-Identifier: BSD-3-Clause -->

# MSX references

The MSX adapter is independently written against public interface
documentation. No proprietary BIOS or BASIC source, tables, comments, data,
or disassembly were used to implement it.

Primary compatibility references:

- [MSX2 Technical Handbook, Appendix 1: BIOS listing](https://konamiman.github.io/MSX2-Technical-Handbook/md/Appendix1.html)
  for the documented calling conventions of `INITXT`, `CHSNS`, `CHGET`,
  `CHPUT`, `CLS`, `POSIT`, `ERAFNK`, `KILBUF`, `TAPION`, `TAPIN`, `TAPIOF`,
  `TAPOON`, `TAPOUT`, `TAPOOF`, `WRTPSG`, `RDPSG`, `GTSTCK`, `GTTRIG`,
  `CHGMOD`, and the MSX2 `SUBROM` 16-bit VRAM calls;
- [MSX2 Technical Handbook, Appendix 4: system work area](https://konamiman.github.io/MSX2-Technical-Handbook/md/Appendix4.html)
  for `CSRX`, `CSRY`, and `JIFFY`;
- [MSX2 Technical Handbook, Chapter 2](https://konamiman.github.io/MSX2-Technical-Handbook/md/Chapter2.html)
  for the 50/60 Hz region bit at `002Bh`;
- [BBC BASIC (Z80) keyword manual](https://www.bbcbasic.co.uk/bbcbasic/mancpm/bbckey1.html)
  and the official [BBC BASIC SOUND reference](https://www.bbcbasic.co.uk/bbcwin/manual/bbcwin7.html)
  for the language-level `SOUND`/`ENVELOPE` parameter semantics. The MSX AY
  implementation is deliberately documented as an approximation where the
  hardware models differ;
[C-BIOS](https://github.com/cbios/cbios) is used only as an open-source
runtime BIOS in the openMSX compatibility test. The separately developed
[1983](https://github.com/salvogendut/1983) emulator provides an independent
rendering confirmation.

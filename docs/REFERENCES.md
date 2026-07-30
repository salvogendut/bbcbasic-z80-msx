<!-- SPDX-License-Identifier: BSD-3-Clause -->

# MSX references

The MSX adapter is independently written against public interface
documentation. No proprietary BIOS or BASIC source, tables, comments, data,
or disassembly were used to implement it.

Primary compatibility references:

- [MSX2 Technical Handbook, Appendix 1: BIOS listing](https://konamiman.github.io/MSX2-Technical-Handbook/md/Appendix1.html)
  for the documented calling conventions of `INITXT`, `CHSNS`, `CHGET`,
  `CHPUT`, `CLS`, `POSIT`, `ERAFNK`, and `KILBUF`;
- [MSX2 Technical Handbook, Appendix 4: system work area](https://konamiman.github.io/MSX2-Technical-Handbook/md/Appendix4.html)
  for `CSRX`, `CSRY`, and `JIFFY`;
- [MSX2 Technical Handbook, Chapter 2](https://konamiman.github.io/MSX2-Technical-Handbook/md/Chapter2.html)
  for the 50/60 Hz region bit at `002Bh`;
[C-BIOS](https://github.com/cbios/cbios) is used only as an open-source
runtime BIOS in the openMSX compatibility test. The separately developed
[1983](https://github.com/salvogendut/1983) emulator provides an independent
rendering confirmation.

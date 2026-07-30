# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pathlib
import tempfile
import unittest

from tools.check_1983_screenshot import ppm_colours
from tools.check_openmsx_graphics import validate_report as validate_graphics_report
from tools.check_openmsx_smoke import validate_report


class EmulatorCheckTests(unittest.TestCase):
    def test_openmsx_report_requires_language_and_rom_guard_results(self) -> None:
        report = """\
ROM_WRITES=0
 BBC BASIC (Z80) Version 3.00+1
 >PRINT 2+2
          4
 1.41421356
 RAINBIOS
 >RUN
          1         2         3>*CAT
 Storage unsupported
 >PRINT TIME>=1000
         -1
 >PRINT INKEY(1)
         -1
"""
        validate_report(report)
        with self.assertRaisesRegex(ValueError, "ROM_WRITES"):
            validate_report(report.replace("ROM_WRITES=0", "ROM_WRITES=1"))

    def test_ppm_reader_counts_rgb_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "tiny.ppm"
            path.write_bytes(b"P6\n2 1\n255\n" + bytes((1, 2, 3, 1, 2, 3)))
            self.assertEqual(ppm_colours(path), ((2, 1), {(1, 2, 3): 2}))

    def test_graphics_report_requires_mode_pixels_colours_and_state(self) -> None:
        report = """\
ROM_WRITES=0
VDP=02,E0
PATTERN_NONZERO=500
PATTERN=80,01,80,80,01
COLOUR=51,31,F1,31,51
GRAPH_STATE=80,5F,0F
POINT_RESULT=07,00,00,00
"""
        validate_graphics_report(report)
        with self.assertRaisesRegex(ValueError, "reference colours"):
            validate_graphics_report(report.replace("F1", "81"))


if __name__ == "__main__":
    unittest.main()

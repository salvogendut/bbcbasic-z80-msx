# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pathlib
import tempfile
import unittest

from tools.check_1983_screenshot import ppm_colours
from tools.check_openmsx_graphics import validate_report as validate_graphics_report
from tools.check_openmsx_mode import validate_report as validate_mode_report
from tools.check_openmsx_msx2 import validate_report as validate_msx2_report
from tools.check_openmsx_smoke import validate_report
from tools.check_openmsx_sound import validate_report as validate_sound_report


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
GRAPH_STATE=C8,5F,0F
POINT_RESULT=07,00,00,00
AFTER_POINT_PATTERN=80
RECT_PATTERN_NONZERO=188
RECT_GRAPH=6C,72
RECT_PREV=6C,4D
RECT_VERTEX=0F
RECT_HYPO=F8
RECT_INSIDE=FF
RECT_OUTSIDE=00
"""
        validate_graphics_report(report)
        with self.assertRaisesRegex(ValueError, "reference colours"):
            validate_graphics_report(report.replace("F1", "81"))

    def test_msx1_mode_report_rejects_an_msx2_switch(self) -> None:
        report = """\
MODE1_SCRMOD=1
MODE3_SCRMOD=3
MODE2_SCRMOD=2
MODE0_SCRMOD=0
MODE5_MSX1_SCRMOD=0
"""
        validate_mode_report(report)
        with self.assertRaisesRegex(ValueError, "MODE 5 on MSX1"):
            validate_mode_report(report.replace("MODE5_MSX1_SCRMOD=0", "MODE5_MSX1_SCRMOD=5"))

    def test_msx2_report_requires_distinct_high_vram_pixels(self) -> None:
        report = """\
MODE5=05,06,01,02,30
MODE5_HIGH=80
MODE6=06,08,01,02,80
MODE6_HIGH=40
MODE7=07,0A,01,02,30
MODE7_HIGH=80
MODE8=08,0E,01,02,03
MODE8_HIGH=08
CLG8=08,0E,00
"""
        validate_msx2_report(report)
        with self.assertRaisesRegex(ValueError, "MODE 8"):
            validate_msx2_report(report.replace("MODE8_HIGH=08", "MODE8_HIGH=03"))

    def test_sound_report_distinguishes_envelope_and_fixed_volume(self) -> None:
        report = """\
TONE_A_PERIOD=B2,01
TONE_C_PERIOD=77,03
VOL_A=08
VOL_C=0A
NOISE_PERIOD=0D
MIXER=B1
ENV_PERIOD=0A,00
ENV_SHAPE=0C
TONE_B_PERIOD=D4,00
VOL_B=10
ENV_MIXER=B1
FIXED_VOL_B=0F
"""
        validate_sound_report(report)
        with self.assertRaisesRegex(ValueError, "fixed channel B"):
            validate_sound_report(report.replace("FIXED_VOL_B=0F", "FIXED_VOL_B=10"))


if __name__ == "__main__":
    unittest.main()

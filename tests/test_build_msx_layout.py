# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pathlib
import unittest

from tools.build_msx_layout import (
    CORE_BASE,
    EXPECTED_SHA256,
    RAM_BASE,
    RAM_END,
    ROM_BASE,
    ROM_END,
    link_command,
)


class MsxLayoutBuildTests(unittest.TestCase):
    def test_memory_profile_is_page_aligned(self) -> None:
        self.assertEqual(ROM_BASE, 0x4000)
        self.assertEqual(CORE_BASE, 0x4100)
        self.assertEqual(ROM_END, 0x8000)
        self.assertEqual(RAM_BASE, 0x8000)
        self.assertEqual(RAM_END, 0x8300)
        self.assertRegex(EXPECTED_SHA256, r"^[0-9a-f]{64}$")

    def test_link_command_fixes_core_and_ram_origins(self) -> None:
        command = link_command("ld80", pathlib.Path("build"))
        origins = [argument for argument in command if argument.startswith("-P")]
        self.assertEqual(origins, ["-P0x4100", "-P0x8000"])


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pathlib
import unittest

from tools.build_msx_console import (
    ADAPTER_BASE,
    CORE_BASE,
    EXPECTED_SHA256,
    RAM_BASE,
    ROM_BASE,
    ROM_END,
    STATE_BASE,
    STATE_END,
    link_command,
    parse_map_sections,
    validate_map,
)


class MsxConsoleBuildTests(unittest.TestCase):
    def test_memory_profile_is_fixed(self) -> None:
        self.assertEqual(ROM_BASE, 0x4000)
        self.assertEqual(ADAPTER_BASE, 0x4013)
        self.assertEqual(CORE_BASE, 0x4400)
        self.assertEqual(ROM_END, 0x8000)
        self.assertEqual(RAM_BASE, 0x8000)
        self.assertEqual(STATE_BASE, 0x8300)
        self.assertEqual(STATE_END, 0x8308)
        if EXPECTED_SHA256:
            self.assertRegex(EXPECTED_SHA256, r"^[0-9a-f]{64}$")

    def test_link_command_fixes_rom_and_ram_origins(self) -> None:
        command = link_command("ld80", pathlib.Path("build"))
        origins = [argument for argument in command if argument.startswith("-P")]
        self.assertEqual(
            origins,
            ["-P0x4013", "-P0x4400", "-P0x8000", "-P0x8300"],
        )

    def test_link_map_guard_accepts_the_fixed_windows(self) -> None:
        link_map = """\
4013   0216   P  -          CONSOLE  build/msx_console.rel
4400   0c5d   P  -          MAIN.Z8  build/main.rel
505d   10d5   P  -          EXEC.Z8  build/exec.rel
74c2   000a   P  -          SORRY.Z  build/sorry.rel
8000   0300   P  -          RAM.Z80  build/ram.rel
8300   0008   P  -          STATE.Z  build/msx_state.rel
"""
        self.assertEqual(
            parse_map_sections(link_map)[0],
            (0x4013, 0x0216, "CONSOLE"),
        )
        validate_map(link_map)

    def test_link_map_guard_rejects_adapter_core_overlap(self) -> None:
        link_map = """\
4013   0400   P  -          CONSOLE  build/msx_console.rel
4400   0c5d   P  -          MAIN.Z8  build/main.rel
8000   0300   P  -          RAM.Z80  build/ram.rel
8300   0008   P  -          STATE.Z  build/msx_state.rel
"""
        with self.assertRaisesRegex(ValueError, "overlaps"):
            validate_map(link_map)


if __name__ == "__main__":
    unittest.main()

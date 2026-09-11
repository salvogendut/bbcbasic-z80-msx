# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pathlib
import unittest

from tools.build_msx_console import (
    ADAPTER_BASE,
    CORE_BASE,
    DESCRIPTOR_ADDRESS,
    EXPECTED_DESCRIPTOR,
    EXPECTED_SHA256,
    MSX2_BASE,
    RAM_BASE,
    ROM_BASE,
    ROM_END,
    SPRITE_BASE,
    STATE_BASE,
    STATE_END,
    link_command,
    parse_map_sections,
    validate_map,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]


class MsxConsoleBuildTests(unittest.TestCase):
    def test_memory_profile_is_fixed(self) -> None:
        self.assertEqual(ROM_BASE, 0x4000)
        self.assertEqual(ADAPTER_BASE, 0x4013)
        self.assertEqual(SPRITE_BASE, 0x424C)
        self.assertEqual(MSX2_BASE, 0x4352)
        self.assertEqual(CORE_BASE, 0x4400)
        self.assertEqual(ROM_END, 0x8000)
        self.assertEqual(RAM_BASE, 0x8000)
        self.assertEqual(STATE_BASE, 0x8300)
        self.assertEqual(STATE_END, 0x833E)
        self.assertEqual(DESCRIPTOR_ADDRESS, 0x7FF0)
        self.assertEqual(len(EXPECTED_DESCRIPTOR), 16)
        self.assertEqual(sum(EXPECTED_DESCRIPTOR) & 0xFF, 0)
        self.assertEqual(EXPECTED_DESCRIPTOR[12:14], bytes((0xE0, 0xE6)))
        if EXPECTED_SHA256:
            self.assertRegex(EXPECTED_SHA256, r"^[0-9a-f]{64}$")

    def test_link_command_fixes_rom_and_ram_origins(self) -> None:
        command = link_command("ld80", pathlib.Path("build"))
        origins = [argument for argument in command if argument.startswith("-P")]
        self.assertEqual(
            origins,
            ["-P0x4013", "-P0x424c", "-P0x4352", "-P0x4400", "-P0x8000",
             "-P0x8300"],
        )
        self.assertIn("build/msx_storage.rel", command)
        self.assertIn("build/msx_sprite.rel", command)
        self.assertIn("build/msx_msx2.rel", command)

    def test_rainbios_dispatch_requires_the_complete_signature(self) -> None:
        source = (ROOT / "platform" / "msx" / "storage.z80").read_text()
        for offset, byte in enumerate("RBFS"):
            suffix = "" if offset == 0 else f"+{offset}"
            self.assertIn(f"LD      A,(RAINFS_SIGNATURE{suffix})", source)
            self.assertIn(f"CP      '{byte}'", source)

    def test_link_map_guard_accepts_the_fixed_windows(self) -> None:
        link_map = """\
4013   0239   P  -          CONSOLE  build/msx_console.rel
424c   0106   P  -          SPRITE.  build/msx_sprite.rel
4352   00a8   P  -          MSX2.Z8  build/msx_msx2.rel
4400   0c5d   P  -          MAIN.Z8  build/main.rel
505d   10d5   P  -          EXEC.Z8  build/exec.rel
6132   0796   P  -          EVAL.Z8  build/eval.rel
68c8   0bfa   P  -          FPP.Z80  build/fpp.rel
74c2   0984   P  -          GRAPHIC  build/msx_graphics.rel
7e46   01aa   P  -          STORAGE  build/msx_storage.rel
8000   0300   P  -          RAM.Z80  build/ram.rel
8300   003e   P  -          STATE.Z  build/msx_state.rel
"""
        self.assertEqual(
            parse_map_sections(link_map)[0],
            (0x4013, 0x0239, "CONSOLE"),
        )
        validate_map(link_map)

    def test_link_map_guard_rejects_adapter_core_overlap(self) -> None:
        link_map = """\
4013   0400   P  -          CONSOLE  build/msx_console.rel
4400   0c5d   P  -          MAIN.Z8  build/main.rel
8000   0300   P  -          RAM.Z80  build/ram.rel
8300   003e   P  -          STATE.Z  build/msx_state.rel
"""
        with self.assertRaisesRegex(ValueError, "overlaps"):
            validate_map(link_map)


if __name__ == "__main__":
    unittest.main()

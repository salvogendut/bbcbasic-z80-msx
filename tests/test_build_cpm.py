# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pathlib
import unittest

from tools.build_cpm_baseline import (
    BASE_ADDRESS,
    EXPECTED_SHA256,
    EXPECTED_SIZE,
    LANGUAGE_MODULES,
    link_command,
)


class CpmBaselineBuildTests(unittest.TestCase):
    def test_baseline_identity_is_fixed(self) -> None:
        self.assertEqual(BASE_ADDRESS, 0x0100)
        self.assertEqual(EXPECTED_SIZE, 15_616)
        self.assertRegex(EXPECTED_SHA256, r"^[0-9a-f]{64}$")

    def test_language_module_order_matches_preserved_build(self) -> None:
        self.assertEqual(
            LANGUAGE_MODULES,
            ("main", "exec", "eval", "fpp", "sorry", "cmos"),
        )

    def test_link_map_has_all_three_fixed_origins(self) -> None:
        output = pathlib.Path("build")
        command = link_command("ld80", output)
        origins = [argument for argument in command if argument.startswith("-P")]
        self.assertEqual(origins, ["-P0x0100", "-P0x0200", "-P0x3b00"])


if __name__ == "__main__":
    unittest.main()

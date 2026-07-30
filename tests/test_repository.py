# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import hashlib
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ImportedSourceTests(unittest.TestCase):
    def test_language_modules_are_present(self) -> None:
        required = {
            "cmos.z80",
            "eval.z80",
            "exec.z80",
            "fpp.z80",
            "main.z80",
            "ram.z80",
            "sorry.z80",
            "adm3a/boot.z80",
        }
        missing = sorted(path for path in required if not (ROOT / path).is_file())
        self.assertEqual([], missing)

    def test_imported_license_is_unchanged(self) -> None:
        digest = hashlib.sha256((ROOT / "COPYING").read_bytes()).hexdigest()
        self.assertEqual(
            "cf5efb79a693ab044d2c5354d00f682e22fde66b428da1b4dc24cb1ad2ef42bb",
            digest,
        )

    def test_msx_boundary_is_documented(self) -> None:
        text = (ROOT / "platform/msx/README.md").read_text(encoding="utf-8")
        for service in ("startup", "VDP", "keyboard", "cursor", "centisecond"):
            self.assertIn(service, text)


if __name__ == "__main__":
    unittest.main()


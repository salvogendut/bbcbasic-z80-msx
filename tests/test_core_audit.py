# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import unittest

from tools.audit_core import EXPECTED_PLATFORM_SYMBOLS, audit_core


class CoreAuditTests(unittest.TestCase):
    def test_static_core_boundary_has_no_regressions(self) -> None:
        report = audit_core()
        self.assertEqual([], report.failures)

    def test_platform_boundary_is_explicit(self) -> None:
        report = audit_core()
        self.assertEqual(EXPECTED_PLATFORM_SYMBOLS, report.platform_symbols)
        self.assertEqual(26, len(report.platform_symbols))


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import struct
import unittest

from tools.make_msx_tape_fixture import (
    BINARY_TYPE,
    CAS_MARKER,
    PROGRAM,
    PROGRAM_NAME,
    PROGRAM_START,
    binary_tape,
    make_image,
)


class MsxTapeFixtureTests(unittest.TestCase):
    def test_fixture_uses_two_standard_cas_blocks(self) -> None:
        image = make_image()
        first = len(CAS_MARKER) + len(BINARY_TYPE) + len(PROGRAM_NAME)
        self.assertEqual(image[: len(CAS_MARKER)], CAS_MARKER)
        self.assertEqual(image[first : first + len(CAS_MARKER)], CAS_MARKER)

    def test_fixture_metadata_matches_program_extent(self) -> None:
        image = make_image()
        metadata_offset = (
            len(CAS_MARKER)
            + len(BINARY_TYPE)
            + len(PROGRAM_NAME)
            + len(CAS_MARKER)
        )
        start, end, execute = struct.unpack_from("<HHH", image, metadata_offset)
        self.assertEqual(start, PROGRAM_START)
        self.assertEqual(end - start + 1, len(PROGRAM))
        self.assertEqual(execute, 0)
        self.assertEqual(image[metadata_offset + 6 :], PROGRAM)

    def test_invalid_envelopes_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "six bytes"):
            binary_tape(b"LONGNAME", b"x", start=0x8000)
        with self.assertRaisesRegex(ValueError, "empty"):
            binary_tape(b"EMPTY ", b"", start=0x8000)


if __name__ == "__main__":
    unittest.main()

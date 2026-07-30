#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Build a deterministic BBC BASIC program cassette for emulator tests."""

from __future__ import annotations

import argparse
import pathlib
import struct


CAS_MARKER = bytes.fromhex("1F A6 DE BA CC 13 7D 74")
BINARY_TYPE = bytes([0xD0]) * 10
PROGRAM_NAME = b"TAPET "
PROGRAM_START = 0x8322

# Tokenized form of: 10 ?&F3AC=90:PRINT "TAPE OK"
# BBC lines are length, little-endian line number, tokenized text, CR; a
# program ends in 00 FF FF.
PROGRAM = bytes.fromhex(
    "19 0A 00 3F 26 46 33 41 43 3D 39 30 3A "
    "F1 20 22 54 41 50 45 20 4F 4B 22 0D 00 FF FF"
)


def binary_tape(
    name: bytes,
    payload: bytes,
    *,
    start: int,
    execute: int = 0,
) -> bytes:
    if len(name) != 6:
        raise ValueError("cassette names must be exactly six bytes")
    if not payload:
        raise ValueError("cassette payload must not be empty")
    end = start + len(payload) - 1
    if not 0 <= start <= end <= 0xFFFF:
        raise ValueError("cassette payload does not fit in 16-bit memory")
    metadata = struct.pack("<HHH", start, end, execute)
    return (
        CAS_MARKER
        + BINARY_TYPE
        + name
        + CAS_MARKER
        + metadata
        + payload
    )


def make_image() -> bytes:
    return binary_tape(PROGRAM_NAME, PROGRAM, start=PROGRAM_START)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=pathlib.Path)
    arguments = parser.parse_args()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    image = make_image()
    arguments.output.write_bytes(image)
    print(f"wrote BBC BASIC cassette fixture: {arguments.output} ({len(image)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

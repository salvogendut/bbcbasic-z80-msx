#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate the openMSX MSX2 mode, POINT, and physical-VRAM report."""

from __future__ import annotations

import argparse
import pathlib


EXPECTED = {
    5: (0x06, 0x01, 0x02, 0x30, 0x80),
    6: (0x08, 0x01, 0x02, 0x80, 0x40),
    7: (0x0A, 0x01, 0x02, 0x30, 0x80),
    8: (0x0E, 0x01, 0x02, 0x03, 0x08),
}


def validate_report(text: str) -> dict[str, str]:
    values = {}
    for line in text.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key] = value

    for mode, expected in EXPECTED.items():
        try:
            fields = tuple(
                int(value, 16) for value in values[f"MODE{mode}"].split(",")
            )
            high = int(values[f"MODE{mode}_HIGH"], 16)
        except (KeyError, ValueError) as error:
            raise ValueError(f"MODE {mode}: missing or invalid report") from error
        actual = fields[1:] + (high,)
        if fields[0] != mode:
            raise ValueError(f"MODE {mode}: SCRMOD is {fields[0]}, expected {mode}")
        if actual != expected:
            raise ValueError(
                f"MODE {mode}: R0/POINT/VRAM {actual}, expected {expected}"
            )
    try:
        clg8 = tuple(int(value, 16) for value in values["CLG8"].split(","))
    except (KeyError, ValueError) as error:
        raise ValueError("missing or invalid Screen 8 CLG report") from error
    if clg8 != (8, 0x0E, 0):
        raise ValueError(
            f"Screen 8 CLG changed mode or missed high VRAM: {clg8}"
        )
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=pathlib.Path)
    arguments = parser.parse_args()
    try:
        validate_report(arguments.report.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print("validated openMSX BBC BASIC MSX2 modes and high-VRAM pixels (5/6/7/8)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

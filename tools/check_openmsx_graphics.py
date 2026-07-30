#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate the openMSX BBC BASIC Graphics II program report."""

from __future__ import annotations

import argparse
import pathlib


def validate_report(text: str) -> dict[str, str]:
    values = {}
    for line in text.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key] = value

    expected = {
        "ROM_WRITES": "0",
        "VDP": "02,E0",
        "GRAPH_STATE": "80,5F,0F",
        "POINT_RESULT": "07,00,00,00",
    }
    for key, value in expected.items():
        if values.get(key) != value:
            raise ValueError(
                f"{key}: found {values.get(key)!r}, expected {value!r}"
            )

    try:
        nonzero = int(values["PATTERN_NONZERO"])
        pattern = [int(value, 16) for value in values["PATTERN"].split(",")]
        colour = [int(value, 16) for value in values["COLOUR"].split(",")]
    except (KeyError, ValueError) as error:
        raise ValueError("missing or invalid graphics VRAM report") from error
    if nonzero < 150:
        raise ValueError(f"only {nonzero} nonzero pattern bytes were drawn")
    if any(value == 0 for value in pattern):
        raise ValueError(f"one or more reference pixels are clear: {pattern}")
    if [value >> 4 for value in colour] != [5, 3, 15, 3, 5]:
        raise ValueError(f"unexpected reference colours: {colour}")
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=pathlib.Path)
    arguments = parser.parse_args()
    try:
        values = validate_report(arguments.report.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(
        "validated openMSX BBC BASIC graphics program: "
        f"{values['PATTERN_NONZERO']} nonzero pattern bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate the openMSX BBC BASIC MODE screen-mode report."""

from __future__ import annotations

import argparse
import pathlib


def validate_report(text: str) -> dict[str, str]:
    values = {}
    for line in text.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key] = value

    try:
        mode1 = int(values["MODE1_SCRMOD"])
        mode3 = int(values["MODE3_SCRMOD"])
        mode2 = int(values["MODE2_SCRMOD"])
        mode7 = int(values["MODE7_SCRMOD"])
    except (KeyError, ValueError) as error:
        raise ValueError("missing or invalid SCRMOD report") from error

    if mode1 != 1:
        raise ValueError(f"MODE 1 -> SCRMOD {mode1}, expected 1")
    if mode3 != 3:
        raise ValueError(f"MODE 3 -> SCRMOD {mode3}, expected 3")
    if mode2 != 2:
        raise ValueError(f"MODE 2 -> SCRMOD {mode2}, expected 2")
    if mode7 != 0:
        raise ValueError(f"MODE 7 -> SCRMOD {mode7}, expected 0")
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
        "validated openMSX BBC BASIC MODE program: "
        f"SCRMOD {values['MODE1_SCRMOD']}/{values['MODE3_SCRMOD']}/"
        f"{values['MODE2_SCRMOD']}/{values['MODE7_SCRMOD']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

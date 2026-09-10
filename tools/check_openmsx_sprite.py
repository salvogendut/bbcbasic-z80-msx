#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate the openMSX BBC BASIC *SPRITE VDP sprite-table report."""

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
        pattern = [int(value, 16) for value in values["PATTERN"].split(",")]
        attr = [int(value, 16) for value in values["ATTR"].split(",")]
    except (KeyError, ValueError) as error:
        raise ValueError("missing or invalid sprite VRAM report") from error

    if pattern != [0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF]:
        raise ValueError(
            f"sprite pattern {pattern}, expected [FF,81,81,81,81,81,81,FF]"
        )
    if attr != [0x64, 0x64, 0x00, 0x0F]:
        raise ValueError(
            f"sprite attribute {attr}, expected [64,64,00,0F]"
        )
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
        "validated openMSX BBC BASIC *SPRITE program: "
        f"pattern={values['PATTERN']} attr={values['ATTR']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

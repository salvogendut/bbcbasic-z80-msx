#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate the text report produced by openmsx_smoke.tcl."""

from __future__ import annotations

import argparse
import pathlib
import re


def validate_report(text: str) -> None:
    required = (
        "ROM_WRITES=0",
        "BBC BASIC (Z80) Version 3.00+1",
        ">PRINT 2+2",
        "          4",
        "1.41421356",
        "RAINBIOS",
        ">RUN",
        "Storage unsupported",
        ">PRINT TIME>=1000",
        ">PRINT INKEY(1)",
    )
    for fragment in required:
        if fragment not in text:
            raise ValueError(f"missing smoke-test result: {fragment!r}")
    if not re.search(r"\n\s+1\s+2\s+3>", text):
        raise ValueError("missing FOR/NEXT program output")
    if len(re.findall(r"\n\s+-1\s*$", text, flags=re.MULTILINE)) < 2:
        raise ValueError("missing TIME assignment or INKEY timeout result")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=pathlib.Path)
    arguments = parser.parse_args()
    try:
        validate_report(arguments.report.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"validated openMSX console smoke test: {arguments.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate BBC BASIC MSX2 PLOT/POINT and high-VRAM access in 1983.

Boots the cartridge on the Omega MSX2 (V9958) model, types a program that
plots distinct pixels on opposite sides of the old 16 KiB alias boundary,
and checks both POINT results for Screens 5, 6, 7, and 8.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess


def run_plot(binary: str, models: str, cart: str, mode: int) -> tuple[int, int]:
    alias_y = 683 if mode < 7 else 342
    program = (
        f"10 MODE {mode}\n20 GCOL 0,1:PLOT 69,500,0\n"
        f"30 GCOL 0,2:PLOT 69,500,{alias_y}\n"
        f"40 ?&E000=POINT(500,0)\n"
        f"50 ?&E001=POINT(500,{alias_y})\nRUN\n"
    )
    command = [
        binary,
        "--config", "/dev/null",
        "--models", models,
        "--model", "omega-msx2",
        "--region", "ntsc",
        "--cart", cart,
        "--headless", "--unthrottled",
        "--paste-at", "300",
        "--paste-text", program,
        "--exit-after", "1000",
        "--dump-ram", "0xE000:2",
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, check=True
    )
    output = result.stdout + result.stderr
    match = re.search(
        r"E000:\s*([0-9a-fA-F]{2})\s+([0-9a-fA-F]{2})", output
    )
    if not match:
        raise ValueError(f"MODE {mode}: no dump-ram output")
    return int(match.group(1), 16), int(match.group(2), 16)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--1983", dest="binary", default="../1983/1983")
    parser.add_argument("--models", default="../1983/1983-models.conf")
    parser.add_argument("--cart", type=pathlib.Path, required=True)
    arguments = parser.parse_args()

    for mode in (5, 6, 7, 8):
        try:
            values = run_plot(
                arguments.binary, arguments.models, str(arguments.cart), mode
            )
        except (subprocess.CalledProcessError, ValueError) as error:
            parser.error(str(error))
        if values != (1, 2):
            parser.error(
                f"MODE {mode}: POINT returned {values}, expected (1, 2); "
                "high VRAM may be aliasing"
            )
        print(f"MODE {mode}: distinct low/high-VRAM PLOT/POINT results OK")

    print("validated 1983 BBC BASIC MSX2 PLOT/POINT (Screens 5/6/7/8)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate the BBC BASIC MSX2 PLOT/POINT round trip in the 1983 emulator.

Boots the cartridge on the Omega MSX2 (V9958) model, types a program that
plots a single point and reads it back with POINT, and checks the stored
result for Screens 5, 7, and 8.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess


def run_plot(binary: str, models: str, cart: str, mode: int) -> int:
    program = (
        f"10 MODE {mode}\n20 GCOL 0,1\n30 PLOT 69,500,512\n"
        "40 ?&E000=POINT(500,512)\nRUN\n"
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
        "--dump-ram", "0xE000:1",
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, check=True
    )
    output = result.stdout + result.stderr
    match = re.search(r"E000:\s*([0-9a-fA-F]{2})", output)
    if not match:
        raise ValueError(f"MODE {mode}: no dump-ram output")
    return int(match.group(1), 16)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--1983", dest="binary", default="../1983/1983")
    parser.add_argument("--models", default="../1983/1983-models.conf")
    parser.add_argument("--cart", type=pathlib.Path, required=True)
    arguments = parser.parse_args()

    for mode in (5, 7, 8):
        try:
            value = run_plot(
                arguments.binary, arguments.models, str(arguments.cart), mode
            )
        except (subprocess.CalledProcessError, ValueError) as error:
            parser.error(str(error))
        if value != 1:
            parser.error(f"MODE {mode}: POINT returned {value}, expected 1")
        print(f"MODE {mode}: PLOT/POINT round trip OK")

    print("validated 1983 BBC BASIC MSX2 PLOT/POINT (Screens 5/7/8)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

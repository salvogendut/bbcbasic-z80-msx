#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate the BBC BASIC MSX2 screen modes in the 1983 emulator.

Boots the cartridge on the Omega MSX2 (V9958) model, types MODE 5-8, and
checks the VDP mode register 0 after each switch.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess

EXPECTED_R0 = {5: 0x06, 6: 0x08, 7: 0x0A, 8: 0x0E}


def run_mode(binary: str, models: str, cart: str, mode: int) -> int:
    command = [
        binary,
        "--config", "/dev/null",
        "--models", models,
        "--model", "omega-msx2",
        "--region", "ntsc",
        "--cart", cart,
        "--headless", "--unthrottled",
        "--paste-at", "300",
        "--paste-text", f"MODE {mode}\n",
        "--exit-after", "600",
        "--dump-state",
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, check=True
    )
    output = result.stdout + result.stderr
    match = re.search(r"vdp_r0=([0-9a-fA-F]{2})", output)
    if not match:
        raise ValueError(f"MODE {mode}: no vdp_r0 in emulator output")
    return int(match.group(1), 16)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--1983", dest="binary", default="../1983/1983")
    parser.add_argument("--models", default="../1983/1983-models.conf")
    parser.add_argument("--cart", type=pathlib.Path, required=True)
    arguments = parser.parse_args()

    for mode, expected in EXPECTED_R0.items():
        try:
            r0 = run_mode(
                arguments.binary, arguments.models, str(arguments.cart), mode
            )
        except (subprocess.CalledProcessError, ValueError) as error:
            parser.error(str(error))
        if r0 != expected:
            parser.error(f"MODE {mode}: vdp_r0={r0:02X}, expected {expected:02X}")
        print(f"MODE {mode}: vdp_r0={r0:02X}")

    print("validated 1983 BBC BASIC MSX2 screen modes (5-8)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

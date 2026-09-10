#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Exercise BBC BASIC sprite rendering and SOUND on the 1983 Omega MSX2."""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess

if __package__:
    from .check_1983_screenshot import ppm_colours
else:
    from check_1983_screenshot import ppm_colours


PROGRAM = (
    "10 MODE 2\n"
    "20 *SPRITECLR\n"
    "30 *SPRITEPAT 0,255,129,129,129,129,129,129,255\n"
    "40 *SPRITE 0,100,100,0,15\n"
    "50 SOUND 2,-12,136,-1\n"
    "60 ?&E000=90\n"
    "70 GOTO 70\n"
    "RUN\n"
)


def validate_output(text: str, screenshot: pathlib.Path) -> None:
    if not re.search(r"E000:\s*5A", text, re.IGNORECASE):
        raise ValueError("program did not execute past the SOUND statement")
    if not re.search(r"vdp_r0=02\b", text, re.IGNORECASE):
        raise ValueError("program did not remain in Screen 2")
    dimensions, colours = ppm_colours(screenshot)
    if dimensions != (640, 480):
        raise ValueError(f"unexpected screenshot dimensions: {dimensions}")
    white = colours[(255, 255, 255)]
    if not 100 <= white <= 200:
        raise ValueError(f"sprite render has {white} white pixels, expected 100..200")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--1983", dest="binary", default="../1983/1983")
    parser.add_argument("--models", default="../1983/1983-models.conf")
    parser.add_argument("--cart", type=pathlib.Path, required=True)
    parser.add_argument("--screenshot", type=pathlib.Path, required=True)
    arguments = parser.parse_args()

    command = [
        arguments.binary,
        "--config", "/dev/null",
        "--models", arguments.models,
        "--model", "omega-msx2",
        "--region", "ntsc",
        "--cart", str(arguments.cart),
        "--headless", "--unthrottled",
        "--paste-at", "300",
        "--paste-text", PROGRAM,
        "--exit-after", "1600",
        "--dump-ram", "0xE000:1",
        "--screenshot", str(arguments.screenshot),
        "--dump-state",
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )
        validate_output(result.stdout + result.stderr, arguments.screenshot)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        parser.error(str(error))
    print("validated 1983 BBC BASIC sprite render and SOUND execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

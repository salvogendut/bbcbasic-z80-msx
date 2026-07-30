#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Check that 1983 rendered the expected MSX text-screen colours."""

from __future__ import annotations

import argparse
import collections
import pathlib


def ppm_colours(path: pathlib.Path) -> tuple[tuple[int, int], collections.Counter]:
    with path.open("rb") as source:
        if source.readline().strip() != b"P6":
            raise ValueError("screenshot is not a raw PPM image")
        dimensions = source.readline().split()
        if len(dimensions) != 2 or source.readline().strip() != b"255":
            raise ValueError("unsupported PPM header")
        width, height = (int(value) for value in dimensions)
        pixels = source.read()
    if len(pixels) != width * height * 3:
        raise ValueError("truncated PPM pixel data")
    colours = collections.Counter(zip(pixels[0::3], pixels[1::3], pixels[2::3]))
    return (width, height), colours


def validate_screenshot(path: pathlib.Path) -> None:
    dimensions, colours = ppm_colours(path)
    if dimensions != (640, 480):
        raise ValueError(f"unexpected screenshot dimensions: {dimensions}")
    if colours[(89, 85, 224)] < 250_000:
        raise ValueError("MSX blue console background was not rendered")
    if colours[(255, 255, 255)] < 1_000:
        raise ValueError("BBC BASIC banner/prompt text was not rendered")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("screenshot", type=pathlib.Path)
    arguments = parser.parse_args()
    try:
        validate_screenshot(arguments.screenshot)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"validated 1983 BBC BASIC screen: {arguments.screenshot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

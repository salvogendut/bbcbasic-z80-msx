#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate the openMSX BBC BASIC SOUND PSG register report."""

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
        tone_a = [int(value, 16) for value in values["TONE_A_PERIOD"].split(",")]
        tone_c = [int(value, 16) for value in values["TONE_C_PERIOD"].split(",")]
        vol_a = int(values["VOL_A"], 16)
        vol_c = int(values["VOL_C"], 16)
        noise = int(values["NOISE_PERIOD"], 16)
        mixer = int(values["MIXER"], 16)
    except (KeyError, ValueError) as error:
        raise ValueError("missing or invalid PSG register report") from error

    if tone_a != [0x50, 0x06]:
        raise ValueError(f"tone A period {tone_a}, expected [0x50, 0x06]")
    if tone_c != [0x30, 0x03]:
        raise ValueError(f"tone C period {tone_c}, expected [0x30, 0x03]")
    if vol_a != 0x08:
        raise ValueError(f"channel A volume {vol_a:#04X}, expected 0x08")
    if vol_c != 0x0A:
        raise ValueError(f"channel C volume {vol_c:#04X}, expected 0x0A")
    if noise != 0x19:
        raise ValueError(f"noise period {noise:#04X}, expected 0x19")
    if not (mixer & 0x01):
        raise ValueError(f"mixer {mixer:#04X}: tone A was not disabled")
    if mixer & 0x08:
        raise ValueError(f"mixer {mixer:#04X}: noise A was not enabled")
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
        "validated openMSX BBC BASIC SOUND program: "
        f"tone A={values['TONE_A_PERIOD']} "
        f"tone C={values['TONE_C_PERIOD']} "
        f"vol A/C={values['VOL_A']}/{values['VOL_C']} "
        f"noise={values['NOISE_PERIOD']} mixer={values['MIXER']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate the openMSX BBC BASIC SOUND/ENVELOPE PSG register report."""

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
        env_period = [int(value, 16) for value in values["ENV_PERIOD"].split(",")]
        env_shape = int(values["ENV_SHAPE"], 16)
        tone_b = [int(value, 16) for value in values["TONE_B_PERIOD"].split(",")]
        vol_b = int(values["VOL_B"], 16)
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
    if env_period != [0x0A, 0x00]:
        raise ValueError(f"envelope period {env_period}, expected [0x0A, 0x00]")
    if env_shape != 0x0C:
        raise ValueError(f"envelope shape {env_shape:#04X}, expected 0x0C")
    if tone_b != [0x70, 0x09]:
        raise ValueError(f"tone B period {tone_b}, expected [0x70, 0x09]")
    if vol_b != 0x10:
        raise ValueError(
            f"channel B volume {vol_b:#04X}, expected 0x10 (envelope mode)"
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
        "validated openMSX BBC BASIC SOUND/ENVELOPE program: "
        f"tone A={values['TONE_A_PERIOD']} "
        f"tone C={values['TONE_C_PERIOD']} "
        f"envelope={values['ENV_PERIOD']}/{values['ENV_SHAPE']} "
        f"vol B={values['VOL_B']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

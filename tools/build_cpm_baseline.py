#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Build and verify the preserved ADM-3A CP/M BBC BASIC baseline."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_ADDRESS = 0x0100
LANGUAGE_MODULES = ("main", "exec", "eval", "fpp", "sorry", "cmos")
RELOCATABLE_MODULES = LANGUAGE_MODULES + ("ram",)
EXPECTED_SIZE = 15_616
EXPECTED_SHA256 = "8f65a0a83d2231384b5a7f79035c2b97d748d238a924a116a84214c004cbe8f6"


def object_path(output_dir: pathlib.Path, module: str) -> pathlib.Path:
    return output_dir / f"{module}.rel"


def assemble_command(
    zmac: str,
    source: pathlib.Path,
    output: pathlib.Path,
) -> list[str]:
    return [
        zmac,
        "--nmnv",
        "--zmac",
        "-m",
        "--rel7",
        "-z",
        "-o",
        str(output),
        str(source),
    ]


def link_command(ld80: str, output_dir: pathlib.Path) -> list[str]:
    return [
        ld80,
        "-m",
        "-O",
        "bin",
        "-o",
        str(output_dir / "bbcbasic_adm3a.all"),
        "-s",
        "/dev/null",
        "-P0x0100",
        str(object_path(output_dir, "boot_adm3a")),
        "-P0x0200",
        *(str(object_path(output_dir, module)) for module in LANGUAGE_MODULES),
        "-P0x3b00",
        str(object_path(output_dir, "ram")),
    ]


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zmac", default="zmac")
    parser.add_argument("--ld80", default="ld80")
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=ROOT / "build" / "cpm",
    )
    arguments = parser.parse_args()
    output_dir = arguments.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for module in RELOCATABLE_MODULES:
        run(
            assemble_command(
                arguments.zmac,
                ROOT / f"{module}.z80",
                object_path(output_dir, module),
            )
        )
    run(
        assemble_command(
            arguments.zmac,
            ROOT / "adm3a" / "boot.z80",
            object_path(output_dir, "boot_adm3a"),
        )
    )
    run(link_command(arguments.ld80, output_dir))

    absolute_image = (output_dir / "bbcbasic_adm3a.all").read_bytes()
    if len(absolute_image) < BASE_ADDRESS:
        print("error: linked image is shorter than its load address", file=sys.stderr)
        return 1

    image = absolute_image[BASE_ADDRESS:]
    digest = hashlib.sha256(image).hexdigest()
    if len(image) != EXPECTED_SIZE or digest != EXPECTED_SHA256:
        print(
            "error: CP/M baseline mismatch: "
            f"{len(image)} bytes, SHA-256 {digest}; expected "
            f"{EXPECTED_SIZE} bytes, SHA-256 {EXPECTED_SHA256}",
            file=sys.stderr,
        )
        return 1

    output = output_dir / "bbcbasic_adm3a.com"
    output.write_bytes(image)
    print(f"wrote verified baseline: {output}")
    print(f"{EXPECTED_SIZE} bytes, SHA-256 {EXPECTED_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

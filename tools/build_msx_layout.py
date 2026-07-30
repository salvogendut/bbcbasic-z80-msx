#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Build and verify the nonfunctional BBC BASIC MSX link-layout ROM."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

if __package__:
    from .build_cpm_baseline import (
        LANGUAGE_MODULES,
        ROOT,
        assemble_command,
        object_path,
    )
else:
    from build_cpm_baseline import (
        LANGUAGE_MODULES,
        ROOT,
        assemble_command,
        object_path,
    )


ROM_BASE = 0x4000
CORE_BASE = 0x4100
ROM_END = 0x8000
RAM_BASE = 0x8000
RAM_END = 0x8300
EXPECTED_SHA256 = "b92d38754db7451e3e14acd0c1ae05efea2c50c99a2b920ee36e35bfc906be11"
CORE_MODULES = LANGUAGE_MODULES[:-1]


def link_command(ld80: str, output_dir: pathlib.Path) -> list[str]:
    return [
        ld80,
        "-m",
        "-O",
        "bin",
        "-o",
        str(output_dir / "bbcbasic_msx_layout.all"),
        "-s",
        str(output_dir / "bbcbasic_msx_layout.map"),
        str(object_path(output_dir, "layout_stub")),
        f"-P{CORE_BASE:#06x}",
        *(str(object_path(output_dir, module)) for module in CORE_MODULES),
        f"-P{RAM_BASE:#06x}",
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
        default=ROOT / "build" / "msx-layout",
    )
    arguments = parser.parse_args()
    output_dir = arguments.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for module in CORE_MODULES + ("ram",):
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
            ROOT / "platform" / "msx" / "layout_stub.z80",
            object_path(output_dir, "layout_stub"),
        )
    )
    run(link_command(arguments.ld80, output_dir))

    absolute_image = (output_dir / "bbcbasic_msx_layout.all").read_bytes()
    if len(absolute_image) != RAM_END:
        print(
            f"error: linked image is {len(absolute_image)} bytes, "
            f"expected {RAM_END}",
            file=sys.stderr,
        )
        return 1

    rom = absolute_image[ROM_BASE:ROM_END]
    digest = hashlib.sha256(rom).hexdigest()
    if len(rom) != ROM_END - ROM_BASE or digest != EXPECTED_SHA256:
        print(
            "error: MSX layout mismatch: "
            f"{len(rom)} bytes, SHA-256 {digest}; expected "
            f"{ROM_END - ROM_BASE} bytes, SHA-256 {EXPECTED_SHA256}",
            file=sys.stderr,
        )
        return 1
    if rom[:2] != b"AB" or int.from_bytes(rom[2:4], "little") != 0x4010:
        print("error: invalid MSX cartridge header", file=sys.stderr)
        return 1

    output = output_dir / "bbcbasic_msx_layout.rom"
    output.write_bytes(rom)
    print(f"wrote verified nonfunctional layout: {output}")
    print(f"{len(rom)} bytes, SHA-256 {EXPECTED_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

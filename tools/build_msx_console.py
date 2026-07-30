#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Build and verify the console-only BBC BASIC MSX cartridge ROM."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
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
ADAPTER_BASE = 0x4013
CORE_BASE = 0x4400
ROM_END = 0x8000
RAM_BASE = 0x8000
STATE_BASE = 0x8300
STATE_END = 0x8308
DESCRIPTOR_ADDRESS = 0x7FF0
EXPECTED_DESCRIPTOR = bytes.fromhex(
    "52 42 50 31 01 10 01 07 10 40 00 80 00 F3 02 0D"
)
EXPECTED_SHA256 = "2a53b54be1f5b734f1f8f9ea075c62b1cdedab5aad516334da74f60614987bcd"
CORE_MODULES = LANGUAGE_MODULES[:-1]
MAP_SECTION_RE = re.compile(
    r"^(?P<address>[0-9a-fA-F]{4})\s+"
    r"(?P<length>[0-9a-fA-F]{4})\s+P\s+\S+\s+"
    r"(?P<module>\S+)"
)


def parse_map_sections(text: str) -> list[tuple[int, int, str]]:
    """Return (address, length, module) records from an ld80 map."""
    sections = []
    for line in text.splitlines():
        match = MAP_SECTION_RE.match(line)
        if match:
            sections.append(
                (
                    int(match.group("address"), 16),
                    int(match.group("length"), 16),
                    match.group("module"),
                )
            )
    return sections


def validate_map(text: str) -> None:
    """Reject a link map whose ROM or RAM sections escaped their windows."""
    sections = parse_map_sections(text)
    expected_starts = {
        ADAPTER_BASE: "CONSOLE",
        CORE_BASE: "MAIN.Z8",
        RAM_BASE: "RAM.Z80",
        STATE_BASE: "STATE.Z",
    }
    by_address = {address: (length, module) for address, length, module in sections}
    for address, expected_module in expected_starts.items():
        if address not in by_address:
            raise ValueError(f"missing section at {address:#06x}")
        _, module = by_address[address]
        if module != expected_module:
            raise ValueError(
                f"section at {address:#06x} is {module}, expected {expected_module}"
            )

    adapter_length, _ = by_address[ADAPTER_BASE]
    if ADAPTER_BASE + adapter_length > CORE_BASE:
        raise ValueError("MSX adapter overlaps the language core")

    rom_sections = [
        (address, length, module)
        for address, length, module in sections
        if ROM_BASE <= address < ROM_END
    ]
    if not rom_sections or any(
        address + length > ROM_END for address, length, _ in rom_sections
    ):
        raise ValueError("a linked code section escapes the cartridge ROM window")

    ram_length, _ = by_address[RAM_BASE]
    state_length, _ = by_address[STATE_BASE]
    if ram_length != STATE_BASE - RAM_BASE:
        raise ValueError("BBC BASIC fixed RAM is not exactly 768 bytes")
    if state_length != STATE_END - STATE_BASE:
        raise ValueError("MSX adapter state is not exactly 8 bytes")


def link_command(ld80: str, output_dir: pathlib.Path) -> list[str]:
    return [
        ld80,
        "-m",
        "-O",
        "bin",
        "-o",
        str(output_dir / "bbcbasic_msx_console.all"),
        "-s",
        str(output_dir / "bbcbasic_msx_console.map"),
        str(object_path(output_dir, "msx_cartridge")),
        f"-P{ADAPTER_BASE:#06x}",
        str(object_path(output_dir, "msx_console")),
        f"-P{CORE_BASE:#06x}",
        *(str(object_path(output_dir, module)) for module in CORE_MODULES),
        str(object_path(output_dir, "msx_descriptor")),
        f"-P{RAM_BASE:#06x}",
        str(object_path(output_dir, "ram")),
        f"-P{STATE_BASE:#06x}",
        str(object_path(output_dir, "msx_state")),
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
        default=ROOT / "build" / "msx-console",
    )
    parser.add_argument(
        "--print-digest",
        action="store_true",
        help="print the candidate digest without enforcing the pinned value",
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
            ROOT / "platform" / "msx" / "cartridge.z80",
            object_path(output_dir, "msx_cartridge"),
        )
    )
    run(
        assemble_command(
            arguments.zmac,
            ROOT / "platform" / "msx" / "console.z80",
            object_path(output_dir, "msx_console"),
        )
    )
    run(
        assemble_command(
            arguments.zmac,
            ROOT / "platform" / "msx" / "state.z80",
            object_path(output_dir, "msx_state"),
        )
    )
    run(
        assemble_command(
            arguments.zmac,
            ROOT / "platform" / "msx" / "descriptor.z80",
            object_path(output_dir, "msx_descriptor"),
        )
    )
    run(link_command(arguments.ld80, output_dir))

    try:
        validate_map(
            (output_dir / "bbcbasic_msx_console.map").read_text(encoding="utf-8")
        )
    except ValueError as error:
        print(f"error: invalid MSX console link map: {error}", file=sys.stderr)
        return 1

    absolute_image = (output_dir / "bbcbasic_msx_console.all").read_bytes()
    if len(absolute_image) != STATE_END:
        print(
            f"error: linked image is {len(absolute_image)} bytes, "
            f"expected {STATE_END}",
            file=sys.stderr,
        )
        return 1

    rom = absolute_image[ROM_BASE:ROM_END]
    digest = hashlib.sha256(rom).hexdigest()
    if len(rom) != ROM_END - ROM_BASE:
        print(f"error: ROM is {len(rom)} bytes, expected 16384", file=sys.stderr)
        return 1
    if rom[:2] != b"AB" or int.from_bytes(rom[2:4], "little") != 0x4010:
        print("error: invalid MSX cartridge header", file=sys.stderr)
        return 1
    descriptor_offset = DESCRIPTOR_ADDRESS - ROM_BASE
    if (
        rom[descriptor_offset : descriptor_offset + len(EXPECTED_DESCRIPTOR)]
        != EXPECTED_DESCRIPTOR
    ):
        print("error: invalid RainBIOS payload descriptor", file=sys.stderr)
        return 1
    if not arguments.print_digest and digest != EXPECTED_SHA256:
        print(
            "error: MSX console ROM digest mismatch: "
            f"{digest}; expected {EXPECTED_SHA256 or '<not pinned>'}",
            file=sys.stderr,
        )
        return 1

    output = output_dir / "bbcbasic_msx_console.rom"
    output.write_bytes(rom)
    print(f"wrote console-only MSX cartridge: {output}")
    print(f"{len(rom)} bytes, SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Check static assumptions behind a ROM-resident BBC BASIC core."""

from __future__ import annotations

from dataclasses import dataclass
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE_SOURCES = ("main.z80", "exec.z80", "eval.z80", "fpp.z80", "sorry.z80")
EXPECTED_DIRECT_IO = {
    ("eval.z80", "IN L,(C)"),
    ("exec.z80", "OUT (C),L"),
}
INDIRECT_REGISTERS = frozenset({"BC", "DE", "HL", "IX", "IY", "SP"})
EXPECTED_PLATFORM_SYMBOLS = frozenset(
    {
        "CLRSCN",
        "GETCSR",
        "GETEXT",
        "GETIME",
        "GETPTR",
        "LTRAP",
        "OSBGET",
        "OSBPUT",
        "OSCALL",
        "OSCLI",
        "OSINIT",
        "OSKEY",
        "OSLINE",
        "OSLOAD",
        "OSOPEN",
        "OSRDCH",
        "OSSAVE",
        "OSSHUT",
        "OSSTAT",
        "OSWRCH",
        "PROMPT",
        "PUTCSR",
        "PUTIME",
        "PUTPTR",
        "RESET",
        "TRAP",
    }
)

LABEL = r"[A-Za-z_?@.$][A-Za-z0-9_?@.$]*"
OPTIONAL_LABEL = rf"(?:{LABEL}:\s*)?"
DIRECT_WRITE = re.compile(
    rf"^{OPTIONAL_LABEL}LD\s+\(\s*({LABEL})(?:\s*[+-][^)]+)?\s*\)\s*,",
    re.IGNORECASE,
)
DIRECT_IO = re.compile(rf"^{OPTIONAL_LABEL}(IN|OUT)\s+", re.IGNORECASE)
INTERRUPT_CONTROL = re.compile(
    rf"^{OPTIONAL_LABEL}(DI|EI|IM|RST)\b",
    re.IGNORECASE,
)
RESERVED_STORAGE = re.compile(
    rf"^{OPTIONAL_LABEL}(DEFS|DS|RMB|BLOCK)\b",
    re.IGNORECASE,
)
DIRECTIVE = re.compile(r"^\s*(GLOBAL|EXTRN)\s+(.+?)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class AuditReport:
    failures: list[str]
    platform_symbols: frozenset[str]
    direct_writes: frozenset[str]
    direct_io: frozenset[tuple[str, str]]


def statement(raw_line: str) -> str:
    code = raw_line.split(";", 1)[0].strip()
    return re.sub(r"\s+", " ", code).upper()


def directive_symbols(paths: tuple[str, ...], directive: str) -> set[str]:
    symbols: set[str] = set()
    for relative_path in paths:
        for raw_line in (ROOT / relative_path).read_text(
            encoding="ascii",
            errors="ignore",
        ).splitlines():
            match = DIRECTIVE.match(raw_line)
            if not match or match.group(1).upper() != directive:
                continue
            symbols.update(
                symbol.strip().upper()
                for symbol in match.group(2).split(",")
                if symbol.strip()
            )
    return symbols


def audit_core() -> AuditReport:
    failures: list[str] = []
    direct_io: set[tuple[str, str]] = set()
    direct_writes: set[str] = set()
    ram_symbols = directive_symbols(("ram.z80",), "GLOBAL")

    for relative_path in CORE_SOURCES:
        path = ROOT / relative_path
        for line_number, raw_line in enumerate(
            path.read_text(encoding="ascii", errors="ignore").splitlines(),
            start=1,
        ):
            code = statement(raw_line)
            if not code:
                continue
            location = f"{relative_path}:{line_number}"

            if re.search(r"\bBDOS\b", code):
                failures.append(f"{location}: CP/M BDOS reference in core")
            if INTERRUPT_CONTROL.match(code):
                failures.append(f"{location}: interrupt-control opcode in core")
            if RESERVED_STORAGE.match(code):
                failures.append(f"{location}: reserved storage in core")

            if DIRECT_IO.match(code):
                direct_io.add((relative_path, code))

            write = DIRECT_WRITE.match(code)
            if write:
                symbol = write.group(1).upper()
                if symbol in INDIRECT_REGISTERS:
                    continue
                direct_writes.add(symbol)
                if symbol not in ram_symbols:
                    failures.append(
                        f"{location}: direct write to non-RAM symbol {symbol}"
                    )

    if direct_io != EXPECTED_DIRECT_IO:
        failures.append(
            "direct I/O set changed: "
            f"found {sorted(direct_io)}, expected {sorted(EXPECTED_DIRECT_IO)}"
        )

    externals = directive_symbols(CORE_SOURCES, "EXTRN")
    definitions = directive_symbols(CORE_SOURCES + ("ram.z80",), "GLOBAL")
    platform_symbols = frozenset(externals - definitions)
    if platform_symbols != EXPECTED_PLATFORM_SYMBOLS:
        failures.append(
            "platform symbol set changed: "
            f"found {sorted(platform_symbols)}, "
            f"expected {sorted(EXPECTED_PLATFORM_SYMBOLS)}"
        )

    layout_exports = directive_symbols(
        ("platform/msx/layout_stub.z80",),
        "GLOBAL",
    )
    missing_layout_exports = EXPECTED_PLATFORM_SYMBOLS - layout_exports
    if missing_layout_exports:
        failures.append(
            "layout stub is missing platform symbols: "
            f"{sorted(missing_layout_exports)}"
        )

    return AuditReport(
        failures=failures,
        platform_symbols=platform_symbols,
        direct_writes=frozenset(direct_writes),
        direct_io=frozenset(direct_io),
    )


def main() -> int:
    report = audit_core()
    if report.failures:
        for failure in report.failures:
            print(f"error: {failure}")
        return 1

    print(
        "verified static core boundary: "
        f"{len(report.platform_symbols)} platform symbols, "
        f"{len(report.direct_writes)} direct RAM symbols, "
        f"{len(report.direct_io)} intentional port instructions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Verify the preserved CP/Mish subtree tag and its commit mapping."""

from __future__ import annotations

import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
TAG = "upstream-cpmish-d70c643"
EXPECTED_TREE = "e9d0ae3c5f53fbd78379aa0d3f38d13f31c823f6"
EXPECTED_TIP = "d4f2987a95f194a3431930340afbf1fc69f42125"


def git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def mapped_commits() -> list[str]:
    mapping = ROOT / "docs/upstream-commit-map.tsv"
    return [
        line.split("\t", 1)[0]
        for line in mapping.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]


def main() -> int:
    try:
        tip = git("rev-parse", f"{TAG}^{{commit}}")
        tree = git("rev-parse", f"{TAG}^{{tree}}")
        history = git("rev-list", "--reverse", f"{TAG}^{{commit}}").splitlines()
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f"provenance verification failed: {error}", file=sys.stderr)
        return 1

    failures = []
    if tip != EXPECTED_TIP:
        failures.append(f"tag tip is {tip}, expected {EXPECTED_TIP}")
    if tree != EXPECTED_TREE:
        failures.append(f"tag tree is {tree}, expected {EXPECTED_TREE}")
    if history != mapped_commits():
        failures.append("extracted history does not match upstream-commit-map.tsv")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print(f"verified {TAG}: {len(history)} commits, tree {tree}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

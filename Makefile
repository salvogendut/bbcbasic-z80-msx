# SPDX-License-Identifier: BSD-3-Clause

PYTHON ?= python3

.PHONY: check help test toolcheck verify-provenance

help:
	@echo "make test               Run source-layout tests"
	@echo "make verify-provenance  Verify the preserved upstream tag and history map"
	@echo "make toolcheck          Check for the legacy CP/M build tools"
	@echo "make check              Run all checks which do not require an assembler"

test:
	$(PYTHON) -m unittest discover -s tests -v

verify-provenance:
	$(PYTHON) tools/verify_provenance.py

toolcheck:
	@command -v zmac >/dev/null || { echo "missing required tool: zmac"; exit 1; }
	@command -v ld80 >/dev/null || { echo "missing required tool: ld80"; exit 1; }
	@echo "found zmac and ld80"

check: test verify-provenance


# SPDX-License-Identifier: BSD-3-Clause

PYTHON ?= python3
ZMAC ?= zmac
LD80 ?= ld80
BUILD_DIR ?= build

.PHONY: audit-core check cpm-baseline help msx-layout test toolcheck \
	verify-provenance

help:
	@echo "make test               Run source-layout tests"
	@echo "make verify-provenance  Verify the preserved upstream tag and history map"
	@echo "make audit-core         Check the interpreter/platform boundary"
	@echo "make toolcheck          Check for the legacy CP/M build tools"
	@echo "make cpm-baseline       Build the known ADM-3A CP/M image"
	@echo "make msx-layout         Build the nonfunctional 16 KiB layout proof"
	@echo "make check              Run all checks which do not require an assembler"

test:
	$(PYTHON) -m unittest discover -s tests -v

verify-provenance:
	$(PYTHON) tools/verify_provenance.py

audit-core:
	$(PYTHON) tools/audit_core.py

toolcheck:
	@command -v "$(ZMAC)" >/dev/null || { echo "missing required tool: $(ZMAC)"; exit 1; }
	@command -v "$(LD80)" >/dev/null || { echo "missing required tool: $(LD80)"; exit 1; }
	@echo "found zmac and ld80"

cpm-baseline: toolcheck
	$(PYTHON) tools/build_cpm_baseline.py \
		--zmac "$(ZMAC)" --ld80 "$(LD80)" \
		--output-dir "$(BUILD_DIR)/cpm"

msx-layout: toolcheck
	$(PYTHON) tools/build_msx_layout.py \
		--zmac "$(ZMAC)" --ld80 "$(LD80)" \
		--output-dir "$(BUILD_DIR)/msx-layout"

check: test verify-provenance audit-core

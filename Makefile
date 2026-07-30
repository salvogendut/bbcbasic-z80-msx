# SPDX-License-Identifier: BSD-3-Clause

PYTHON ?= python3
ZMAC ?= zmac
LD80 ?= ld80
BUILD_DIR ?= build
OPENMSX ?= openmsx
OPENMSX_MACHINE ?= C-BIOS_MSX1
MSX1983 ?= ../1983/1983
MSX1983_MODELS ?= ../1983/1983-models.conf
MSX_CONSOLE_ROM = $(BUILD_DIR)/msx-console/bbcbasic_msx_console.rom
OPENMSX_SMOKE_REPORT = $(BUILD_DIR)/msx-console/openmsx-smoke.txt
MSX1983_SCREENSHOT = $(BUILD_DIR)/msx-console/1983-smoke.ppm
OPENMSX_GRAPHICS_REPORT = $(BUILD_DIR)/msx-console/openmsx-graphics.txt
OPENMSX_GRAPHICS_SCREENSHOT = $(BUILD_DIR)/msx-console/openmsx-graphics.png

.PHONY: audit-core check cpm-baseline help msx-console msx-layout test toolcheck \
	test-msx-console-1983 test-msx-console-openmsx \
	test-msx-graphics-openmsx verify-provenance

help:
	@echo "make test               Run source-layout tests"
	@echo "make verify-provenance  Verify the preserved upstream tag and history map"
	@echo "make audit-core         Check the interpreter/platform boundary"
	@echo "make toolcheck          Check for the legacy CP/M build tools"
	@echo "make cpm-baseline       Build the known ADM-3A CP/M image"
	@echo "make msx-layout         Build the nonfunctional 16 KiB layout proof"
	@echo "make msx-console        Build the 16 KiB MSX cartridge"
	@echo "make test-msx-console-openmsx  Run the guarded interactive openMSX test"
	@echo "make test-msx-console-1983     Confirm the rendered prompt in 1983"
	@echo "make test-msx-graphics-openmsx Run the BBC graphics program in openMSX"
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

msx-console: toolcheck
	$(PYTHON) tools/build_msx_console.py \
		--zmac "$(ZMAC)" --ld80 "$(LD80)" \
		--output-dir "$(BUILD_DIR)/msx-console"

test-msx-console-openmsx: msx-console
	$(OPENMSX) -machine "$(OPENMSX_MACHINE)" \
		-cart "$(abspath $(MSX_CONSOLE_ROM))" -romtype Normal \
		-command "set smoke_output {$(abspath $(OPENMSX_SMOKE_REPORT))}" \
		-script "$(abspath tools/openmsx_smoke.tcl)"
	$(PYTHON) tools/check_openmsx_smoke.py "$(OPENMSX_SMOKE_REPORT)"

test-msx-console-1983: msx-console
	$(MSX1983) --config /dev/null --models "$(MSX1983_MODELS)" \
		--model msx1 --region ntsc --cart "$(MSX_CONSOLE_ROM)" \
		--headless --unthrottled --exit-after 240 --dump-state \
		--screenshot "$(MSX1983_SCREENSHOT)"
	$(PYTHON) tools/check_1983_screenshot.py "$(MSX1983_SCREENSHOT)"

test-msx-graphics-openmsx: msx-console
	$(OPENMSX) -machine "$(OPENMSX_MACHINE)" \
		-cart "$(abspath $(MSX_CONSOLE_ROM))" -romtype Normal \
		-command "set graphics_output {$(abspath $(OPENMSX_GRAPHICS_REPORT))}; set graphics_screenshot {$(abspath $(OPENMSX_GRAPHICS_SCREENSHOT))}" \
		-script "$(abspath tools/openmsx_graphics.tcl)"
	$(PYTHON) tools/check_openmsx_graphics.py "$(OPENMSX_GRAPHICS_REPORT)"

check: test verify-provenance audit-core

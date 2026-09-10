# SPDX-License-Identifier: BSD-3-Clause
#
# Validate MSX2 bitmap modes using an open-source C-BIOS MSX2 machine. Each
# workload writes two pixels separated by exactly the distance that aliased
# through the old 14-bit main-BIOS VRAM calls, then records logical and raw
# VRAM results. Raw bytes also verify Screen 6 bit order and Screen 7 packing.

set throttle off

if {![info exists msx2_output]} {
    set msx2_output /tmp/bbcbasic-msx2.txt
}

proc run_mode {mode alias_y} {
    type_via_keybuf "10 MODE $mode\r20 GCOL 0,1:PLOT 69,500,0\r30 GCOL 0,2:PLOT 69,500,$alias_y\r40 ?&E000=POINT(500,0)\r50 ?&E001=POINT(500,$alias_y)\rRUN\r"
}

proc capture_mode {mode low_addr high_addr} {
    puts $::handle [format "MODE%d=%02X,%02X,%02X,%02X,%02X" $mode \
        [peek 0xFCAF] [debug read "VDP regs" 0] \
        [peek 0xE000] [peek 0xE001] \
        [debug read VRAM $low_addr]]
    puts $::handle [format "MODE%d_HIGH=%02X" $mode \
        [debug read VRAM $high_addr]]
}

after time 4.00 {
    set ::handle [open $::msx2_output w]
    run_mode 5 683
}
after time 8.00 {
    capture_mode 5 0x1FB2 0x5FB2
    run_mode 6 683
}
after time 12.00 {
    capture_mode 6 0x1F99 0x5F99
    run_mode 7 342
}
after time 16.00 {
    capture_mode 7 0x7F32 0xBF32
    run_mode 8 342
}
after time 20.00 {
    capture_mode 8 0x7F64 0xBF64
    type_via_keybuf "CLG\r"
}
after time 22.00 {
    puts $::handle [format "CLG8=%02X,%02X,%02X" \
        [peek 0xFCAF] [debug read "VDP regs" 0] [debug read VRAM 0xBF64]]
    close $::handle
    exit
}

after realtime 32 {
    exit
}

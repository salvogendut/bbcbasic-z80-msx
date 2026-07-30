# SPDX-License-Identifier: BSD-3-Clause
#
# Execute a real BBC BASIC graphics program and record Graphics II state.

set throttle off
set ::rom_writes 0

if {![info exists graphics_output]} {
    set graphics_output /tmp/bbcbasic-msx-graphics.txt
}
if {![info exists graphics_screenshot]} {
    set graphics_screenshot /tmp/bbcbasic-msx-graphics.png
}

proc record_graphics_rom_write {} {
    incr ::rom_writes
}

debug watchpoint create \
    -type write_mem \
    -address {0x4000 0x7fff} \
    -condition {[lindex [get_selected_slot 1] 0] == 1} \
    -command record_graphics_rom_write

after time 4.00 {
    type_via_keybuf "10 MODE 2\r20 GCOL 0,1\r30 MOVE 480,384:DRAW 800,384:DRAW 800,640:DRAW 480,640:DRAW 480,384\r40 GCOL 0,2\r50 MOVE 480,384:DRAW 800,640\r60 GCOL 0,4\r70 MOVE 480,640:DRAW 800,384\r80 GCOL 0,7\r90 PLOT 69,640,512\r95 P%=POINT(640,512)\r98 PLOT 69,1000,512\r100 GOTO 100\rRUN\r"
}

after time 90.00 {
    set pattern_nonzero 0
    for {set address 0} {$address < 0x1800} {incr address} {
        if {[debug read VRAM $address] != 0} {
            incr pattern_nonzero
        }
    }

    set handle [open $::graphics_output w]
    puts $handle "ROM_WRITES=$::rom_writes"
    puts $handle [
        format "VDP=%02X,%02X" \
            [debug read "VDP regs" 0] [debug read "VDP regs" 1]
    ]
    puts $handle "PATTERN_NONZERO=$pattern_nonzero"
    puts $handle [
        format "PATTERN=%02X,%02X,%02X,%02X,%02X" \
            [debug read VRAM 0x0867] [debug read VRAM 0x08A7] \
            [debug read VRAM 0x0B87] [debug read VRAM 0x0E67] \
            [debug read VRAM 0x0EA7]
    ]
    puts $handle [
        format "COLOUR=%02X,%02X,%02X,%02X,%02X" \
            [debug read VRAM 0x2867] [debug read VRAM 0x28A7] \
            [debug read VRAM 0x2B87] [debug read VRAM 0x2E67] \
            [debug read VRAM 0x2EA7]
    ]
    puts $handle [
        format "GRAPH_STATE=%02X,%02X,%02X" \
            [peek 0x8308] [peek 0x8309] [peek 0x830A]
    ]
    puts $handle [
        format "POINT_RESULT=%02X,%02X,%02X,%02X" \
            [peek 0x8240] [peek 0x8241] [peek 0x8242] [peek 0x8243]
    ]
    puts $handle [
        format "AFTER_POINT_PATTERN=%02X" [debug read VRAM 0x0BCF]
    ]
    close $handle
    screenshot -raw -size 320 $::graphics_screenshot
    exit
}

after realtime 90 {
    exit
}

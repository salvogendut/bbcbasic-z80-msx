# SPDX-License-Identifier: BSD-3-Clause
#
# Execute real BBC BASIC graphics programs and record Graphics II state.
# The first program exercises absolute DRAW and PLOT 69 point modes; the
# second exercises absolute PLOT 85 and relative PLOT 0 / PLOT 81 triangle
# modes from drawing-rectangle.bbc.

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

# Pattern byte address for physical pixel (x, y) in Graphics II.
proc pattern_cell {x y} {
    return [expr {($y >> 3) * 256 + ($y & 7) + (($x >> 3) << 3)}]
}

after time 4.00 {
    type_via_keybuf "10 MODE 2\r20 GCOL 0,1\r30 MOVE 480,384:DRAW 800,384:DRAW 800,640:DRAW 480,640:DRAW 480,384\r40 GCOL 0,2\r50 MOVE 480,384:DRAW 800,640\r60 GCOL 0,4\r70 MOVE 480,640:DRAW 800,384\r80 GCOL 0,7\r90 PLOT 69,640,512\r95 P%=POINT(640,512)\r98 PLOT 69,1000,512\r100 GOTO 100\rRUN\r"
}

after time 30.00 {
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
    keymatrixdown 7 4
}

after time 36.00 {
    keymatrixup 7 4
}

after time 38.00 {
    type_via_keybuf "NEW\r10 MODE 2\r20 GCOL 0,1\r30 MOVE 540,412:MOVE 540,612\r40 PLOT 85,740,612\r50 PLOT 0,-200,0:PLOT 81,0,-200\r60 GOTO 60\rRUN\r"
}

after time 90.00 {
    set rect_pattern_nonzero 0
    for {set address 0} {$address < 0x1800} {incr address} {
        if {[debug read VRAM $address] != 0} {
            incr rect_pattern_nonzero
        }
    }

    set handle [open $::graphics_output a]
    puts $handle "RECT_PATTERN_NONZERO=$rect_pattern_nonzero"
    puts $handle [
        format "RECT_GRAPH=%02X,%02X" [peek 0x8308] [peek 0x8309]
    ]
    puts $handle [
        format "RECT_PREV=%02X,%02X" [peek 0x8312] [peek 0x8313]
    ]
    puts $handle [
        format "RECT_VERTEX=%02X" [debug read VRAM [pattern_cell 108 77]]
    ]
    puts $handle [
        format "RECT_HYPO=%02X" [debug read VRAM [pattern_cell 148 77]]
    ]
    puts $handle [
        format "RECT_INSIDE=%02X" [debug read VRAM [pattern_cell 123 95]]
    ]
    puts $handle [
        format "RECT_OUTSIDE=%02X" [debug read VRAM [pattern_cell 145 95]]
    ]
    close $handle
    screenshot -raw -size 320 $::graphics_screenshot
    exit
}

after realtime 90 {
    exit
}

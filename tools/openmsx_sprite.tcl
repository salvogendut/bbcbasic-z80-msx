# SPDX-License-Identifier: BSD-3-Clause
#
# Exercise the BBC BASIC *SPRITE commands and record the resulting VDP sprite
# attribute and pattern tables. MODE 2 switches to Graphics II (the only mode
# with visible sprites), then a pattern is defined and a sprite positioned.

set throttle off

if {![info exists sprite_output]} {
    set sprite_output /tmp/bbcbasic-msx-sprite.txt
}

after time 4.00 {
    type_via_keybuf "MODE 2\r*SPRITECLR\r*SPRITEPAT 0,255,129,129,129,129,129,129,255\r*SPRITE 0,100,100,0,15\r"
}

after time 8.00 {
    set handle [open $::sprite_output w]
    puts $handle [format "PATTERN=%02X,%02X,%02X,%02X,%02X,%02X,%02X,%02X" \
        [debug read VRAM 0x3800] [debug read VRAM 0x3801] \
        [debug read VRAM 0x3802] [debug read VRAM 0x3803] \
        [debug read VRAM 0x3804] [debug read VRAM 0x3805] \
        [debug read VRAM 0x3806] [debug read VRAM 0x3807]]
    puts $handle [format "ATTR=%02X,%02X,%02X,%02X" \
        [debug read VRAM 0x1B00] [debug read VRAM 0x1B01] \
        [debug read VRAM 0x1B02] [debug read VRAM 0x1B03]]
    close $handle
    exit
}

after realtime 15 {
    exit
}

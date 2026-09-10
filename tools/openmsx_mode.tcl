# SPDX-License-Identifier: BSD-3-Clause
#
# Exercise the BBC BASIC MODE statement on an MSX1 and record the resulting
# SCRMOD work-area value after each Screen 0-3 mode switch.

set throttle off

if {![info exists mode_output]} {
    set mode_output /tmp/bbcbasic-msx-mode.txt
}

after time 4.00 {
    set ::handle [open $::mode_output w]
    type_via_keybuf "MODE 1\r"
}
after time 5.00 {
    puts $::handle "MODE1_SCRMOD=[peek 0xFCAF]"
    type_via_keybuf "MODE 3\r"
}
after time 6.00 {
    puts $::handle "MODE3_SCRMOD=[peek 0xFCAF]"
    type_via_keybuf "MODE 2\r"
}
after time 7.00 {
    puts $::handle "MODE2_SCRMOD=[peek 0xFCAF]"
    type_via_keybuf "MODE 0\r"
}
after time 8.00 {
    puts $::handle "MODE0_SCRMOD=[peek 0xFCAF]"
    close $::handle
    exit
}

after realtime 15 {
    exit
}

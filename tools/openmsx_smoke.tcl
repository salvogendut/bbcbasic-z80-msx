# SPDX-License-Identifier: BSD-3-Clause
#
# Run with a C-BIOS MSX1 machine and the console cartridge in slot A.

set throttle off
set ::rom_writes 0

if {![info exists smoke_output]} {
    set smoke_output /tmp/bbcbasic-msx-smoke.txt
}

proc record_rom_write {} {
    incr ::rom_writes
}

debug watchpoint create \
    -type write_mem \
    -address {0x4000 0x7fff} \
    -condition {[lindex [get_selected_slot 1] 0] == 1} \
    -command record_rom_write

after time 4.00 {
    type_via_keybuf "PRINT 2+3"
}

after time 4.50 {
    keymatrixdown 7 0x20
}

after time 4.60 {
    keymatrixup 7 0x20
}

after time 5.00 {
    type_via_keybuf "2\rPRINT SQR(2)\rPRINT \"RAIN\";\"BIOS\"\r10 FOR I=1 TO 3\r20 PRINT I;\r30 NEXT\rRUN\r*CAT\r"
}

after time 8.00 {
    type_via_keybuf "TIME=1000\rPRINT TIME>=1000\rPRINT INKEY(1)\r"
}

after time 14.00 {
    set handle [open $::smoke_output w]
    puts $handle "ROM_WRITES=$::rom_writes"
    puts $handle [get_screen]
    close $handle
    exit
}

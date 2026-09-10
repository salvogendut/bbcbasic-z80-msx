# SPDX-License-Identifier: BSD-3-Clause
#
# Exercise the BBC BASIC SOUND statement and record the resulting PSG state.
# Three SOUND commands program tone channels A and C and the noise channel,
# then the report captures the PSG registers for the Python checker.

set throttle off

if {![info exists sound_output]} {
    set sound_output /tmp/bbcbasic-msx-sound.txt
}

after time 4.00 {
    type_via_keybuf "SOUND 1,-15,100,0\rSOUND 3,-10,50,0\rSOUND 0,-8,200,0\r"
}

after time 8.00 {
    set handle [open $::sound_output w]
    puts $handle [format "TONE_A_PERIOD=%02X,%02X" \
        [debug read "PSG regs" 0] [debug read "PSG regs" 1]]
    puts $handle [format "TONE_C_PERIOD=%02X,%02X" \
        [debug read "PSG regs" 4] [debug read "PSG regs" 5]]
    puts $handle [format "VOL_A=%02X" [debug read "PSG regs" 8]]
    puts $handle [format "VOL_C=%02X" [debug read "PSG regs" 10]]
    puts $handle [format "NOISE_PERIOD=%02X" [debug read "PSG regs" 6]]
    puts $handle [format "MIXER=%02X" [debug read "PSG regs" 7]]
    close $handle
    exit
}

after realtime 15 {
    exit
}

# SPDX-License-Identifier: BSD-3-Clause
#
# Exercise the BBC BASIC SOUND and ENVELOPE statements and record the PSG
# state. Three SOUND commands program tone channels A and C and the noise
# channel; an ENVELOPE followed by SOUND on channel B then programs the
# hardware envelope. The report captures both phases for the Python checker.

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

    type_via_keybuf "ENVELOPE 1,5,-1,0,0,0,0,0,0,-10,15,-10,0,0\rSOUND 2,-15,150,0\r"
}

after time 12.00 {
    set handle [open $::sound_output a]
    puts $handle [format "ENV_PERIOD=%02X,%02X" \
        [debug read "PSG regs" 11] [debug read "PSG regs" 12]]
    puts $handle [format "ENV_SHAPE=%02X" [debug read "PSG regs" 13]]
    puts $handle [format "TONE_B_PERIOD=%02X,%02X" \
        [debug read "PSG regs" 2] [debug read "PSG regs" 3]]
    puts $handle [format "VOL_B=%02X" [debug read "PSG regs" 9]]
    close $handle
    exit
}

after realtime 20 {
    exit
}

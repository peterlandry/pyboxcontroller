from RockBandDrums import RockBandDrumDevice

MIDI_SIGNALS = {
    "BASS_DRUM": 36,
    "GREEN_DRUM": 41,
    "RED_DRUM": 40,
    "BLUE_DRUM": 45,
    "YELLOW_DRUM": 44
}

if __name__ == '__main__':
    import rtmidi, time
    midiout = rtmidi.RtMidiOut()


    midiout.openVirtualPort("Rock Band Drums")
    note = 44
    def keyPressed(key_name):
        midiout.sendMessage(144,MIDI_SIGNALS[key_name],90)

    def keyReleased(key_name):
        midiout.sendMessage(128,MIDI_SIGNALS[key_name],40)
    
    drums = RockBandDrumDevice()
    if not drums.foundDevice():
        print "Drums not found"
        exit()
    drums.keyPressed += keyPressed
    drums.keyReleased += keyReleased
    while 1:
        drums.updateKeysPressed()
#!/usr/bin/env python

import usb

class RockBandDrumDevice(object):
    filename = "002-1bad-0003-ff-ff"
    interfaceSubclass = 93
    interfaceProtocol = 1
    endpointNumber = 1
    
    NONE = 0 #(0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    BASS_DRUM = 1 #(0, 20, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    GREEN_DRUM = 16 #(0, 20, 0, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    RED_DRUM = 32 #(0, 20, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    BLUE_DRUM = 64 #(0, 20, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    YELLOW_DRUM = 128 #(0, 20, 0, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


    def __init__(self):
        self.device = self.interface = self.config = None
        busses = usb.busses()
        for bus in busses:
            devices = bus.devices
            for dev in devices:
                if dev.filename == self.filename:
                    self.device = dev
                    for config in self.device.configurations:
                        for intf in config.interfaces:
                            for alt in intf:
                                if alt.interfaceSubClass == self.interfaceSubclass and alt.interfaceProtocol == self.interfaceProtocol:
                                    self.interface = alt
                                    self.config = config
        if self.foundDevice():
            self.handle = self.device.open()
            self.handle.claimInterface(self.interface)
            self.handle.setConfiguration(self.config)
    
    def foundDevice(self):
        if self.device and self.interface and self.config:
            return True
        return False
    
    def _read(self):
        if not self.foundDevice():
            return None
        return self.handle.bulkRead(self.endpointNumber, 32)
    
    def buttonsPressed(self):
        data = self._read()
        pressedButtons = []
        if len(data) == 20:
            button_data = data[3]
            if button_data & self.BASS_DRUM:
                pressedButtons.append(self.BASS_DRUM)
            if button_data & self.GREEN_DRUM:
                pressedButtons.append(self.GREEN_DRUM)
            if button_data & self.RED_DRUM:
                pressedButtons.append(self.RED_DRUM)
            if button_data & self.BLUE_DRUM:
                pressedButtons.append(self.BLUE_DRUM)        
            if button_data & self.YELLOW_DRUM:
                pressedButtons.append(self.YELLOW_DRUM)
        return tuple(pressedButtons)
        
drums = RockBandDrumDevice()

if not drums.foundDevice():
    print "Drums not found"

countdown = 100
while countdown > 0:
    pressed = drums.buttonsPressed()
    if len(pressed) > 0:
        print pressed
    countdown -= 1
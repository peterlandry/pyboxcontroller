#!/usr/bin/env python

import usb

# http://www.valuedlessons.com/2008/04/events-in-python.html
# TODO: is there a more pythonic way to handle this?
class Event:
    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount

class RockBandDrumDevice(object):
    filename = "003-1bad-0003-ff-ff"
    interfaceSubclass = 93
    interfaceProtocol = 1
    endpointNumber = 1
    
    KEYS = (
        ("NONE", 0), #(0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ("BASS_DRUM", 1), #(0, 20, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ("GREEN_DRUM", 16), #(0, 20, 0, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ("RED_DRUM", 32), #(0, 20, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ("BLUE_DRUM", 64), #(0, 20, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ("YELLOW_DRUM", 128), #(0, 20, 0, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    )

    def __init__(self):
        self.device = self.interface = self.config = None
        self.lastPressedKeys = ()
        self.keyPressed = Event()
        self.keyReleased = Event()
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
        return self.handle.bulkRead(self.endpointNumber, 32, 10000)
    
    def _createButtonEvents(self, newPressedKeys = (), lastPressedKeys = ()):
        # new keys that are pressed
        for key in newPressedKeys:
            if not key in lastPressedKeys:
                self.keyPressed(key)
        
        # keys that are released
        for key in lastPressedKeys:
            if not key in newPressedKeys:
                self.keyReleased(key)
    
    def updateKeysPressed(self):
        data = self._read()
        pressedKeys = []
        if len(data) == 20 and data[0] == 0:
            button_data = data[3]
            for key in self.KEYS:
                key_name = key[0]
                key_data = key[1]
                if button_data & key_data:
                    pressedKeys.append(key[0])
        self._createButtonEvents(tuple(pressedKeys), self.lastPressedKeys)
        self.lastPressedKeys = tuple(pressedKeys)
        return tuple(self.lastPressedKeys)
    
    def close(self):
        if self.foundDevice():
            self.handle.releaseInterface()

if __name__ == '__main__':
    drums = RockBandDrumDevice()

    if not drums.foundDevice():
        print "Drums not found"

#    try:
    countdown = 100
    while countdown > 0:
        drums.updateKeysPressed()
        countdown -= 1
#    except:
#        drums.close()
# ! /usr/bin/env python
# coding=utf-8

from interface.i2c_bridge.tca9548a import *
import platform


class allcoation:

    @staticmethod
    def bridge_allcoation(emulator, logging):
        
        if "rpi" in platform.platform():
            # rpi support 2 channels of i2c on gpio header pins
            from interface.i2c_bridge.rpi import rpi
            emulator = "rpi"
            channel = 1
            i2c = rpi(channel=channel)

        elif "mcp" in emulator:
            from interface.i2c_bridge.mcp2221 import mcp2221 as mcp
            i2c = mcp()

        elif ("ch341" in emulator) or ("341" in emulator):
            from interface.i2c_bridge.ch341 import ch341
            i2c = ch341(logging=logging) # some registers are auto-cleared after operation
        
        elif ("ft4222" in emulator) or ("4222" in emulator):
            from interface.i2c_bridge.ft4222 import ft4222
            i2c = ft4222()

        elif "cp2112" in emulator:
            from interface.i2c_bridge.cp2112 import cp2112
            i2c = cp2112(retry=1, logging=logging, led=True)
        
        return i2c
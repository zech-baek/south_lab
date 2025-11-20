# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib

try:
    # try to use __file__
    bridge_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        bridge_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        bridge_dir = os.getcwd()

root_dir = pathlib.Path(bridge_dir).parent


import ctypes, ctypes.util
from ctypes import *

import platform, time


if "32bit" in platform.architecture():
    dll = f"{root_dir}/sc_approval/ch341_x32.dll"
else:
    dll = f"{root_dir}/sc_approval/ch341_x64.dll"


class ch341(object):
    
    '''
    before : use the 8bit_write address for i2c device
    after  : use the 7bit_write address for i2c device
    e.g.,
        - HL7133 has a 0x5e i2c address (7bit)
        - to use the ch341 class, address shold be 0x5e<<1 = 0xbc
    '''
    
    index = 0
    value= ctypes.c_int(0)

    if "macOS" in platform.platform():
        dll = cdll.LoadLibrary(dll)
    else:
        dll = windll.LoadLibrary(dll)

    OpenDev = dll.CH341OpenDevice
    OpenDev.argtype = [ctypes.c_int]
    OpenDev.restype = ctypes.POINTER(ctypes.c_int)
    
    CloseDev = dll.CH341CloseDevice
    CloseDev.argtype = [ctypes.c_int]
    CloseDev.restype = None
    
    CH341ReadI2C = dll.CH341ReadI2C
    CH341ReadI2C.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
    CH341ReadI2C.restype = bool

    CH341WriteI2C = dll.CH341WriteI2C
    CH341WriteI2C.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int,  ctypes.c_int]
    CH341WriteI2C.restype = bool            
    
    
    def __init__(self, readback=False, logging=False):             
        
        self.index    = 0
        self.readback = readback
        self.value    = ctypes.c_int(0)
        self.logging  = logging
        self.OpenDev(0)
        self.i2c_speed(value=1)
        
        
    def OpenDevice(self):
        self.OpenDev(0)
        
        
    def CloseDevice(self):
        self.CloseDev(0)
        
        
    def i2c_read(self, i2c_address, reg):
        
        # 7bit address style
        time.sleep(0.01)
        if self.CH341ReadI2C(self.index, i2c_address, reg, ctypes.byref(self.value)) == True:
            ret = self.value.value
            return ret
        else:
            '''
            no way to distinguish the ACK and NACK
            therefore, always return the 0xff even though i2c address is wrong
            else loop will not run in this implementation
            '''
            pass
        

    def i2c_write(self, i2c_address, reg, w_val):
        
        # 7bit address style
        time.sleep(0.01)
        self.CH341WriteI2C(self.index, i2c_address, reg, w_val)


    def smbus_scan(self):
        
        '''
        it always returs the 0xff even though there's nack
        if the response of first register is not 0xff, return it as the i2c address
        '''
        ret = []
        for i in range(0x2, 0x70):
            temp_store = []
            for n in range(4):
                value = self.i2c_read(i, n)
                temp_store.append(value)
            if any(item != 0xff for item in temp_store):
                ret.append(i)
            else:
                pass
        return ret


    def _write(self, i2c_address, addr, data):
        
        obuf = (c_byte * 3)()
        ibuf = (c_byte * 1)()
        obuf[0] = i2c_address<<1 # need 8bit style address
        obuf[1] = addr
        obuf[2] = data & 0xff
        
        if self.dll.CH341StreamI2C(self.index, 3, obuf, 0, ibuf):
            pass
        else:
            print(f"write transaction failed")
            
            
    def _read(self, i2c_address, addr):
        
        obuf = (c_byte * 2)()
        ibuf = (c_byte * 1)()
        obuf[0] = i2c_address<<1 # need 8bit style address
        obuf[1] = addr
        
        if self.dll.CH341StreamI2C(self.index, 2, obuf, 1, ibuf):
            return ibuf[0] & 0xff
        else:
            print(f"read transaction failed")


    def i2c_speed(self, value):
        
        scl_speed = {
            0 : "20kHz",
            1 : "100kHz",
            2 : "400kHz",
            3 : "750kHz"
        }
    
        if self.dll.CH341SetStream(self.index, value):
            print(f"initialized the ch341 with default {scl_speed[value]} clock speed")
        else:
            print(f"failed to set the i2C speed")
    

    def i2c_write_bulk(self, slave, addr, length, data):

        obuf = (c_byte * (2 + length))()
        ibuf = (c_byte * 1)()

        for i in range(2 + length):
            if (i == 0):
                obuf[i] = slave << 1 # need 8bit style address
            elif (i==1):
                obuf[i] = addr
            else:
                obuf[i] = data[i-2] & 0xff
        
        if self.dll.CH341StreamI2C(self.index, 2 + length, obuf, 0, ibuf):
            time.sleep(self.delay)
            return True
        else:
            print("Please Check dongle connection")
            return False           
    
    
    def i2c_read_bulk(self, slave, addr, length):

        result = []
        index = 0
        obuf = (c_byte * 2)()
        ibuf = (c_byte * length)()
        
        obuf[0] = slave << 1 # need 8bit style address
        obuf[1] = addr

        if self.dll.CH341StreamI2C(self.index, 2, obuf, length, ibuf):
            for i in ibuf:
                ret = i & 0xff
                print("addr[", hex(addr + index),"], = [", hex(ret), "]")
                result.insert(index, i)
                index = index +1
            time.sleep(self.delay)
            return result
        else:
            return 0
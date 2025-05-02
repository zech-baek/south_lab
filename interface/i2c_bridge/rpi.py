from smbus import SMBus as smb
from interface.cui_logger import logger as log
from interface.cui_colors import color
import sys


class rpi(object):
    
    def __init__(self, channel=1):
        
        self._channel = channel
        self._i2c = smb(self._channel)
        
    
    def i2c_read(self, i2c_address, reg_addr):
        
        ret = self._i2c.read_byte_data(i2c_address, reg_addr)
        # log.infoLog(f"[{i2c_address:#04x} read] {reg_addr:#04x}, return {ret:#04x}")
    
    
    def i2c_write(self, i2c_address, reg_addr, reg_val):

        self._i2c.write_byte_data(i2c_address, reg_addr, reg_val)
        # log.infoLog(f"[{i2c_address:#04x} write] {reg_addr:#04x}, value {reg_val:#04x}")


    def smbus_scan(self):
        
        ret = []
        for i in range(0x80):
            try:
                self._i2c.read_byte_data(i, 0)
                ret.append(i)
            except:
                pass
        return ret
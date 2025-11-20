from interface.cui_logger import logger as log
from interface.cui_colors import color
from tabulate import tabulate as tb
from time import sleep as delay



'''
tca9548a
- sequence
1. select the tca9548 channel
    - e.g. ic.i2c_h.write(0x70<<1, dummy, channel)
    - tca9548 recoginizes the last byte as an actual channel selection value
    - channel configuration
        - channel 0 : 0b0000_0001
        - channel 1 : 0b0000_0010
        - channel 2 : 0b0000_0100
            ...
        - channel 7 : 0b1000_0000
2. data transaction
    - e.g. ic.i2c_h.write(0x0c<<1, 0x04, 0x22)
'''


class function:
    
    def __init__(self, protocol, channel) -> None:
        
        self._handler = protocol
        self._channel = channel
        
        self._dummy = 0
        self._delay = 0.1
        self.i2c_address = None
    
    
    @property
    def enable(self):
        
        self._handler.channel_selection = self._channel
        self._handler.selected_channel = self._channel
        delay(self._delay)
        # log.forcedLog(f"select i2c channel #{self._channel}")
    
    
    @property
    def set_i2c_address(self):
        log.forcedLog(f"channe {self._channel} is configured via i2c address {self.i2c_address:#04x}")
    
    
    @set_i2c_address.setter
    def set_i2c_address(self, address):
        
        self.i2c_address = address
        log.infoLog(f"channe {self._channel} is configured to i2c address {self.i2c_address:#04x}")
    
    
    '''
    distinguish the read and write block with our without the slave address
    - i2c_read/write : require the slave address, register, value
    - read/write : require the register, value
    '''
    
    def i2c_write(self, i2c_address, reg_addr, reg_val):
        
        if self._handler.selected_channel != self._channel:
            self.enable
        self._handler.send(i2c_address, reg_addr, reg_val)
    
    
    def i2c_read(self, i2c_address, reg_addr):

        if self._handler.selected_channel != self._channel:
            self.enable
        ret = self._handler.query(i2c_address, reg_addr)
        return ret
    
    
    @property
    def write(self):
        log.forcedLog(f"require the correct format (e.g. address, register, value)")
    
    
    @write.setter
    def write(self, *args):
        
        register   = args[0][0]
        value      = args[0][1]
        if self._handler.selected_channel != self._channel:
            self.enable
        self._handler.send(self.i2c_address, register, value)
    
    
    def read(self, *args):

        register   = args[0]
        if self._handler.selected_channel != self._channel:
            self.enable
        ret = self._handler.query(self.i2c_address, register)
        return ret



class tca9548:
    
    def __init__(self, i2c_h=None, i2c_a=None) -> None:
        
        if i2c_a == None:
            # tca9548 uses 8bit address type, but 7 bit is used in this code
            # a0 ~ 2 pins are grounded
            self.i2c_address = 0x70
        else:
            self.i2c_address = i2c_a
        
        self._i2c_h = i2c_h # i2c handler
        self._delay = 0.1   # delay between the channel transition
        self._dummy = 0     # tca9548 recognize the last byte only for the channel selection
        self.selected_channel = None
        
        for ch in range(8):
            self.__dict__[f"ch{ch}"] = function(self, ch)
        
        self.init_device
    
    
    @property
    def channel_selection(self):
        log.infoLog(f"channel {self.selected_channel} is activated")
    
    
    @channel_selection.setter
    def channel_selection(self, channel):
        
        self.send((self.i2c_address), (1<<channel), (1<<channel))
        self.selected_channel = channel
        log.infoLog(f"tca9548 activate the channel {channel}")
    
    
    @property
    def init_device(self):
        
        self.send(self.i2c_address, self._dummy, (1<<0))
        self.selected_channel = 0
        log.forcedLog(f"{color.blue}initialize tca9548 and activate channel 0 by default{color.end}")
    
    
    def send(self, *args):
        
        secondary_address = args[0] # require 7bit format
        register_address  = args[1]
        register_value    = args[2]
        self._i2c_h.i2c_write(secondary_address, register_address, register_value)
    
    
    def query(self, *args):
        
        secondary_address = args[0] # require 7bit format
        register_address  = args[1]
        ret = self._i2c_h.i2c_read(secondary_address, register_address)
        return ret
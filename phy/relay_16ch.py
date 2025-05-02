from interface.cui_logger import logger as log
from interface.cui_colors import color
from tabulate import tabulate as tb
from time import sleep as delay

import tabulate, sys



'''
pcf8575 data format

i2c write (i2c address, low channel 2byte, high channel 2byte)
- initial state : 0xffff
- low channel  == register address
- high channel == register value

'''


def log_wrapping(header, message, is_logging=True):
    
    msg = f"[{header} {sys._getframe(2).f_code.co_name}] {message}"
    log.forcedLog(msg) if is_logging else log.debugLog(msg)



class function:
    
    def __init__(self, protocol, channel) -> None:
        
        self._handler = protocol
        self._channel = channel
        self._gpio    = channel - 1
    
    
    def state_update(self, low, high):
        
        self._handler.low_state  = low
        self._handler.high_state = high
    
    @property
    def enable(self):
        
        if self._channel < 9: # low channel
            low_ch  = self._handler.low_state & ~(0x1 << self._gpio) # 0 is switch on control
            high_ch = self._handler.high_state
        else:
            low_ch  = self._handler.low_state
            high_ch = self._handler.high_state & ~(0x1 << (self._gpio-8))
            
        self._handler.i2c_write = low_ch, high_ch
        self.state_update(low_ch, high_ch)
        # log.forcedLog(f"low {low_ch:#x} high {high_ch:#x}")
        log.forcedLog(f"relay channel {self._channel} on : low {low_ch:#04x}, high {high_ch:#04x}")
        delay(1)
    
    
    @property
    def disable(self):
        
        if self._channel < 9: # low channel
            low_ch = self._handler.low_state | (0x1 << self._gpio) # 0 is switch on control
            high_ch = self._handler.high_state
        else:
            low_ch  = self._handler.low_state
            high_ch = self._handler.high_state | (0x1 << (self._gpio-8))
            
        self._handler.i2c_write = low_ch, high_ch
        self.state_update(low_ch, high_ch)
        # log.forcedLog(f"low {low_ch:#x} high {high_ch:#x}")
        log.forcedLog(f"relay channel {self._channel} off : low {low_ch:#04x}, high {high_ch:#04x}")
        delay(1)


class relay_box:
    
    def __init__(self, i2c_h=None, i2c_a=0x27):
        
        self.i2c_h = i2c_h.get_i2c_handler()
        self.i2c_a = i2c_a
        self.delay = 0.5
        
        self.logging = True
        
        self.low_state  = 0xff # low 2 byte for p0~p7
        self.high_state = 0xff # high 2 byte for p8~p15
        
        for ch in range(1, 17):
            self.__dict__[f"ch{ch}"] = function(self, ch)
        
        log_wrapping(
            self.__class__.__name__,
            f"{color.blue}initialize pcf8575 to be off state for all channels{color.end}",
            self.logging
            )
        
        log_wrapping(
            self.__class__.__name__,
            f"low channel 2 byte should be placed before high channel 2 byte for pcf8575",
            self.logging
            )
        
        # self.i2c_write = 0xff, 0xff
    
    
    @property
    def set_delay(self):
        
        log_wrapping(
            self.__class__.__name__,
            f"delay time : {self.delay}",
            self.logging
            )
    
    
    @set_delay.setter
    def set_delay(self, delay):
        
        self.delay = delay
        log_wrapping(
            self.__class__.__name__,
            f"set delay time : {self.delay}",
            self.logging
            )
    
    
    @property
    def init_channels(self):
        
        self.low_state  = 0xff
        self.high_state = 0xff
        self.i2c_write = self.low_state, self.high_state
        self.status
        
        log_wrapping(
            self.__class__.__name__,
            f"disable all channels",
            self.logging
            )
        
        
    @property
    def status(self):
        
        ret_map = list()
        ret_map.append(["channel", "state"])
        
        for ch in range(8):
            channel_state = (self.low_state >> ch) & 0x1
            if channel_state:
                ret_map.append([f"low channel  # {ch+1}", "off"])
            else:
                ret_map.append([f"low channel  # {ch+1}", "on"])
        
        for ch in range(8):
            channel_state = (self.high_state >> ch) & 0x1
            if channel_state:
                ret_map.append([f"high channel # {ch+9}", "off"])
            else:
                ret_map.append([f"high channel # {ch+9}", "on"])
        
        print(tabulate.tabulate(ret_map, headers="firstrow"))
        print(f"\n")
    
    
    @property
    def enable(self):
        print(f"require the channels want to enable : e.g. self.enable = 1, 3, 6, 4")
    
    
    @enable.setter
    def enable(self, *args):
        
        for ch in list(range(len(args[0]))):
            if args[0][ch] < 9: # low channel
                low_ch  = self.low_state & ~(0x1 << args[0][ch]-1) # 0 is switch on control
                high_ch = self.high_state
            else:
                low_ch  = self.low_state
                high_ch = self.high_state & ~(0x1 << args[0][ch]-9)
                
            self.i2c_write  = low_ch, high_ch
            self.low_state  = low_ch
            self.high_state = high_ch
            log.forcedLog(f"relay channel {args[0][ch]} on")
    
    
    @property
    def disable(self):
        print(f"require the channels want to enable : e.g. self.enable = 1, 3, 6, 4")
    
    
    @disable.setter
    def disable(self, *args):
        
        for ch in list(range(len(args[0]))):
            if args[0][ch] < 9: # low channel
                low_ch  = self.low_state | (0x1 << args[0][ch]-1) # 0 is switch on control
                high_ch = self.high_state
            else:
                low_ch  = self.low_state
                high_ch = self.high_state | (0x1 << args[0][ch]-9)
                
            self.i2c_write  = low_ch, high_ch
            self.low_state  = low_ch
            self.high_state = high_ch
            log.forcedLog(f"relay channel {args[0][ch]} off")
    
    
    @property
    def i2c_write(self):
        log.forcedLog("2x 2byte channel values should be provided (e.g. self.i2c_write = 0xaa, 0xbb)")
    
    
    @i2c_write.setter
    def i2c_write(self, *args):
        
        len_args = len(args)
        if len_args == 1:
            low_ch  = args[0][0]
            high_ch = args[0][1]
            self.i2c_h.i2c_write(self.i2c_a, low_ch, high_ch)
        else:
            log.errorLog(f"input byte length is not correct, require 2 byte for low and high channels respectively")
        delay(self.delay)
    
    
    def set_channel(self, channel:int, logic:int):
        
        gpio = channel - 1
        
        if logic:
            if channel < 9: # low channel
                low_ch  = self.low_state & ~(0x1 << gpio) # 0 is switch on control
                high_ch = self.high_state
            else:
                low_ch  = self.low_state
                high_ch = self.high_state & ~(0x1 << (gpio-8))
            
            self.i2c_write = low_ch, high_ch
            self.low_state  = low_ch
            self.high_state = high_ch
            log.forcedLog(f"relay channel {channel} on")
            delay(1)
    
        else:
            if channel < 9: # low channel
                low_ch = self.low_state | (0x1 << gpio) # 0 is switch on control
                high_ch = self.high_state
            else:
                low_ch  = self.low_state
                high_ch = self.high_state | (0x1 << (gpio-8))
                
            self.i2c_write = low_ch, high_ch
            self.low_state  = low_ch
            self.high_state = high_ch
            # log.forcedLog(f"low {low_ch:#x} high {high_ch:#x}")
            log.forcedLog(f"relay channel {channel} off")
            delay(1)
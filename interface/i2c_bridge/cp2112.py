# support HID
# configurable GPIO as input / output / open drain / push pull
# on chip 3.45V regulator
# read / write timeout : 0 ~ 1000ms (0 means no timeout), data transfer will be automaticall canceled
# SCL low timeout : disable or enable, 25ms duration
# retry counter : 0 ~ 1000
# 8 GPIOs and clock output from 48MHz to 94MHz
# toggle LED
# support I2C clock : 10kHz ~ 400kHz
# integrated VIO input
# typical address read
#   start + 7bit slave address + write(0) --> ACK
#   --> logical address --> ACK
#   --> repeated start --> 7bit slave address + read(1)
#   --> ACK --> data byte (generate clk) --> NACK --> stop
# alternate GPIO function : GPIO0=Tx LED toggle, GPIO1=Tx LED toggle, GPIO7=CLK output
# GPIO7 clock frequency = 48MHz / (2x clock divider)
# VID = 0x10C4
# PID = 0xEA90

# referenced from
# https://github.com/artizirk/cp2112/blob/master/main.py


import hid, sys

from time import sleep as delay
from interface.cui_logger import logger as log


def log_wrapping(header, message, is_logging):
    
    if is_logging:
        log.forcedLog(f"[{header} {sys._getframe(2).f_code.co_name}] {message}")
    else:
        log.debugLog(f"[{header} {sys._getframe(2).f_code.co_name}] {message}")


class parameter:

    # original vid=0x10c4, pid=0xea90

    vendor_id        = 0x2100
    product_id       = 0xffff
    serial_number    = "00AE1450"
    manufacturing_id = "Silicon Laboratories"
    product_string   = "CP2112 HID USB-to-SMBus Bridge"

    gpio_direction = 0x00   # 0 - input, 1 - output
    gpio_pushpull  = 0x00   # 0 - open-drain, 1 - push-pull
    gpio_special   = 0x00   # only on bits 0-2,  0 standard gpio, 1 special function as LED, CLK out
    gpio_clockdiv  = 1   # should be 24Mhz on GPIO7, equation: 48Mhz / (2 * clockdiv)

    led_gpio_direction = 0x83
    # led_gpio_pushpull  = 0xFF
    led_gpio_pushpull  = 0xFC # set the gpio0/1_led to open-drain
    # led_gpio_special   = 0xFF
    led_gpio_special   = 0x00 # set the gpio0/1/7 to GPIO type


class cp2112:

    def __init__(self, retry=1, logging=False, led=True):

        self.logging = logging
        self.retry   = retry
        self.led     = led
        
        self.h = hid.device()
        hid_list = hid.enumerate()
        for dev in iter(hid_list):
            if "Silicon Laboratories" in dev["manufacturer_string"]:
                if "CP2112" in dev["product_string"]:
                    vid = dev["vendor_id"]
                    pid = dev["product_id"]

        # self.h.open_path(hid.enumerate(parameter.vendor_id, parameter.product_id)[0]["path"])
        self.h.open_path(hid.enumerate(vid, pid)[0]["path"])
        log_wrapping("cp2112", f"initiate the device on hid", self.logging)

        # self.hid_send([0x03, 0xFF, 0x00, 0x00, 0x00]) # set gpio to open drain
        self.hid_send([0x03, 0xFF, 0x00]) # set gpio to open drain
        self.hid_send([0x02,                          # report ID
                                    parameter.led_gpio_direction,  # direction (gpio7_clk, gpio1_rxt and gpio0_txt are output)
                                    parameter.led_gpio_pushpull,   # push-pull type
                                    parameter.led_gpio_special,    # special feature
                                    parameter.gpio_clockdiv])      # clock divider

        # report ID : 0x04 (set gpio value)
        # offset : total 2bytes
        # offset_1 : latch value
        # offset_2 : latch mask (if set to 0, the new value will not be set even if the in is configured as an output pin)

        # currently, gpio0/1 set to open-drain
        # setting the bit to 1 in offset_1 of 0x04 means off the led on corresponding gpio
        for _ in range(3):
            self.h.send_feature_report([0x04, 0b0000_0001, 0b0000_0011]) # turn off gpio_0 led --> index 1 = output status, index 2 = gpio
            delay(0.2)
            self.h.send_feature_report([0x04, 0b0000_0010, 0b0000_0011]) # turn off gpio_1 led
            delay(0.2)
        self.h.send_feature_report([0x04, 0x03, 0b0000_0011])
        
        version_info = self.hid_get(0x05, 3) # report id 0x05, 2byte read (+id)
        log_wrapping("cp2112", f"device part number : {version_info[1]:#x}", self.logging)
        log_wrapping("cp2112", f"device version : {version_info[2]}", self.logging)

        self.smbus_parameter(display=self.logging)


    def hid_send(self, packet):
        
        if self.led:
            self.h.send_feature_report([0x04, 0x02, 0b0000_0011]) # blink Tx leds
        self.h.send_feature_report(packet)
        if self.led:
            self.h.send_feature_report([0x04, 0x03, 0b0000_0011]) # blink Tx leds

    
    def hid_get(self, repori_id, size):

        if self.led:
            self.h.send_feature_report([0x04, 0x01, 0b0000_0011]) # blink Rx leds
        ret = self.h.get_feature_report(repori_id, size)
        if self.led:
            self.h.send_feature_report([0x04, 0x03, 0b0000_0011]) # blink Rx leds
        return ret
    

    def hid_write(self, packet):
        
        if self.led:
            self.h.send_feature_report([0x04, 0x02, 0b0000_0011]) # blink Tx leds
        self.h.write(packet)
        if self.led:
            self.h.send_feature_report([0x04, 0x03, 0b0000_0011]) # blink Tx leds

    
    def hid_read(self, size):

        if self.led:
            self.h.send_feature_report([0x04, 0x01, 0b0000_0011]) # blink Rx leds
        ret = self.h.read(size)
        if self.led:
            self.h.send_feature_report([0x04, 0x03, 0b0000_0011]) # blink Rx leds
        return ret

    
    def gpio_7(self, output):
        
        if output == 1:
            self.h.send_feature_report([0x04, 0x80, 0x80])
        elif output == 0:
            self.h.send_feature_report([0x04, 0x00, 0x80])
        else:
            log_wrapping("cp2112", f"wrong logic for gpio 8", 1)
    

    def smbus_parameter(self, display=True):

        # report ID : 0x06 (SMBus configuration)
        # offset : total 13bytes
        # offsets_1~4 : clock speed
        # offset_5 : device address (default 0x02)
        # offset_6 : auto send read(0=disable, 1=enable)
        # offsets_7~8  : write timeout (0x0000=no timeout, 0~1000ms)
        # offsets_9~10 : read timeout (0x0000=no timeout, 0~1000ms)
        # offset_11 : scl low timeout (0=disable, 1=enable)
        # offsets_12~13 : retry time (0x0000=no limit, 0~1000 retries)

        preset_cfg = self.hid_get(0x06, 14)
        preset_cfg[7:9]  = [0x00, 0xff] # 255ms for write timeout
        preset_cfg[9:11] = [0x00, 0xff] # 255ms for read timeout
        preset_cfg[11]   = 0x01
        preset_cfg[13]   = self.retry
        self.hid_send(preset_cfg)

        smbus_cfg = self.hid_get(0x06, 14)
        clock_speed = smbus_cfg[4] + (smbus_cfg[3]<<8) + (smbus_cfg[2]<<16) + (smbus_cfg[1]<<24)
        write_timeout = smbus_cfg[8] + (smbus_cfg[7]<<8)
        read_timeout = smbus_cfg[10] + (smbus_cfg[9]<<8)
        retry_time = smbus_cfg[13] + (smbus_cfg[12]<<8)

        log_wrapping("cp2112", f"clock speed : {clock_speed/1000:.1f}kHz", display)
        log_wrapping("cp2112", f"auto send read : {bool(smbus_cfg[6])}", display)
        log_wrapping("cp2112", f"write timeout : {write_timeout}ms", display)
        log_wrapping("cp2112", f"read timeout : {read_timeout}ms", display)
        log_wrapping("cp2112", f"scl low timeout : {bool(smbus_cfg[11])}", display)
        log_wrapping("cp2112", f"retry time : {retry_time}", display)


    def close(self):

        # report ID : 0x01 (reset device)
        # offset : total 1 byte
        # offset_1 : 0x01 to re-enumeration
        self.hid_send([0x01, 0x01])

    
    def i2c_speed(self, clk=400):

        # configurable range : 20kHz to 400kHz
        # report id : 0x06
        # offset_1~4 : 0bus clock value (example for 100,000Hz=0x000186a0 : 00h, 01h, 86h, a0h)
        # e.g., cp.i2c_speed(50)

        target = int(clk * 1000)
        index_1 = (target>>24) & 0xff
        index_2 = (target>>16) & 0xff
        index_3 = (target>>8)  & 0xff
        index_4 = target       & 0xff
        
        preset_cfg = self.hid_get(0x06, 14)
        preset_cfg[1:5] = [index_1, index_2, index_3, index_4]
        self.hid_send(preset_cfg)
        log_wrapping("cp2112", f"clock speed : {clk}kHz", self.logging)
    

    def smbus_scan(self):
        
        ret = list()

        # report ID : 0x10 (data read request)
        # offset : total 3 bytes
        # offset_1 : slave address in 8 bit format, lsb is read/write bit, but must be zero
        # offset_2~3 : 1 ~ 512 (0x0200) byte

        for addr in range(0x02, 0x7f):
            self.hid_write([0x10, addr<<1, 0x00, 0x01])
            status = self.i2c_status(logging=False)

            if status[1]==0x01:
                if status[2]==0x00:
                    message = f"[{addr:#04x}] status_0={status[1]}, address acked"
                    ret.append(addr)
                    log_wrapping("cp2112", message, True)
                elif status[2]==0x01:
                    message = f"[{addr:#04x}] status_0={status[1]}, address nacked"
            elif status[1]==0x02 or status[1]==0x03:
                if status[2]==0x0:
                    message = f"[{addr:#04x}] status_0={status[1]}, timeout address nacked"
                elif status[2]==0x1:
                    message = f"[{addr:#04x}] status_0={status[1]}, scl low timeout"
                elif status[2]==0x3:
                    message = f"[{addr:#04x}] status_0={status[1]}, read incomplete"
                elif status[2]==0x4:
                    message = f"[{addr:#04x}] status_0={status[1]}, write incomplete"
                elif status[2]==0x5:
                    message = f"[{addr:#04x}] status_0={status[1]}, succeeded after {self.retry} retry"
                    ret.append(addr)
                    log_wrapping("cp2112", message, self.logging)
        
        return ret


    def i2c_status(self, offset=7, logging=True):
        
        # report ID : 0x15 (transfer status request)
        # offset_1 : should be 0x01, other than 1 command will be ignored
        self.hid_write([0x15, 0x01])
        
        # report ID : 0x16 (22d, transfer status response)
        # offset : total 6bytes
        # offset_1 : status_0 (0=idle, 1=busy, 2&3=done->cleared to 0 after read)
        # offset_2 : status_1
        # offset_3~4 : status_2 (number of retries before competing)
        # offset_5~6 : status_3 (number of received bytes)

        status = self.hid_read(offset)

        sts_0 = status[1]
        sts_1 = status[2]

        n_retries = (status[3]<<8) + status[4]
        sts_table = {
            0 : "idle, other values are invalid",
            1 : {
                0 : "address acked",
                1 : "address nacked",
                2 : "data read in progress",
                3 : "data write in progress"
            },
            2 : {
                0 : "timeout address nacked",
                1 : "scl low timeout",
                2 : "arbitration lost",
                3 : "read incomplete",
                4 : "write incomplete",
                5 : "succeeded after retry"
            },
            3 : {
                0 : f"(retry {n_retries}) timeout address nacked",
                1 : f"(retry {n_retries}) scl low timeout",
                2 : f"(retry {n_retries}) arbitration lost",
                3 : f"(retry {n_retries}) read incomplete",
                4 : f"(retry {n_retries}) write incomplete",
                5 : f"(retry {n_retries}) succeeded after retry"
            }
        }

        if sts_0 == 0:
            message = f"status_0={sts_0}, {sts_table[sts_0]}"
        else:
            message = f"status_0={sts_0}, {sts_table[sts_0][sts_1]}"
        log_wrapping("cp2112", message, logging)

        return status


    def i2c_write_multiple_byte(self, addr, data):
        
        # data should be list type and matched with the length
        # report ID : 0x14 (data write)
        # offset_1 : slave address in 8 bit format, lsb is read/write bit, but must be zero
        # offset_2 : number of valid data bytes
        # offset_3~63 : number of bytes (1~512) to be returned from slave device
        # e.g., cp.i2c_write_byte(0x0c, [0xf, 0xa, 0x1])

        length = len(data)
        packet = [0x14, addr<<1, length] + data
        self.hid_write(packet)


    def i2c_write_byte(self, addr, data):
        
        # function to write 1 byte
        # data should be list type and matched with the length
        # report ID : 0x14 (data write)
        # offset_1 : slave address in 8 bit format, lsb is read/write bit, but must be zero
        # offset_2 : this will be fixed to 1
        # offset_3~63 : this will be fixed to 1
        # e.g., cp.i2c_write_byte(0x0c, 0xf)

        length = 1
        packet = [0x14, addr<<1, length] + [data]
        self.hid_write(packet)
    

    def i2c_write_word(self, addr, data):
        
        # e.g., cp.i2c_write_byte(0x0c, 0xab23)
        length = 3
        packet = [0x14, addr<<1, length] + [data>>8, (data&0xff)]
        self.hid_write(packet)


    def i2c_read_byte(self, addr):

        # report ID : 0x10 (data read request)
        # offset : total 3bytes
        # offset_1 : slave address in 8 bit format, lsb is read/write bit, but must be zero
        # offset_2~3 : number of read back, 1~512 bytes --> this will be fixed to 1
        # e.g., cp.i2c_read_byte(0x0c)
        # the function will sequentially returns the value from register 0x00

        '''
        if length > 512:
            log.forcedLog(f"exceed the maximum (512) number of bytes to read back")
        else:
            index_2 = (length>>8) & 0xff
            index_3 = length & 0xff
            packet = [0x10, addr<<1, index_2, index_3]
            self.hid_write(packet)
        '''

        self.hid_write([0x10, addr<<1, 0, 1])

        # polling loop for data read
        for _ in range(10):
            status = self.i2c_status(logging=False)
            if (status[0]==0x16) and (status[2]==5): # succeeded the data transfer
                self.hid_write([0x12, 0, 1])
                res = self.hid_read(4)
                log_wrapping("cp2112", f"report ID[{res[0]:#x}] : offset data {res[1:]}", False)
                return res[3]
            
        log_wrapping("cp2112", "byte read error", True)
    

    def i2c_read_word(self, addr, reg):

        # report ID : 0x11 (data write read request)
        # offset : total 20bytes
        # offset_1 : slave address in 8 bit format, lsb is read/write bit, but must be zero
        # offset_2~3 : number of read back, 1~512 bytes --> this will be fixed to 2
        # offset_4 : number of bytes in target address
        # offset_5 : target address
        # e.g., cp.i2c_read_byte(0x0c, 0x02)
        # the function will sequentially return 2bytes from target register

        # report ID : 0x12 (data read force)
        # offset_1~2 : number of valid data bytes

        # polling loop for data read
        # report ID : 0x13 (data read response)
        # offset_1 : status (0=idle, 1=busy, 2=complete & revert to 0, 3=complete after retry & revert to 0)
        # offset_2 : number of valid data bytes
        # offset_3~63 : returned data

        self.hid_write([0x11, addr<<1, 0x0, 0x02, 0x01, reg])
        self.hid_write([0x12, 0x00, 0x02])

        for _ in range(10):
            status = self.hid_read(10)
            log_wrapping("cp2112", f"report ID[{status[0]:#x}] : offset data {status[1:]}", False)
            if (status[0]==0x13) and (status[2]==2): # succeeded the data transfer
                return (status[4]<<8) + status[3]
            self.hid_write([0x11, addr<<1, 0x0, 0x02, 0x01, reg])
            self.hid_write([0x12, 0x00, 0x02])
        log_wrapping("cp2112", "word read error", True)
    

    def i2c_write(self, addr, reg, data):

        # report ID : 0x14 (data write)
        # offset_1 : slave address in 8 bit format, lsb is read/write bit, but must be zero
        # offset_2 : number of valid data bytes --> this will be fixed to 2
        # offset_3~63 : number of bytes (1~512) to be returned from slave device
        # e.g., cp.i2c_write_byte(0x0c, 0x03, 0xaf)

        self.hid_write([0x14, addr<<1, 0x02, reg, data])
        status = self.i2c_status(logging=False)
        if status[2] != 5:
            log_wrapping("cp2112", f"i2c write error", self.logging)
    

    def i2c_read(self, addr, reg):

        # report ID : 0x11 (data write read request)
        # offset : total 20bytes
        # offset_1 : slave address in 8 bit format, lsb is read/write bit, but must be zero
        # offset_2~3 : number of read back, 1~512 bytes --> this will be fixed to 1
        # offset_4 : number of bytes in target address --> this will be fixed to 1
        # offset_5 : target address
        # e.g., cp.i2c_read_byte(0x0c, 0x03)
        # the function will just return 1bytes from target register

        # report ID : 0x12 (data read force)
        # offset_1~2 : number of valid data bytes

        self.hid_write([0x11, addr<<1, 0x0, 0x1, 0x1, reg])

        for _ in range(10):

            status = self.i2c_status(offset=7, logging=False)
            log_wrapping("cp2112", f"report ID[{status[0]:#x}] : offset data {status[1:]}", False)

            if (status[0]==0x16) and (status[2]==5): # succeeded the data transfer
                
                self.hid_write([0x12, 0x00, 0x01])
                res = self.hid_read(4)
                log_wrapping("cp2112", f"report ID[{res[0]:#x}] : offset data {res[1:]}", False)
            
                return res[3]
            
        log_wrapping("cp2112", f"i2c read error", self.logging)
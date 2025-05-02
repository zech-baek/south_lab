from interface.cui_logger import logger as log
import hid
import time
import sys


'''
devices = hid.enumerate()
for dev in devices:
    print(dev)
'''


def log_wrapping(header, message, is_logging):
    
    if is_logging:
        log.errorLog(f"[{header} {sys._getframe(2).f_code.co_name}] {message}")


class mcp2221:
    
    # class variable for thread
    # if there're multi device on the i2c bus, they'll share the class variable

    # i2c_lock    = threading.Lock()
    i2c_handler = None

    def __init__(self, logging=False):
        
        self.logging = logging

        self.PACKET_SIZE = 65
        self.DIR_OUTPUT  = 0
        self.DIR_INPUT   = 1
        self.CLKDUTY_0   = 0x00
        self.CLKDUTY_25  = 0x08
        self.CLKDUTY_50  = 0x10
        self.CLKDUTY_75  = 0x18
        self.CLKDIV_2    = 0x01 # 24MHz
        self.CLKDIV_4    = 0x02 # 12MHz
        self.CLKDIV_8    = 0x03 # 6MHz
        self.CLKDIV_16   = 0x04 # 3MHz
        self.CLKDIV_32   = 0x05 # 1.5MHz
        self.CLKDIV_64   = 0x06 # 750KHz
        self.CLKDIV_128  = 0x07 # 375KHz

        # self.__class__.i2c_handler = hid.device()
        self.mcp2221a = hid.device()
        self.mcp2221a.open_path(hid.enumerate(0x04D8, 0x00DD)[0]["path"])
        log_wrapping(f"mcp", f"activate the mcp2221a", self.logging)


    def close(self) :

        # if ("i2c_handler" in self.__dict__) and (self.__class__.i2c_handler != None):
        #     self.__class__.i2c_handler.close()

        self.mcp2221a.close()


    def compile_packet(self, buf):

        assert len(buf) <= self.PACKET_SIZE
        buf = buf + [0 for i in range(self.PACKET_SIZE - len(buf))]
        return buf

    
    # ----------------------------- wrapping -----------------------------

    def i2c_read(self, i2c_address, reg_addr):
        
        # send to i2c address to write the register address
        # then, read 1 byte from i2c address

        self.i2c_write_nostop(i2c_address, [reg_addr])
        ret = self.i2c_read_repeated(i2c_address, 1)
        log_wrapping(f"mcp", f"i2c {i2c_address:#04x}, read {reg_addr:#04x}, return {ret[0]:#04x}", self.logging)

        return ret[0]
    

    def i2c_write(self, i2c_address, reg_addr, reg_val):

        self.i2c_write_single(i2c_address, [reg_addr, reg_val])
        log_wrapping(f"mcp", f"i2c {i2c_address:#04x}, write {reg_addr:#04x}, value {reg_val:#04x}", self.logging)
    

    def smbus_scan(self):
        
        ret = []
        for i in range(0x70):
            read_single_byte = self.i2c_read_single(i, 1)
            if "None" in read_single_byte:
                pass
            else:
                ret.append(i)
        log_wrapping(f"mcp", f"smbus scan : {ret}", self.logging)
        return ret
    

    def i2c_speed(self, clk=None):
        pass
    

    # ------------------------------ i2c block ------------------------------

    def i2c_init(self, speed=100000):  # speed = 100000

        buf = self.compile_packet([0x00, 0x10])
        buf[2 + 1] = 0x00  # Cancel current I2C/SMBus transfer (sub-command)
        buf[3 + 1] = 0x20  # Set I2C/SMBus communication speed (sub-command)

        # system clock divider that will be used to establish the i2c speed
        buf[4 + 1] = int((12000000 / speed) - 3)

        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(self.PACKET_SIZE)

        if (rbuf[22] == 0):
            log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] scl pin is low status", self.logging)
        if (rbuf[23] == 0):
            log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] sda pin is low status", self.logging)


    def check_i2c_status(self):

        buf = self.compile_packet([0x00, 0x10])
        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(self.PACKET_SIZE)
        return rbuf[8]


    def i2c_cancel(self):

        buf = self.compile_packet([0x00, 0x10])
        buf[2+1] = 0x10
        self.mcp2221a.write(buf)
        self.mcp2221a.read(self.PACKET_SIZE)


    def i2c_write_single(self, addrs, data):

        # write the data with start and stop condition
        # param int addrs : 7-bit
        # param list data : list of int
        # Datasheet (Rev.B 2017), section 3.1.5
        
        buf = self.compile_packet([0x00, 0x90])
        self._i2c_write(addrs, data, buf)


    def i2c_write_repeated(self, addrs, data):

        # writes the data with repeated start and stop
        # param int addrs : 7-bit
        # param list data : list of int
        # Datasheet (Rev.B 2017), section 3.1.6

        buf = self.compile_packet([0x00, 0x92])
        self._i2c_write(addrs, data, buf)


    def i2c_write_nostop(self, addrs, data):

        # writes the data with start condition
        # param int addrs : 7-bit
        # param list data : list of int
        # Datasheet(Rev.B 2017), section 3.1.7

        buf = self.compile_packet([0x00, 0x94])
        self._i2c_write(addrs, data, buf)


    def _i2c_write(self, addrs, data, buf):

        buf[1 + 1] = (len(data) & 0x00FF)  # Cancel current I2C/SMBus transfer (sub-command)
        buf[2 + 1] = (len(data) & 0xFF00) >> 8  # Set I2C/SMBus communication speed (sub-command)
        buf[3 + 1] = 0xFF & (addrs << 1)

        for i in range(len(data)):
            buf[4 + 1 + i] = data[i]

        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(self.PACKET_SIZE)
        time.sleep(0.01)


    def i2c_read_single(self, addrs, size):

        # readthe data with start and stop
        # param int addrs : 7-bit
        # param int size : size of read out in bytes
        # Datasheet(Rev.B 2017), section 3.1.8

        buf = self.compile_packet([0x00, 0x91])
        return self._i2c_read(addrs, size, buf)


    def i2c_read_repeated(self, addrs, size):

        # reads the data with repeated start and stop
        # param int addrs : 7-bit
        # param int size : size of read out in bytes
        # Datasheet(Rev.B 2017), section 3.1.9

        buf = self.compile_packet([0x00, 0x93])
        ret = self._i2c_read(addrs, size, buf)

        return ret


    def _i2c_read(self, addrs, size, buf):
        
        buf[1 + 1] = (size & 0x00FF)  # Read LEN
        buf[2 + 1] = (size & 0xFF00) >> 8  # Read LEN
        buf[3 + 1] = 0xFF & (addrs << 1)  # addrs

        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(self.PACKET_SIZE)

        if (rbuf[1] != 0x00):
            self.i2c_cancel()
            self.i2c_init()
            log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] fail to read i2c", self.logging)

        buf = self.compile_packet([0x00, 0x40])
        buf[1 + 1] = 0x00
        buf[2 + 1] = 0x00
        buf[3 + 1] = 0x00
        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(self.PACKET_SIZE)

        if (rbuf[1] != 0x00):
            self.i2c_cancel()
            self.i2c_init()
            log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] fail to get a data from i2c (code {rbuf[1]})", self.logging)
            return "None"
        if (rbuf[2] == 0x00 and rbuf[3] == 0x00):
            self.i2c_cancel()
            self.i2c_init()
            return rbuf[4]
        if (rbuf[2] == 0x55 and rbuf[3] == size):
            rdata = [0] * size
            for i in range(size):
                rdata[i] = rbuf[4 + i]
            return rdata

    def reset_mcp2221a(self):

        buf = self.compile_packet([0x00, 0x70, 0xAB, 0xCD, 0xEF])
        self.mcp2221a.write(buf)
        time.sleep(1)

        log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] reset the module", self.logging)


    def mcp_device_info(self):

        # HID DeviceDriver Info
        log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] manufacturer{self.mcp2221a.get_manufacturer_string()}", self.logging)
        log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] product: {self.mcp2221a.get_product_string()}", self.logging)
        log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] serial number {self.mcp2221a.get_serial_number_string()}", self.logging)

    
    def command_struct(self, I2C_Cancel_Bit=0, I2C_Speed_SetUp_Bit=0, I2C_Speed_SetVal_Byte=0):
        
        # Command Structure
        buf = self.compile_packet([0x00, 0x10, 0x00, I2C_Cancel_Bit << 4, I2C_Speed_SetUp_Bit << 5, I2C_Speed_SetVal_Byte])
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(self.PACKET_SIZE)

        # log_wrapping(f"mcp", chr(buf[46]))
        # log_wrapping(f"mcp", chr(buf[47]))
        # log_wrapping(f"mcp", chr(buf[48]))
        # log_wrapping(f"mcp", chr(buf[49]))


    # ------------------------------ gpio block ------------------------------
        
    def gpio_init(self):

        # GPIO Init
        buf = self.compile_packet([0x00, 0x61])
        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(self.PACKET_SIZE)

        buf = self.compile_packet([0x00, 0x60])
        buf[2 + 1] = rbuf[5]  # Clock Output Divider value
        buf[3 + 1] = rbuf[6]  # DAC Voltage Reference
        buf[4 + 1] = 0x00  # Set DAC output value
        buf[5 + 1] = 0x00  # ADC Voltage Reference
        # buf[6+1] = 0x00     #   Setup the interrupt detection mechanism and clear the detection flag
        buf[7 + 1] = 0x80  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80

        self.GPIO_0_BIT = (rbuf[22 + 1] >> 4) & 0x01  # 1:Hi 0:LOW
        self.GPIO_0_DIR = (rbuf[22 + 1] >> 3) & 0x01  # 0:OutPut 1:Input
        self.GPIO_0_MODE = rbuf[22 + 1] & 0x07  # GPIO MODE = 0x00
        self.GPIO_1_BIT = (rbuf[23 + 1] >> 4) & 0x01  # 1:Hi 0:LOW
        self.GPIO_1_DIR = (rbuf[23 + 1] >> 3) & 0x01  # 0:OutPut 1:Input
        self.GPIO_1_MODE = rbuf[23 + 1] & 0x07  # GPIO MODE = 0x00
        self.GPIO_2_BIT = (rbuf[24 + 1] >> 4) & 0x01  # 1:Hi 0:LOW
        self.GPIO_2_DIR = (rbuf[24 + 1] >> 3) & 0x01  # 0:OutPut 1:Input
        self.GPIO_2_MODE = rbuf[24 + 1] & 0x07  # GPIO MODE = 0x00
        self.GPIO_3_BIT = (rbuf[25 + 1] >> 4) & 0x01  # 1:Hi 0:LOW
        self.GPIO_3_DIR = (rbuf[25 + 1] >> 3) & 0x01  # 0:OutPut 1:Input
        self.GPIO_3_MODE = rbuf[25 + 1] & 0x07  # GPIO MODE = 0x00

        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(self.PACKET_SIZE)


    def set_gpio_direction(self, pin, direction):

        # GPIO Set Direction and Set Value commands

        buf = self.compile_packet([0x00, 0x50])
        offset = (pin + 1) * 4
        buf[offset + 1] = 0x01  # set pin direction
        buf[offset + 1 + 1] = direction  # to this

        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(self.PACKET_SIZE)

        if rbuf[1] != 0x00:
            log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] fail to set the gpio direction", self.logging)


    def set_gpio_value(self, pin, value):

        buf = self.compile_packet([0x00, 0x50])
        offset = ((pin + 1) * 4) - 1
        buf[offset - 1 + 1] = 0x01  # set pin value
        buf[offset + 1] = value  # to this
        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(self.PACKET_SIZE)

        if rbuf[1] != 0x00:
            log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] fail to set the gpio value", self.logging)


    def read_gpio(self, pin):

        # Read GPIO Data command

        buf = self.compile_packet([0x00, 0x51])
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(self.PACKET_SIZE)

        self.GPIO_0_INPUT = buf[2]
        self.GPIO_0_DIR = buf[3]
        self.GPIO_1_INPUT = buf[4]
        self.GPIO_1_DIR = buf[5]
        self.GPIO_2_INPUT = buf[6]
        self.GPIO_2_DIR = buf[7]
        self.GPIO_3_INPUT = buf[8]
        self.GPIO_3_DIR = buf[9]

        # buf is tuple, rbuf is integer
        rbuf = buf
        offset = (pin + 1) * 2

        if rbuf[offset] == 0xEE:
            log_wrapping(f"mcp", f"[mcp2221a {sys._getframe(2).f_code.co_name}] receiving fail", self.logging)

        return buf, rbuf[offset]


    # GPIO Outpu/Input Data
    
    def gpio_ch0_out(self, bit):
        self.GPIO_0_BIT = bit  # 1:Hi 0:LOW
        self.set_gpio_ch0_output_mode()
        self.set_gpio_value(pin=0, value=self.GPIO_0_BIT)

    def set_gpio_ch0_input_mode(self):
        self.GPIO_0_DIR = self.DIR_INPUT  # 0:OutPut 1:Input
        self.set_gpio_direction(pin=0, direction=self.GPIO_0_DIR)

    def set_gpio_ch0_output_mode(self):
        self.GPIO_0_DIR = self.DIR_OUTPUT  # 0:OutPut 1:Input
        self.set_gpio_direction(pin=0, direction=self.GPIO_0_DIR)

    def gpio_ch0_in(self):
        self.read_gpio()
        return self.GPIO_0_INPUT, self.GPIO_0_DIR

    def gpio_ch1_out(self, bit):
        self.GPIO_1_BIT = bit  # 1:Hi 0:LOW
        self.set_gpio_1_output_mode()
        self.set_gpio_value(pin=1, value=self.GPIO_1_BIT)

    def set_gpio_ch1_input_mode(self):
        self.GPIO_1_DIR = self.DIR_INPUT  # 0:OutPut 1:Input
        self.set_gpio_direction(pin=1, direction=self.GPIO_1_DIR)

    def set_gpio_1_output_mode(self):
        self.GPIO_1_DIR = self.DIR_OUTPUT  # 0:OutPut 1:Input
        self.set_gpio_direction(pin=1, direction=self.GPIO_1_DIR)

    def gpio_ch1_in(self):
        self.read_gpio()
        return self.GPIO_1_INPUT, self.GPIO_1_DIR

    def gpio_ch2_out(self, bit):
        self.GPIO_2_BIT = bit  # 1:Hi 0:LOW
        self.set_gpio_2_output_mode()
        self.set_gpio_value(pin=2, value=self.GPIO_2_BIT)

    def set_gpio_ch2_input_mode(self):
        self.GPIO_2_DIR = self.DIR_INPUT  # 0:OutPut 1:Input
        self.set_gpio_direction(pin=2, direction=self.GPIO_2_DIR)

    def set_gpio_2_output_mode(self):
        self.GPIO_2_DIR = self.DIR_OUTPUT  # 0:OutPut 1:Input
        self.set_gpio_direction(pin=2, direction=self.GPIO_2_DIR)

    def gpio_ch2_in(self):
        self.read_gpio()
        return self.GPIO_2_INPUT, self.GPIO_2_DIR

    def gpio_ch2_out(self, bit):
        self.GPIO_3_BIT = bit  # 1:Hi 0:LOW
        self.set_gpio_3_output_mode()
        self.set_gpio_value(pin=3, value=self.GPIO_3_BIT)

    def set_gpio_ch3_input_mode(self):
        self.GPIO_3_DIR = self.DIR_INPUT  # 0:OutPut 1:Input
        self.set_gpio_direction(pin=3, direction=self.GPIO_3_DIR)

    def set_gpio_3_output_mode(self):
        self.GPIO_3_DIR = self.DIR_OUTPUT  # 0:OutPut 1:Input
        self.set_gpio_direction(pin=3, direction=self.GPIO_3_DIR)

    def gpio_ch3_in(self):
        self.read_gpio()
        return self.GPIO_3_INPUT, self.GPIO_3_DIR
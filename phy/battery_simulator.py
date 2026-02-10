# ! /usr/bin/env python
# coding=utf-8

import os, sys,pathlib

try:
    # try to use __file__
    phy_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        phy_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        phy_dir = os.getcwd()

root_dir = pathlib.Path(phy_dir).parent
equipment_dir = pathlib.Path(phy_dir).parent/"equipment"
log_dir = pathlib.Path(phy_dir).parent/"log"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)


from interface.cui_logger import logger as log
from interface.cui_colors import color
from tabulate import tabulate as tb
from time import sleep as delay
import crcmod, serial



def log_wrapping(header, message, is_logging=True):
    
    msg = f"[{header} {sys._getframe(2).f_code.co_name}] {message}"
    log.forcedLog(msg) if is_logging else log.debugLog(msg)



class asd_906b(serial.Serial):

    def __init__(self, port, logging=False):
        
        self.logging = logging
        self._enable_flag = False
        self._voltage = 0.1
        
        self.packet_port  = f"{port:02}"
        self.packet_read  = f"{0x11:02x}"
        self.packet_write = f"{0x10:02x}"
        self.local_addr = "01"
        
        try:
            serial.Serial.__init__(
                self,
                port=f"COM{port}",
                baudrate=115200,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=3
                )
            
            log.forcedLog(f"initialized the asd-906b connection to COM{port}")
        except:
            log.errorLog(f"{color.bgred}failed to initialize asd-906b{color.end}")


    def crc_generate(self, value):
        
        # CRC-16 (Modbus) generator

        crc16 = crcmod.mkCrcFun(
            0x18005,
            rev=True,
            initCrc=0xFFFF,
            xorOut=0x0000
            )
        
        byte_array = bytes.fromhex(value)
        checksum   = crc16(byte_array)

        second_crc = str(f"{checksum:04X}")[0:2]
        first_crc = str(f"{checksum:04X}")[2:4]
        
        log_wrapping(
            self.__class__.__name__,
            f"crc={crc16}, byte array={byte_array}, crc checksum={checksum}, 2nd crc={second_crc}, first crc={first_crc}",
            self.logging
        )
        
        return [first_crc, second_crc]


    def send_packet(self, packet):

        ret_crc16 = self.crc_generate(" ".join(packet))
        packet.extend(ret_crc16)
        
        for byte16 in packet:

            self.write(bytes.fromhex(byte16))
            log_wrapping(
            self.__class__.__name__,
                f"send packet={bytes.fromhex(byte16)}",
                self.logging
            )
        
        delay(0.5)

    def conv_voltage(self, voltage):

        conv_voltage = f"{int(voltage*1000):#06x}"
        msb = f"{conv_voltage[2:4]:02}"
        lsb = f"{conv_voltage[4:6]:02}"

        return msb, lsb
    

    @property
    def enable(self):

        if self._enable_flag:
            pass
        else:
            self._enable_flag = True
            msb, lsb = self.conv_voltage(self._voltage)

            ps_state = "01" # unchanged
            curr_state = "00" # unchanged

            module_info = [self.local_addr, "11", "10", "08", ps_state, msb, lsb, curr_state, "00", "00", "00", "00"]
            
            ret_crc = self.crc_generate(" ".join(module_info))
            module_info.extend(ret_crc)

            self.send_packet(module_info)
    

    @property
    def disable(self):

        self._enable_flag = False
        # msb, lsb = self.conv_voltage(self._voltage)
        msb, lsb = self.conv_voltage(0.1)

        ps_state = "02" # unchanged
        curr_state = "00" # unchanged

        module_info = [self.local_addr, "11", "10", "08", ps_state, msb, lsb, curr_state, "00", "00", "00", "00"]
        
        ret_crc = self.crc_generate(" ".join(module_info))
        module_info.extend(ret_crc)

        self.send_packet(module_info)


    @property
    def vset(self):
        pass


    @vset.setter
    def vset(self, voltage):

        self._voltage = voltage
        msb, lsb = self.conv_voltage(voltage)

        ps_state = "00" # unchanged
        curr_state = "00" # unchanged

        module_info = [self.local_addr, "11", "10", "08", ps_state, msb, lsb, curr_state, "00", "00", "00", "00"]
        
        ret_crc = self.crc_generate(" ".join(module_info))
        module_info.extend(ret_crc)

        self.send_packet(module_info)
    

    @property
    def power_recycle(self):

        self.disable
        delay(1)
        self.enable
        delay(1)
from interface.cui_logger import logger as log
from tabulate import tabulate as tb
from time import sleep as delay
import crcmod, serial, sys, os


'''
[Packet structure]
1. run (address=0x002e, data size=1byte)
    com_port 06 00 2e 00 01 1st_crc 2nd_crc
2. stop (address=0x002e, data size=2byte)
    com_port 06 00 2e 00 02 1st_crc 2nd_crc
3. temperature write (address=0x0014, data size=2byte)
    com_port 06 00 14 temp[1:0] temp[3:2] 1st_crc 2nd_crc
4. temperature read (address=0x0015, data size=1byte)
    com_port 04 00 15 00 01 1st_crc 2nd_crc
    --> read data from rs-232

[crc type]
- crc-16 (modbus)
- python package : crcmod <--- pip/conda install crcmod
'''


def log_wrapping(header, message, is_logging=True):
    
    msg = f"[{header} {sys._getframe(2).f_code.co_name}] {message}"
    log.forcedLog(msg) if is_logging else log.debugLog(msg)



class chamber(serial.Serial):
    
    def __init__(self, port) -> None:
        
        self.logging = True
        
        self.com_port     = f"COM{port}"
        self.packet_port  = f"{port:02x}"
        self.packet_read  = f"{4:02x}"
        self.packet_write = f"{6:02x}"
        
        self.temp_reading = None
        self.temp_setting = None
        self.baud = 9600
        
        serial.Serial.__init__(
            self,
            port=self.com_port,
            baudrate=self.baud,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1
            )
        
        log_wrapping(
            self.__class__.__name__,
            f"connected to {self.com_port}, baud {self.baud}",
            self.logging
            )
    
    
    def crc_generate(self, value):
        
        # value format (string) : e.g. "08 04 00 15 00 01"
        # create a CRC-16 (Modbus) function : reversed value
        
        crc16 = crcmod.mkCrcFun(
            0x18005,
            rev=True,
            initCrc=0xFFFF,
            xorOut=0x0000
            )
        byte_array   = bytes.fromhex(value)
        crc_checksum = crc16(byte_array)

        second_crc = str(f"{crc_checksum:04X}")[0:2]
        first_crc = str(f"{crc_checksum:04X}")[2:4]
        
        log_wrapping(
            self.__class__.__name__,
            f"crc={crc16}, byte array={byte_array}, crc checksum={crc_checksum}, 2nd crc={second_crc}, first crc={first_crc}",
            self.logging
        )
        
        return [first_crc, second_crc]
    
    
    @property
    def status(self):
        
        # if (self.temp_reading==None) or (self.temp_setting==None):
        self.get_temperature
        
        header  = ["read temp.", "configured temp."]
        tb_list = [f"{self.temp_reading/100:.02f}", f"{self.temp_setting/100:.01f}"]
        print(tb([header, tb_list], headers="firstrow"))
    
    
    @property
    def uart_read(self):
        
        delay(0.5)
        ret = self.readline()
        hex_list = [f'{byte:#04x}' for byte in ret]
        
        log_wrapping(
            self.__class__.__name__,
            f"read packet={hex_list}",
            self.logging
        )
        
        return hex_list
    
    
    def parsing_hex(self, value):
        
        if isinstance(value, int):
            first_byte  = f"{value:04x}"[0:2]
            second_byte = f"{value:04x}"[2:4]
            
        elif isinstance(value, str):
            first_byte  = value[0:2]
            second_byte = value[2:4]
        
        log_wrapping(
            self.__class__.__name__,
            f"parsing_1st={first_byte}, parsing_2nd={second_byte}",
            self.logging
        )
        
        return [first_byte, second_byte]
    
    
    def update_temp(self, value):
        
        index_1, index_2 = (4, 5) if len(value)>9 else (3, 4)
        read_value = ((int(value[index_1], 16)<<8) + int(value[index_2], 16))
        
        binary_representation = bin(read_value)[2:].zfill(16)
        
        if binary_representation[0] == '1':
            inverted_binary = ''.join('1' if b == '0' else '0' for b in binary_representation)
            inverted_value  = int(inverted_binary, 2) + 1
            signed_value    = -inverted_value
        else:
            signed_value = int(binary_representation, 2)
        
        log_wrapping(
            self.__class__.__name__,
            f"value={value}, signed value={signed_value}",
            self.logging
        )
        
        return signed_value
    
    
    def send_packet(self, packet):
        
        for c in packet:
            self.write(bytes.fromhex(c))
            
            log_wrapping(
                self.__class__.__name__,
                f"packet={packet}, send packet={bytes.fromhex(c)}",
                self.logging
            )
        
        delay(0.5)
        ret = self.uart_read
        
        log_wrapping(
            self.__class__.__name__,
            f"uart read={ret}",
            self.logging
        )
        
        return ret
    
    
    @property
    def enable(self):
        
        addr = self.parsing_hex(value=0x002e)
        
        insert_packet = [
            self.packet_port,
            self.packet_write,
            addr[0],
            addr[1],
            "00",
            "01"
            ]
        
        crc = self.crc_generate(" ".join(insert_packet))
        insert_packet.extend(crc)
        
        log_wrapping(
            self.__class__.__name__,
            f"insert packet={insert_packet}, crc={crc}",
            self.logging
        )
        
        self.send_packet(packet=insert_packet)
    
    
    @property
    def disable(self):
        
        addr = self.parsing_hex(value=0x002e)
        
        insert_packet = [
            self.packet_port,
            self.packet_write,
            addr[0],
            addr[1],
            "00",
            "02"
            ]
        
        crc = self.crc_generate(" ".join(insert_packet))
        insert_packet.extend(crc)
        
        log_wrapping(
            self.__class__.__name__,
            f"insert packet={insert_packet}, crc={crc}",
            self.logging
        )
        
        self.send_packet(packet=insert_packet)
    
    
    def convert_temp(self, target):
        
        if target >= 0:
            ret = int(target*100)
            
        else:
            if not (-32768 <= target <= 32767):
                raise ValueError("out of range for a 16-bit signed integer")
            else:
                target = (1 << 16) + target*100
                hex_value = hex(target).upper()
                ret = hex_value[2:].zfill(4)
        
        return self.parsing_hex(ret)
    
    
    @property
    def set_temperature(self):
        
        print(f"+-----------------------------------+")
        print(f"  temperature configuration : {self.temp_setting}")
        print(f"+------------------------------------+")
    
    
    @set_temperature.setter
    def set_temperature(self, target):
        
        addr = self.parsing_hex(value=0x0014)
        temp = self.convert_temp(target)
        
        insert_packet = [
            self.packet_port,
            self.packet_write,
            addr[0],
            addr[1],
            temp[0],
            temp[1]
            ]
        
        crc = self.crc_generate(" ".join(insert_packet))
        insert_packet.extend(crc)        
        ret = self.send_packet(packet=insert_packet)
        self.temp_setting = ((int(ret[4], 16)<<8) + int(ret[5], 16))/100
        
        log_wrapping(
            self.__class__.__name__,
            f"insert packet={insert_packet}, crc={crc}, return={ret}",
            self.logging
        )
    
    
    @property
    def get_temperature(self):
        
        addr = self.parsing_hex(value=0x0015)
        preset_packet = [
            self.packet_port,
            self.packet_read,
            addr[0],
            addr[1],
            "00",
            "01"
            ]
        
        crc = self.crc_generate(" ".join(preset_packet))
        preset_packet.extend(crc)
        ret = self.send_packet(packet=preset_packet) # length 7 list data
        self.temp_reading = self.update_temp(value=ret)
        
        addr = self.parsing_hex(value=0x0014)
        insert_packet = [
            self.packet_port,
            self.packet_read,
            addr[0],
            addr[1],
            "00",
            "02"
            ]
        
        crc = self.crc_generate(" ".join(insert_packet))
        insert_packet.extend(crc)
        ret = self.send_packet(packet=insert_packet) # length 9 list data
        self.temp_setting = self.update_temp(value=ret)
        
        log_wrapping(
            self.__class__.__name__,
            f"preset packet={preset_packet}, crc={crc}, ret={ret}, insert packet={insert_packet}, crc={crc}, return={ret}",
            self.logging
        )
        
        self.status
# ! /usr/bin/env python
# coding=utf-8

import os, sys,pathlib
from interface.cui_logger import logger as log
from interface.cui_colors import color
from tabulate import tabulate as tb
from time import sleep as delay
import crcmod, serial

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




def log_wrapping(header, message, is_logging=True):
    
    # msg = f"[{header} {sys._getframe(2).f_code.co_name}] {message}"
    log.forcedLog(message) if is_logging else log.debugLog(message)



class preset:

    info = ["10", "01", "00"]
    enable = ["11", "04", "03", "01", "00", "00"]
    disable = ["11", "04", "03", "00", "00", "00"]
    voltage = ["11", "10", "08", "00", "msb", "lsb", "00", "00", "00", "00", "00"]
    get_vi = ["10", "08", "00"]



class asd_906b(serial.Serial):

    """
    api list
        - get_info : property
        - vset : setter
        - iset : setter, can be set to the first decimal place
        - enable (property)
        - disable (property)
        - voltage (property)
        - current (property)
    trouble shooting
        - if packet error exists in the received data, adjust lower baud rate
    """


    def __init__(self, port:int, local_addr="01", logging=False, ignore=False):
        
        self.logging = logging
        self.packet_port  = f"{port:02}"
        self.packet_read  = f"{0x11:02x}"
        self.packet_write = f"{0x10:02x}"
        self.local_addr = [local_addr]
        self.ignore = ignore
        
        try:
            serial.Serial.__init__(
                self,
                port=f"COM{self.packet_port}",
                baudrate=115200,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=3
                )

            self.flush()
            log.forcedLog(f"initialized the asd-906b connection to COM{port}")

        except:
            log.errorLog(f"{color.bgred}failed to initialize asd-906b{color.end}")
    

    def flush(self):
        
        # while self.in_waiting:
            # print(self.readline().decode().strip())
        self.reset_input_buffer()


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
        
        return [first_crc, second_crc]


    def send_packet(self, packet):

        ret_crc16 = self.crc_generate(" ".join(packet))
        packet.extend(ret_crc16)
        
        for byte16 in packet:
            self.write(bytes.fromhex(byte16))

        if self.logging:
            for i in packet:
                print(f"[send_packet] {bytes.fromhex(i)} ({i})")
        

    def receive_packet(self, expected_length=None):

        try:
            if expected_length is None:
                rx_data = self.read_until()
            else:
                rx_data = self.read(expected_length)

            hex_data = rx_data.hex().upper() # convert bytes to hex strings
            packet = [hex_data[i:i+2] for i in range(0, len(hex_data), 2)] # split the data into a list

            rx_crc = packet[-2:]  # last two bytes = crc
            data_wo_crc = packet[:-2]
            calculated_crc = self.crc_generate(" ".join(data_wo_crc))

            log_message = f"[receive_packet] packet={packet}, rx_crc={rx_crc}, data_crc={calculated_crc}"
            log_wrapping(self.__class__.__name__, log_message, self.logging)
            log.debugLog(log_message)
            
            if rx_crc == calculated_crc: # validate the CRC
                return packet
            else:
                if self.ignore:
                    return packet
                else:
                    log_message = f"[receive_packet] invalid crc, packet discarded"
                    log.debugLog("invalid crc, packet discarded")
                    return None
            
        except serial.SerialException as e:
            print(f"serial error: {e}")

        except Exception as e:
            print(f"error receiving packet: {e}")


    @property
    def get_info(self):

        module = self.local_addr + preset.info
        self.send_packet(module)
        ret = self.receive_packet()

        if self.convert_packet(hex_list=ret[1], ret_int=True) == 0x12 and self.convert_packet(hex_list=ret[2], ret_int=True) == 0x1 and self.convert_packet(hex_list=ret[3], ret_int=True) == 0x1c:

            header = ["Type", "MAC", "Model name", "HW", "SW", "Max Vout", "Max Iout", "Max Vin", "Max Iin"]
            list_info = list()
            list_info.append(header)
            packet_info = list()

            packet_type = self.convert_packet(ret[4], ret_int=True)
            if   packet_type == 1: device_type = "Battery simulator"
            elif packet_type == 2: device_type = "Power supply"
            elif packet_type == 3: device_type = "Loader"
            else: "Misc."

            packet_info.append(packet_type)
            mac_addr = self.convert_packet(ret[5:9], ret_int_list=True)
            packet_info.append(" ".join([f"0x{value:X}" for value in mac_addr]))
            packet_info.append(self.convert_packet(ret[9:11], ret_join=True))
            packet_info.append(self.convert_packet(ret[13:15], ret_int=True))
            packet_info.append(self.convert_packet(ret[15:17], ret_int=True))
            packet_info.append(self.convert_packet(ret[20:22], ret_int=True))
            packet_info.append(self.convert_packet(ret[22:24], ret_int=True))
            packet_info.append(self.convert_packet(ret[26:28], ret_int=True))
            packet_info.append(self.convert_packet(ret[28:30], ret_int=True))

            list_info.append(packet_info)
            print(tb(list_info, headers="firstrow"))

        else:
            log.forcedLog(f"wrong packet header")


    def convert_packet(self, hex_list, ret_int=False, ret_int_list=False, ret_join=False):
    
        # join the list into integer
        hex_string = "".join(hex_list)

        if ret_int:
            return int(hex_string, 16)
        elif ret_int_list:
            return [int(f"0x{value}", 16) for value in hex_list]
        elif ret_join:
            return "".join(hex_list)


    def conv_voltage(self, voltage):

        conv_voltage = f"{int(voltage*1000):#06x}"
        msb = f"{conv_voltage[2:4]:02}"
        lsb = f"{conv_voltage[4:6]:02}"

        log_wrapping(
            self.__class__.__name__,
            f"[conv_voltage] parameter={conv_voltage}, msb={msb}, lsb={lsb}",
            self.logging
        )

        return msb, lsb
    

    @property
    def enable(self):

        module = self.local_addr + preset.enable        
        ret_crc = self.crc_generate(" ".join(module))
        module.extend(ret_crc)
        self.send_packet(module)
    

    @property
    def disable(self):

        module = self.local_addr + preset.disable      
        ret_crc = self.crc_generate(" ".join(module))
        module.extend(ret_crc)
        self.send_packet(module)


    @property
    def vset(self):
        pass


    @vset.setter
    def vset(self, voltage):

        self._voltage = voltage
        msb, lsb = self.conv_voltage(voltage)

        ps_state = "00" # unchanged
        curr_state = "00" # unchanged

        module_info = self.local_addr + ["11", "10", "08", ps_state, msb, lsb, curr_state, "00", "00", "00", "00"]
        
        ret_crc = self.crc_generate(" ".join(module_info))
        module_info.extend(ret_crc)

        self.send_packet(module_info)
    

    @property
    def vset_backup(self):
        pass


    @vset_backup.setter
    def vset_backup(self, voltage):

        msb, lsb = self.conv_voltage(voltage)
        module = self.local_addr + preset.voltage
        module[5] = msb
        module[6] = lsb
        ret_crc = self.crc_generate(" ".join(module))
        module.extend(ret_crc)

        self.send_packet(module)

        log_wrapping(
            self.__class__.__name__,
            f"[vset] module={module}, crc={ret_crc}",
            self.logging
        )
    

    @property
    def iset(self):
        pass

    
    @iset.setter
    def iset(self, current):

        # set the same limit current for input and output
        # can be set to the first decimal place

        measure_range = "04" # auto
        current_limit = int(round(current,1)*1000)
        msb_ilimt = str(f"{current_limit:04X}")[0:2]
        lsb_ilimt = str(f"{current_limit:04X}")[2:4]
        t_prot    = "96" # 150ms
        msb_r_bat = "00"
        lsb_r_bat = "00"

        module = self.local_addr + [
            "11", "03", "0F", measure_range,
            msb_ilimt, lsb_ilimt, "00", "00", t_prot,
            msb_ilimt, lsb_ilimt, "00", "00", t_prot,
            msb_r_bat, lsb_r_bat, "02", "00"]
        
        log_wrapping(
            self.__class__.__name__,
            f"[iset] module={module}",
            self.logging
        )

        self.send_packet(module)
    

    def get_vi(self):

        module = self.local_addr + preset.get_vi
        
        try:
            
            self.send_packet(module)
            ret = self.receive_packet()

            log_wrapping(
                self.__class__.__name__,
                f"[get_vi] module={module}, ret={ret}",
                self.logging
            )

            if ret == None:
                try:
                    self.send_packet(module)
                    ret = self.receive_packet()

                    log_wrapping(
                        self.__class__.__name__,
                        f"[get_vi] retry return={ret}",
                        self.logging
                    )
                except:
                    return [0, 0]
                
            ret_voltage = self.convert_packet(hex_list=ret[4:8], ret_int=True) / 1e+3
            ret_current = self.convert_packet(hex_list=ret[9:13], ret_int=True) / 1e+3
            return [ret_voltage, ret_current]

        except:
            return [0, 0]
    
    
    @property
    def cfg_all(self):
        pass


    @cfg_all.setter
    def cfg_all(self, *args):
        
        len_args = len(args)
        if len_args == 1:
            self.vset = args[0][0]
            self.iset = args[0][1]
        else:
            log.forcedLog(f"configuration error, require voltage and current input (e.g. self.cfg_all = 5, 0.2)")
    

    @property
    def voltage(self):
        return self.get_vi()[0]
    

    @property
    def current(self):
        return self.get_vi()[1]
    

    @property
    def power_recycle(self):

        self.disable
        delay(1)
        self.enable
        delay(1)
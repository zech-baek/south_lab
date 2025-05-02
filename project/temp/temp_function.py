from tabulate import tabulate as tb
from interface.cui_colors import color
from interface.cui_logger import logger as log
import yaml, sys


def print_byte_status(reg, obj):
    
    obj = obj
    sts_reg = reg
    header = ["Addr", "Reg", "Value", "Bit7", "Bit6", "Bit5", "Bit4", "Bit3", "Bit2", "Bit1", "Bit0"]
    
    with open(f"{obj.device_path}/{obj.device}_{obj.revision}_status.yaml") as yaml_device:
        status_map = yaml.safe_load(yaml_device)
    
    sts_map = dict()
    for n in sts_reg:
        sts_map[n] = status_map[n]
    
    ret_map = []
    ret_map.append(header)

    for reg in sts_reg:

        ret = obj.read_byte(reg)
        parsing_list = []

        for shift in range(8):
            parsing_list.append((ret>>shift) & 0x1)

        parsing_list.reverse()
        
        item_list = []
        item_list.append(f"{reg:#04x}")
        item_list.append(f"{sts_map[reg][0]}")
        item_list.append(f"{ret:#04x}")

        for m in range(8):
            if parsing_list[m] == 1:
                item_list.append(f"{color.blue}{color.bold}{sts_map[reg][m+1]}{color.end}")
            else:
                item_list.append(f"{sts_map[reg][m+1]}")
        ret_map.append(item_list)

    print(tb(ret_map, headers="firstrow"))



class function:

    def __init__(self, obj):

        self.obj = obj

    
    @property
    def tm_activate(self):
        
        self.obj.write_byte(0xa0, 0xf9)
        self.obj.write_byte(0xa0, 0x9f)
        print(f"activate test mode : [0xa0]={self.obj.read_byte(0xa0):#04x}")


    @property
    def status(self):
        
        status_register = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]
        print_byte_status(reg=status_register, obj=self.obj)
    
    
    @property
    def status_otp(self):
        
        status_register = [0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA, 0xCB, 0xCC, 0xCD, 0xCE, 0xCF]
        print_byte_status(reg=status_register, obj=self.obj)
    
    
    @property
    def status_tm(self):
        
        status_register = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA9, 0xBA, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF]
        print_byte_status(reg=status_register, obj=self.obj)
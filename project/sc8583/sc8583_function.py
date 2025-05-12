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
        
        status_register = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12]
        print_byte_status(reg=status_register, obj=self.obj)
    
    
    @property
    def status_ctrl(self):
        
        status_register = [0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29]
        print_byte_status(reg=status_register, obj=self.obj)
    

    @property
    def status_adc(self):
        
        # status_register = [0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F]
        # print_byte_status(reg=status_register, obj=self.obj)

        lsb_iin  = 0.001875
        lsb_vin  = 0.00625
        lsb_wpc  = 0.00625
        lsb_vext = 0.00625
        lsb_vout = 0.00125
        lsb_vbat = 0.00125
        lsb_tdie = 0.5
        lsb_c1p  = 0.00625
        lsb_ibat = 0.00375
        lsb_ntc  = 0.01465

        sts_map = dict()
        header = ["ADC", "Hex", "Value"]

        sts_reg = {
            "IIN_ADC"    : 0.001875,
            "VIN_ADC"    : 0.00625,
            "WPC_IN_ADC" : 0.00625,
            "VEXT_ADC"   : 0.00625,
            "VOUT_ADC"   : 0.00125,
            "VBAT_ADC"   : 0.00125,
            "IBAT_ADC"   : 0.00375,
            "C1P_ADC"    : 0.00625,
            "NTC_ADC"    : 0.01465,
            "TDIE_ADC"   : 0.5
        }
    
        ret_map = []
        ret_map.append(header)

        for reg, lsb in sts_reg.items():

            ret = getattr(self.obj, reg)
            
            item_list = []
            item_list.append(f"{reg}")
            item_list.append(f"{ret:#05x}")
            item_list.append(f"{ret*lsb}")
            
            ret_map.append(item_list)

        print(tb(ret_map, headers="firstrow", numalign="right"))
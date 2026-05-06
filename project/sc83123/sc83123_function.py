from tabulate import tabulate as tb
from interface.cui_colors import color
from interface.cui_logger import logger as log
from interface.docs.output_excel import excel_frame
import yaml, sys, os


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
                item_list.append(f"{color.bggrn}{color.bold}{color.black}{sts_map[reg][m+1]}{color.end}")
            else:
                item_list.append(f"{sts_map[reg][m+1]}")
        ret_map.append(item_list)

    print(tb(ret_map, headers="firstrow"))



class function:

    def __init__(self, obj):
        self.obj = obj


    @property
    def status(self):
        
        status_register = [0x01, 0x02, 0x03]
        print_byte_status(reg=status_register, obj=self.obj)


    @property
    def register_byte_dump(self):

        filename = log.time_stamp(display=False, ret=True) + f"_sc83123_dump"
        xl = excel_frame(file=filename)
        xl.worksheet_title = "sc83123"

        start_row = 2
        header = ["register", "value (dec)", "value (hex)"]
        xl.insert_header = start_row, 2, header

        log.output_set_filename(filename)
        log.output_csv(header)
        
        for reg_addr in range(0x0, 0x04):

            readback = self.obj.read_byte(reg_addr)
            start_row += 1
            temp = [f"{reg_addr:#04x}", readback, f"{readback:#04x}"]
            xl.insert_list = start_row, 2, temp
            log.output_csv(temp)
        
        xl.close
    

    def log_analyzer(self, log_value):

        # log_value
        # key : register address
        # value : regiter value
        # e.g. log_value = {0x0d : 0x7f, 0x0e : 0xa2}
    
        header = ["Addr", "Reg", "Value", "Bit7", "Bit6", "Bit5", "Bit4", "Bit3", "Bit2", "Bit1", "Bit0"]
        
        with open(f"{self.obj.device_path}/{self.obj.device}_{self.obj.revision}_status.yaml") as yaml_device:
            status_map = yaml.safe_load(yaml_device)
        
        sts_map = dict()
        for n in log_value.keys():
            sts_map[n] = status_map[n]
        
        ret_map = []
        ret_map.append(header)

        for reg_addr, reg_value in log_value.items():

            parsing_list = []

            for shift in range(8):
                parsing_list.append((reg_value>>shift) & 0x1)

            parsing_list.reverse()
            
            item_list = []
            item_list.append(f"{reg_addr:#04x}")
            item_list.append(f"{sts_map[reg_addr][0]}")
            item_list.append(f"{reg_value:#04x}")

            for m in range(8):
                if parsing_list[m] == 1:
                    item_list.append(f"{color.blue}{color.bold}{sts_map[reg_addr][m+1]}{color.end}")
                else:
                    item_list.append(f"{sts_map[reg_addr][m+1]}")
            ret_map.append(item_list)

        print(tb(ret_map, headers="firstrow"))
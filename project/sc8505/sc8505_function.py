from tabulate import tabulate as tb
from interface.cui_colors import color
from interface.cui_logger import logger as log
from interface.docs.output_excel import excel_frame

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
                item_list.append(f"{color.bggrn}{color.bold}{color.black}{sts_map[reg][m+1]}{color.end}")
            else:
                item_list.append(f"{sts_map[reg][m+1]}")
        ret_map.append(item_list)

    print(tb(ret_map, headers="firstrow"))



class function:

    STATUS_REGISTERS = [  0x06, 0x0A, 0x0F, 0x10, 0x12,
                          0x13, 0x14, 0x16, 0x17,
                          0x18, 0x19, 0x1B,
                          0x1D, 0x1E, 0x20, 0x22,
                          0x40, 0x41, 0x42, 0x43,
                          0x50, 0x51, 0x52, 0x53, 0x54, 0x55]

    def __init__(self, obj):

        self.obj = obj
    

    @property
    def status(self):
        
        print_byte_status(reg=self.STATUS_REGISTERS, obj=self.obj)
    

    def log_analyzer(self, log_value):

        # log_value
        # key : register address
        # value : regiter value

        log_value = log_value

        if 0 in log_value.keys():
            del log_value[0]

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
    

    def log_dump(self, *args):

        len_args = len(args)
        
        # case 1 : autoset the filename
        if len_args == 0:
            filename = log.time_stamp(display=False, ret=True) + f"_sc8505_log_dump"
            xl = excel_frame(file=filename)
            xl.worksheet_title = "sc8505"
            self._log_excel_dump(obj=xl, filename=filename)
        
        # case 2 : setup the filename by manual input
        else:
            filename = args[0]
            xl = excel_frame(file=filename)
            xl.worksheet_add = f"sc8505_log_dump"
            self._log_excel_dump(obj=xl, filename=filename)


    def _log_excel_dump(self, obj, filename):
        
        xl = obj
        header = ["register", "address (dec)", "address (hex)"]
        start_row = 2
        xl.insert_header = start_row, 2, header

        log.output_set_filename(filename)
        log.output_csv(header)

        # reg_page format
        # index 0 : splited number
        # index 1 : register name
        # index 2 : list for address
        # index 3 : list for msb
        # index 4 : list for lsb
        # index 5 : list for highest bit
        # index 6 : list for lowest bit
        # index 7 : permission
        # index 8 : R or RW

        reg_page = self.obj.get_regpage()

        for key in reg_page.keys():
            
            start_row += 1
            readback = getattr(self, key)
            temp = [key, readback, f"{readback:#x}"]
            xl.insert_list = start_row, 2, temp
            log.output_csv(temp)
        
        xl.close

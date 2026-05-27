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

    def __init__(self, obj):

        self.obj = obj

        adc_table = {
            "iin"   : ["IIN_ADC"  , 0.001875],
            "vin"   : ["VIN_ADC"  , 0.005],
            "vext1" : ["VEXT1_ADC", 0.005],
            "vext2" : ["VEXT2_ADC", 0.005],
            "vout"  : ["VOUT_ADC" , 0.00125],
            "vbat"  : ["VBAT_ADC" , 0.00125],
            "ibat"  : ["IBAT_ADC" , 0.003125],
            "c1p"   : ["C1P_ADC"  , 0.005],
            "ntc"   : ["NTC_ADC"  , 0.01465],
            "tdie"  : ["TDIE_ADC" , 0.5]
        }

        self.create_property("adc", adc_table)
    

    def create_property(self, suffix, config_list):

        for prefix, cfg in config_list.items():
            setattr(self.__class__, f"{prefix}_{suffix}", property(lambda self, cfg=cfg: getattr(self, suffix)(cfg)))
    

    def adc(self, cfg):

        reg = cfg[0]
        lsb = cfg[1]

        raw = getattr(self.obj, reg)
        return raw * lsb
    

    @property
    def status(self):
        
        status_register = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12]
        print_byte_status(reg=status_register, obj=self.obj)
    
    
    @property
    def status_ctrl(self):
        
        status_register = [0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A]
        print_byte_status(reg=status_register, obj=self.obj)
    

    @property
    def status_adc(self):

        initial_set = self.obj.ADC_EN
        self.obj.ADC_EN = 1
        
        # status_register = [0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F]
        # print_byte_status(reg=status_register, obj=self.obj)

        lsb_iin   = 0.001875
        lsb_vin   = 0.005
        lsb_vext1 = 0.005
        lsb_vext2 = 0.005
        lsb_vout  = 0.00125
        lsb_vbat  = 0.00125
        lsb_tdie  = 0.5
        lsb_c1p   = 0.005
        lsb_ibat  = 0.003125
        lsb_ntc   = 0.01465

        sts_map = dict()
        header = ["ADC", "Hex", "Value"]

        sts_reg = {
            "IIN_ADC"    : 0.001875,
            "VIN_ADC"    : 0.005,
            "VEXT1_ADC"   : 0.005,
            "VEXT2_ADC"   : 0.005,
            "VOUT_ADC"   : 0.00125,
            "VBAT_ADC"   : 0.00125,
            "IBAT_ADC"   : 0.003125,
            "C1P_ADC"    : 0.005,
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
        
        self.obj.ADC_EN = initial_set
    

    @property
    def enable_charging(self):

        self.obj.write_byte(0x13, 0xd0)
        print(f"CP_EN = {self.obj.CP_EN}")
        print(f"QB_EN = {self.obj.QB_EN}")
    

    @property
    def preparing_charging(self):

        self.obj.IIN_REG_DIS = 1
        self.obj.IBAT_REG_DIS = 1
        self.obj.VBAT_REG_DIS = 1
        self.obj.IBAT_OCP_DIS = 1
        self.obj.IIN_UCP_DIS = 1
        self.obj.NTC_FLT_DIS = 1
        self.obj.VBAT_OVP_DIS = 1
        self.obj.STANDBY_MODE_SET = 1
        self.obj.VEXT_SHUT_DOWN_SET = 0
        self.obj.SS_TIMEOUT = 0

        print(f"IIN_REG_DIS = {self.obj.IIN_REG_DIS}")
        print(f"IBAT_REG_DIS = {self.obj.IBAT_REG_DIS}")
        print(f"VBAT_REG_DIS = {self.obj.VBAT_REG_DIS}")
        print(f"IBAT_OCP_DIS = {self.obj.IBAT_OCP_DIS}")
        print(f"IIN_UCP_DIS = {self.obj.IIN_UCP_DIS}")
        print(f"NTC_FLT_DIS = {self.obj.NTC_FLT_DIS}")
        print(f"VBAT_OVP_DIS = {self.obj.VBAT_OVP_DIS}")
        print(f"STANDBY_MODE_SET = {self.obj.STANDBY_MODE_SET}")
        print(f"VEXT_SHUT_DOWN_SET = {self.obj.VEXT_SHUT_DOWN_SET}")
        print(f"SS_TIMEOUT = {self.obj.SS_TIMEOUT}")
    

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
            filename = log.time_stamp(display=False, ret=True) + f"_sc85853_log_dump"
            xl = excel_frame(file=filename)
            xl.worksheet_title = "sc85853"
            self._log_excel_dump(obj=xl, filename=filename)
        
        # case 2 : setup the filename by manual input
        else:
            filename = args[0]
            xl = excel_frame(file=filename)
            xl.worksheet_add = f"sc85853_log_dump"
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
    

    @property
    def status_reg(self):
        
        control_reg = [
            "MODE", "SS_TIMEOUT", "FREQ_SHIFT", "FSW_SET", "SYNC_EN", "SET_IBAT_SNS_HS", "SET_IBAT_SNS_RES", 
            "VEXT_SHUT_DOWN_SET", "STANDBY_MODE_SET", "WD_VEXT_SHUTDOWN_EN", "WD_STANDBY_EN", "WD_TIMEOUT", 
            "WD_TIMEOUT_DIS", "EXT1_OVP", "EXT1_SW_CTRL1", "EXT1_SW_CTRL2", "EXT2_SW_CTRL1", "EXT2_SW_CTRL2", 
            "EXT2_GATE_CTRL", "EXT2_OVP", "IIN_REG", "VBAT_REG", "VBAT_OVP", "IBAT_REG", "VIN_OVP", "VOUT_OVP", 
            "IIN_OCP", "C1P2OUT_OVP", "C1P2OUT_UVP", "NTC_FLT_DIS", "VBAT_REG_DIS", "IIN_REG_DIS", "IIN_UCP_DIS", 
            "TDIE_REG_DIS", "TDIE_REG", "VBAT_OVP_DIS", "IIN_UCP_DIS", "IIN_OCP_DG_SET", "VBAT_OVP_DG_SET", 
            "VIN_OVP_DG_SET", "VOUT_OVP_DG_SET", "VEXT1_OVP_DG_SET", "VEXT2_OVP_DG_SET", "IIN_UCP_FALL_DG_SET"
            ]
        
        for reg in control_reg:
            
            ret = getattr(self.obj, reg)
            print(f"{reg} = {ret:#x} ({ret})")     


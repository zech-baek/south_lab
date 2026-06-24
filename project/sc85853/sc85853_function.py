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

    ADC_TABLE = {
        "iin"   : ["IIN_ADC"   , 0.001875, "A"],
        "vin"   : ["VIN_ADC"   , 0.00625 , "V"],
        "vb_out": ["VB_OUT_ADC", 0.00625 , "V"],
        "vusb"  : ["VUSB_ADC"  , 0.00625 , "V"],
        "vext"  : ["VEXT_ADC"  , 0.00625 , "V"],
        "vout"  : ["VOUT_ADC"  , 0.00125 , "V"],
        "vbat"  : ["VBAT_ADC"  , 0.00125 , "V"],
        "c1p"   : ["C1P_ADC"   , 0.00625 , "V"],
        "ntc"   : ["NTC_ADC"   , 0.01465 , "%"],
        "tdie"  : ["TDIE_ADC"  , 0.5     , "C"]
    }

    def __init__(self, obj):

        self.obj = obj

        self.create_property("adc", self.ADC_TABLE)
    

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
        
        status_register = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x14,0x15,0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D]
        print_byte_status(reg=status_register, obj=self.obj)
    
    
    @property
    def status_ctrl(self):
        
        status_register = [0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36]
        print_byte_status(reg=status_register, obj=self.obj)
    

    @property
    def status_adc(self):

        initial_set = self.obj.ADC_EN
        self.obj.ADC_RATE = 0
        self.obj.ADC_EN = 1
        try:
            # status_register = [0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F]
            # print_byte_status(reg=status_register, obj=self.obj)

            header = ["ADC", "Hex", "LSB", "Value"]
        
            ret_map = []
            ret_map.append(header)

            for reg, lsb, unit in self.ADC_TABLE.values():

                ret = getattr(self.obj, reg)
                
                item_list = []
                item_list.append(f"{reg}")
                item_list.append(f"{ret:#05x}")
                item_list.append(f"{lsb:g} {unit}")
                item_list.append(f"{ret*lsb:g} {unit}")
                
                ret_map.append(item_list)

            print(tb(ret_map, headers="firstrow", numalign="right"))
        finally:
            self.obj.ADC_EN = initial_set
    

    @property
    def enable_charging(self):

        self.obj.CP_EN = 1
        print(f"CP_EN = {self.obj.CP_EN}")


    @property
    def qb1_enable_charging(self):
        
        self.obj.VUSB_SW_CTRL1 = 1
        self.obj.STANDBY_MODE_SET = 1
        self.obj.CP_EN = 1

        print(f"STANDBY_MODE_SET = {self.obj.STANDBY_MODE_SET}")
        print(f"QB1_CTRL2 = {self.obj.VUSB_SW_CTRL1}")
        print(f"CP_EN = {self.obj.CP_EN}")


    @property
    def qb2_enable_charging(self):

        self.obj.VEXT_SW_CTRL1 = 1
        self.obj.STANDBY_MODE_SET = 1
        self.obj.CP_EN = 1

        print(f"STANDBY_MODE_SET = {self.obj.STANDBY_MODE_SET}")
        print(f"QB1_CTRL2 = {self.obj.VEXT_SW_CTRL1}")
        print(f"CP_EN = {self.obj.CP_EN}")
    

    @property
    def preparing_charging(self):

        # self.obj.IIN_REG_DIS = 1
        # self.obj.VBAT_REG_DIS = 1
        self.obj.IIN_UCP_DIS = 1
        self.obj.NTC_FLT_DIS = 1
        self.obj.VBAT_OVP_DIS = 1
        self.obj.STANDBY_MODE_SET = 1
        self.obj.VUSB_SHUTDOWN_SET = 0
        self.obj.SS_TIMEOUT = 0

        # print(f"IIN_REG_DIS = {self.obj.IIN_REG_DIS}")
        # print(f"VBAT_REG_DIS = {self.obj.VBAT_REG_DIS}")
        print(f"IIN_UCP_DIS = {self.obj.IIN_UCP_DIS}")
        print(f"NTC_FLT_DIS = {self.obj.NTC_FLT_DIS}")
        print(f"VBAT_OVP_DIS = {self.obj.VBAT_OVP_DIS}")
        print(f"STANDBY_MODE_SET = {self.obj.STANDBY_MODE_SET}")
        print(f"VUSB_SHUTDOWN_SET = {self.obj.VUSB_SHUTDOWN_SET}")
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
            "MODE", "CP_EN", "QB1_CTRL2", "QB2_CTRL1", "QB2_CTRL2", "QB2_OTG_MODE",
            "SS_TIMEOUT", "SS_FAIL_DIS", "FREQ_SHIFT", "FSW_SET", "SYNC_EN",
            "STANDBY_MODE_SET", "VUSB_SHUTDOWN_SET", "WD_VUSB_SHUTDOWN_EN",
            "WD_STANDBY_EN", "WD_TIMEOUT", "WD_TIMEOUT_DIS",
            "VUSB_SW_CTRL1", "VUSB_SW_CTRL2", "VUSB_OFF_GATE_CTRL", "VUSB_OVP_SEL",
            "VUSB_OVP", "VUSB_OVP_DIS", "VUSB_DISCHG_CTRL1", "VUSB_DISCHG_CTRL2",
            "VEXT_SW_CTRL1", "VEXT_SW_CTRL2", "VEXT_OFF_GATE_CTRL", "VEXT_OVP_SEL",
            "VEXT_OVP", "VEXT_OVP_DIS", "VEXT_DISCHG_CTRL1", "VEXT_DISCHG_CTRL2",
            "VB_OUT_OVP", "VB_OUT_OVP_DIS", "VB_OUT_PD_EN", "VB_OUT_PRESENT_DIS",
            "VIN_OVP", "VIN_OVP_DIS", "VIN_PRESENT_DIS", "VOUT_OVP", "VOUT_OVP_DIS",
            "VBAT_REG", "VBAT_REG_DIS", "VBAT_OVP", "VBAT_OVP_DIS",
            "IIN_REG", "IIN_REG_DIS", "IIN_OCP", "IIN_OCP_DIS", "IIN_UCP_CFG",
            "IIN_UCP_DIS", "IIN_UCP_EN_METHOD_SEL", "IIN_UCP_FALL_BLANKING_SET",
            "TDIE_REG", "TDIE_REG_DIS", "IIN_TDIE_REG_INTERVAL", "NTC_FLT_DIS",
            "C1P2OUT_OVP", "C1P2OUT_OVP_DIS", "C1P2OUT_UVP", "C1P2OUT_UVP_DIS",
            "ADC_EN", "ADC_RATE", "ADC_FREEZE", "IIN_ADC_DIS", "VIN_ADC_DIS",
            "VB_OUT_ADC_DIS", "VUSB_ADC_DIS", "VEXT_ADC_DIS", "VOUT_ADC_DIS",
            "VBAT_ADC_DIS", "C1P_ADC_DIS", "NTC_ADC_DIS", "TDIE_ADC_DIS",
            "IIN_OCP_DG_SET", "VBAT_OVP_DG_SET", "VIN_OVP_DG_SET",
            "VOUT_OVP_DG_SET", "VEXT_OVP_DG_SET", "VUSB_OVP_DG_SET",
            "VB_OUT_OVP_DG_SET", "IIN_UCP_FALL_DG_SET"
            ]
        
        for reg in control_reg:
            
            ret = getattr(self.obj, reg)
            print(f"{reg} = {ret:#x} ({ret})")     


    @property
    def status_power_path(self):

        status_list = [
            "VIN_PRESENT_STAT", "VB_OUT_PRESENT_STAT", "VOUT_INSERT_STAT",
            "VIN_TH_CHG_EN_STAT", "VB_OUT_TH_CHG_EN_STAT",
            "VOUT_TH_CHG_EN_STAT", "VOUT_TH_REV_EN_STAT",
            "VUSB_INSERT_STAT", "VEXT_INSERT_STAT",
            "VUSB_DRV_ON_STAT", "VEXT_DRV_ON_STAT",
            "VUSB_OVP_STAT", "VEXT_OVP_STAT",
            "QB1_ON_STAT", "QB2_ON_STAT", "CP_SWITCHING_STAT"
        ]

        ret_map = [["Status", "Value"]]
        for status in status_list:
            value = getattr(self.obj, status)
            if value == 1:
                value = f"{color.bggrn}{color.bold}{color.black}{value}{color.end}"
            ret_map.append([status, value])

        print(tb(ret_map, headers="firstrow", numalign="right"))


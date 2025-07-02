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
                item_list.append(f"{color.blue}{color.bold}{sts_map[reg][m+1]}{color.end}")
            else:
                item_list.append(f"{sts_map[reg][m+1]}")
        ret_map.append(item_list)

    print(tb(ret_map, headers="firstrow"))



class function:

    def __init__(self, obj):

        self.obj = obj
        adc_table = {
            "iin"   : ["IIN_ADC"   , 0.001875],
            "vin"   : ["VIN_ADC"   , 0.00625],
            "wpcin" : ["WPC_IN_ADC", 0.00625],
            "vext"  : ["VEXT_ADC"  , 0.00625],
            "vout"  : ["VOUT_ADC"  , 0.00125],
            "vbat"  : ["VBAT_ADC"  , 0.00125],
            "ibat"  : ["IBAT_ADC"  , 0.00375],
            "c1p"   : ["C1P_ADC"   , 0.00625],
            "ntc"   : ["NTC_ADC"   , 0.01465],
            "tdie"  : ["TDIE_ADC"  , 0.5]
        }

        self.lsb_iin  = 0.001875
        self.lsb_vin  = 0.00625
        self.lsb_wpc  = 0.00625
        self.lsb_vext = 0.00625
        self.lsb_vout = 0.00125
        self.lsb_vbat = 0.00125
        self.lsb_tdie = 0.5
        self.lsb_c1p  = 0.00625
        self.lsb_ibat = 0.00375
        self.lsb_ntc  = 0.01465

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
        
        status_register = [0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29]
        print_byte_status(reg=status_register, obj=self.obj)
    

    @property
    def status_adc(self):
        
        # status_register = [0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F]
        # print_byte_status(reg=status_register, obj=self.obj)

        self.obj.ADC_EN = 1

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

        self.obj.ADC_EN = 0
    

    @property
    def enable_vin_charging(self):

        self.obj.QB_USB_EN = 1
        self.obj.QB_WPC_EN = 0
        self.obj.CP_EN = 1
        print(f"QB_USB_EN = {self.obj.QB_USB_EN}, QB_WPC_EN = {self.obj.QB_WPC_EN}, CP_EN = {self.obj.CP_EN}")
    

    @property
    def enable_wpc_charging(self):

        self.obj.QB_USB_EN = 0
        self.obj.QB_WPC_EN = 1
        self.obj.CP_EN = 1
        print(f"QB_USB_EN = {self.obj.QB_USB_EN}, QB_WPC_EN = {self.obj.QB_WPC_EN}, CP_EN = {self.obj.CP_EN}")
    

    @property
    def disable_charging(self):

        self.obj.QB_USB_EN = 0
        self.obj.QB_WPC_EN = 0
        self.obj.CP_EN = 0
        print(f"QB_USB_EN = {self.obj.QB_USB_EN}, QB_WPC_EN = {self.obj.QB_WPC_EN}, CP_EN = {self.obj.CP_EN}")
    

    @property
    def register_byte_dump(self):

        filename = log.time_stamp(display=False, ret=True) + f"_sc8583_dump"
        xl = excel_frame(file=filename)
        xl.worksheet_title = "sc8583"

        start_row = 2
        header = ["register", "value (dec)", "value (hex)"]
        xl.insert_header = start_row, 2, header

        log.output_set_filename(filename)
        log.output_csv(header)
        
        for reg_addr in range(0x0, 0x3f):

            readback = self.obj.read_byte(reg_addr)
            start_row += 1
            temp = [f"{reg_addr:#04x}", readback, f"{readback:#04x}"]
            xl.insert_list = start_row, 2, temp
            log.output_csv(temp)
        
        for reg_addr in [0x40, 0x41, 0x42, 0x43, 0x44, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x98]:

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
    

    @property
    def status_reg(self):

        control_reg = [
            "MODE", "SS_TIMEOUT", "FREQ_SHIFT", "FSW_SET", "SET_IBAT_SNS_RES", "PMID_IN_RANGE_DIS", 
            "VEXT_SHUT_DOWN_SET", "STANDBY_MODE_SET", "VEXT_OVP", "IIN_OCP", "IIN_REG", "VBAT_REG", 
            "IIN_UCP_DIS", "VBAT_OVP", "VIN_OVP", "WPC_IN_OVP", "IIN_OCP", "VOUT_OVP", "C1P2OUT_OVP", 
            "C1P2OUT_UVP", "IIN_OCP_DG_SET", "VBAT_OVP_DG_SET", "VOUT_OVP_DG_SET", "VEXT_OVP_DG_SET", 
            "VIN_OVP_DG_SET", "WPC_IN_OVP_DG_SET", "IIN_UCP_FALL_DG_SET", "IBAT_OCP_DIS", "NTC_FLT_DIS", 
            "TDIE_REG_DIS"
            ]
        
        for reg in control_reg:
            
            ret = getattr(self.obj, reg)
            print(f"{reg} = {ret:#x} ({ret})")
    

    def save_strings_to_file(self, file_path, strings, mode="a"):
        
        try:
            split_str = strings[0].split(" ")
        except:
            split_str = ""

        suffix = None
        
        try:
            if "reg[0x22]" in split_str:
                offset = [37.5, 75, 150, 300, 600, 1200, 2400, 4800]
                value = split_str[-1:]
                hex_value = int(value, 16)
                iin_ocp = 0
                for shift in range(8):
                    bits = (hex_value>>shift) & 0x01
                    iin_ocp += bits * offset[shift]
                suffix = f"IIN_OCP={round(iin_ocp, 1)}"

            elif "reg[0x1a]" in split_str:
                offset = [37.5, 75, 150, 300, 600, 1200, 2400, 4800]
                value = split_str[-1:]
                hex_value = int(value, 16)
                iin_reg = 0
                for shift in range(8):
                    bits = (hex_value>>shift) & 0x01
                    iin_reg += bits * offset[shift]
                suffix = f"IIN_REG={round(iin_reg, 1)}"

            elif "reg[0x1e]" in split_str:
                offset = [5, 10, 20, 40, 80, 160, 320, 640]
                value = split_str[-1:]
                hex_value = int(value, 16)
                vbat_ovp = 0
                for shift in range(8):
                    bits = (hex_value>>shift) & 0x01
                    vbat_ovp += bits * offset[shift]
                suffix = f"VBAT_OVP={round(vbat_ovp, 1)}"
            
            elif "reg[0x1b]" in split_str:
                offset = [5, 10, 20, 40, 80, 160, 320, 640]
                value = split_str[-1:]
                hex_value = int(value, 16)
                vbat_reg = 0
                for shift in range(8):
                    bits = (hex_value>>shift) & 0x01
                    vbat_reg += bits * offset[shift]
                suffix = f"VBAT_REG={round(vbat_reg, 1)}"
            
            elif "reg[0x1c]" in split_str:
                offset = [125, 250, 500, 1000, 2000, 4000, 8000]
                value = split_str[-1:]
                hex_value = int(value, 16)
                ibat_reg = 0
                for shift in range(7):
                    bits = (hex_value>>shift) & 0x01
                    ibat_reg += bits * offset[shift]
                suffix = f"IBAT_REG={round(ibat_reg, 1)}"
            
            else:
            
                flag_dict = {
                    "0x01" : ["POR_FLAG", "CP_SWITCHING_FLAG", "VIN_PRESENT_FLAG", "VOUT_INSERT_FLAG", "VOUT_TH_REV_EN_FLAG", "VOUT_TH_CHG_EN_FLAG", "VIN_TH_CHG_EN_FLAG", "WPC_IN_TH_CHG_EN_FLAG"],
                    "0x02" : ["VEXT_REMOVE_FLAG", "WPC_REMOVE_FLAG", "VEXT_INSERT_FLAG", "WPC_INSERT_FLAG", "VEXT_OVP_FLAG", "VEXT_DRV_ON_FLAG", "QB1_ON_FLAG", "QB2_ON_FLAG"],
                    "0x03" : ["ADC_DONE_FLAG", "WD_TIMEOUT_FLAG", "IIN_UCP_RISE_FLAG", "TDIE_REG_EXIT_FLAG", "TDIE_REG_ACTIVE_FLAG", "VBAT_REG_ACTIVE_FLAG", "IBAT_REG_ACTIVE_FLAG", "IIN_REG_ACTIVE_FLAG"],
                    "0x04" : ["IIN_OCP_FLAG", "IIN_UCP_FALL_FLAG", "IBAT_OCP_FLAG", "RSVD", "VIN_OVP_FLAG", "WPC_IN_OVP_FLAG", "VOUT_OVP_FLAG", "VBAT_OVP_FLAG"],
                    "0x05" : ["PIN_DIAG_FAIL_FLAG", "CFLY_OPEN_FLAG", "CFLY_SHORT_FLAG", "BST_FAIL_FLAG", "EXT_DRV_SHORT_FLAG", "EXT_FET_OPEN_FLAG", "PMID_ERRORHI_FLAG", "PMID_ERRORLO_FLAG"],
                    "0x06" : ["CONV_OCP_FLAG", "VO12OUT_UVP_FLAG", "C1P2OUT_UVP_FLAG", "C1P2OUT_OVP_FLAG", "NTC_FLT_FLAG", "TSHUT_FLAG", "SS_FAIL_FLAG", "SS_TIMEOUT_FLAG"],
                    "0x07" : ["POR_MASK", "CP_SWITCHING_MASK", "VIN_PRESENT_MASK", "VOUT_INSERT_MASK", "VOUT_TH_REV_EN_MASK", "VOUT_TH_CHG_EN_MASK", "VIN_TH_CHG_EN_MASK", "WPC_IN_TH_CHG_EN_MASK"],
                    "0x08" : ["VEXT_REMOVE_MASK", "WPC_REMOVE_MASK", "VEXT_INSERT_MASK", "WPC_INSERT_MASK", "VEXT_OVP_MASK", "VEXT_DRV_ON_MASK", "QB1_ON_MASK", "QB2_ON_MASK"],
                    "0x09" : ["ADC_DONE_MASK", "IIN_UCP_RISE_MASK", "WD_TIMEOUT_MASK", "TDIE_REG_EXIT_MASK", "TDIE_REG_ACTIVE_MASK", "VBAT_REG_ACTIVE_MASK", "IBAT_REG_ACTIVE_MASK", "IIN_REG_ACTIVE_MASK"],
                    "0x0a" : ["IIN_OCP_MASK", "IIN_UCP_FALL_MASK", "IBAT_OCP_MASK", "RSVD", "VIN_OVP_MASK", "WPC_IN_OVP_MASK", "VOUT_OVP_MASK", "VBAT_OVP_MASK"],
                    "0x0b" : ["PIN_DIAG_FAIL_MASK", "CFLY_OPEN_MASK", "CFLY_SHORT_MASK", "BST_FAIL_MASK", "EXT_DRV_SHORT_MASK", "EXT_FET_OPEN_MASK", "PMID_ERRORHI_MASK", "PMID_ERRORLO_MASK"],
                    "0x0c" : ["CONV_OCP_MASK", "VO12OUT_UVP_MASK", "C1P2OUT_UVP_MASK", "C1P2OUT_OVP_MASK", "NTC_FLT_MASK", "TSHUT_MASK", "SS_FAIL_MASK", "SS_TIMEOUT_MASK"],
                    "0x0d" : ["RSVD", "CP_SWITCHING_STAT", "VIN_PRESENT_STAT", "VOUT_INSERT_STAT", "VOUT_TH_REV_EN_STAT", "VOUT_TH_CHG_EN_STAT   VIN_TH_CHG_EN_STAT", "WPC_IN_TH_CHG_EN_STAT"],
                    "0x0e" : ["VOUT_OK_SW_AVDD_STAT", "RSVD", "VEXT_INSERT_STAT", "WPC_INSERT_STAT", "VEXT_OVP_STAT", "VEXT_DRV_ON_STAT", "QB1_ON_STAT", "QB2_ON_STAT"],
                    "0x0f" : ["ADC_DONE_STAT", "WD_TIMEOUT_STAT", "IIN_UCP_RISE_STAT", "RSVD", "TDIE_REG_ACTIVE_STAT", "VBAT_REG_ACTIVE_STAT  IBAT_REG_ACTIVE_STAT", "IIN_REG_ACTIVE_STAT"],
                    "0x10" : ["IIN_OCP_STAT", "IIN_UCP_FALL_STAT", "IBAT_OCP_STAT", "RSVD", "VIN_OVP_STAT", "WPC_IN_OVP_STAT", "VOUT_OVP_STAT", "VBAT_OVP_STAT"],
                    "0x11" : ["PIN_DIAG_FAIL_STAT", "CFLY_OPEN_STAT", "CFLY_SHORT_STAT", "BST_FAIL_STAT", "EXT_DRV_SHORT_STAT", "EXT_FET_OPEN_STAT", "PMID_ERRORHI_STAT", "PMID_ERRORLO_STAT"],
                    "0x12" : ["CONV_OCP_STAT", "VO12OUT_UVP_STAT", "C1P2OUT_UVP_STAT", "C1P2OUT_OVP_STAT", "NTC_FLT_STAT", "TSHUT_STAT", "SS_FAIL_STAT", "SS_TIMEOUT_STAT"]
                }

                for key, flags in flag_dict.items():

                    if f"reg[{key}]" in split_str:
                        flag_string = ""
                        value = split_str[-1:]
                        hex_value = int(value, 16)
                        for shift in range(8):
                            bits = (hex_value>>(7-shift)) & 0x01
                            flag_string += f"{flags[shift]}={bits} "
                        suffix = flag_string
        except:
            pass

        try:
            with open(file_path, mode, encoding="utf-8") as file:
                basic_string = f"{strings[0].strip()}"
                string_suffix = basic_string + f" --> {suffix}\n"
                file.write(string_suffix)
        except:
            pass


    def log_sorting(self, file_path, keyword):
        
        dir_name, base_name = os.path.split(file_path)
        name, ext = os.path.splitext(base_name)

        if ext == ".txt":
            new_base = f"{name}_sorting{ext}"
        else:
            new_base = f"{name}_sorting.txt"

        sorting_file = os.path.join(dir_name, new_base)

        # log.forcedLog(dir_name, base_name, new_base, sorting_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if keyword in line:
                        # log.forcedLog(f"{keyword}, {line}")
                        self.save_strings_to_file(sorting_file, [line])
            return "done"
        except FileNotFoundError:
            return f"error: file not found at {file_path}"
        except Exception as e:
            return f"an error occurred: {str(e)}"
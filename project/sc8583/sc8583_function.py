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

        # print(f"QB_USB_EN = {self.obj.QB_USB_EN}, QB_WPC_EN = {self.obj.QB_WPC_EN}, CP_EN = {self.obj.CP_EN}")
    

    @property
    def enable_wpc_charging(self):

        self.obj.QB_USB_EN = 0
        self.obj.QB_WPC_EN = 1
        self.obj.CP_EN = 1

        # print(f"QB_USB_EN = {self.obj.QB_USB_EN}, QB_WPC_EN = {self.obj.QB_WPC_EN}, CP_EN = {self.obj.CP_EN}")
    

    @property
    def disable_charging(self):

        self.obj.QB_USB_EN = 0
        self.obj.QB_WPC_EN = 0
        self.obj.CP_EN = 0

        # print(f"QB_USB_EN = {self.obj.QB_USB_EN}, QB_WPC_EN = {self.obj.QB_WPC_EN}, CP_EN = {self.obj.CP_EN}")
    

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
    

    def _get_index(self, list_item, keyword):

        matches = [(i, item) for i, item in enumerate(list_item) if f"reg[{keyword:#04x}]" in item]
        
        if len(matches) > 0:
            index = matches[0][0]
            value = matches[0][1]
            return index, value
        else:
            return 0


    def save_strings_to_file(self, file_path, strings, sts_map, mode="a"):
        
        try:
            split_str = strings[0].split(" ")
        except:
            split_str = ""
        
        suffix = ""
        filtered = False
        
        reg_dict = {
            0x22 : {
                "offset" : [37.5, 75, 150, 300, 600, 1200, 2400, 4800],
                "index"  : 8,
                "suffix" : f"IIN_OCP"
                },
            0x1a : {
                "offset" : [37.5, 75, 150, 300, 600, 1200, 2400, 4800],
                "index"  : 8,
                "suffix" : f"IIN_REG"
                },
            0x1e : {
                "offset" : [5, 10, 20, 40, 80, 160, 320, 640],
                "index"  : 8,
                "suffix" : f"VBAT_OVP"
                },
            0x1b : {
                "offset" : [5, 10, 20, 40, 80, 160, 320, 640],
                "index"  : 8,
                "suffix" : f"VBAT_REG"
                },
            0x1c : {
                "offset" : [125, 250, 500, 1000, 2000, 4000, 8000],
                "index"  : 7,
                "suffix" : f"IBAT_REG"
                }
        }

        for reg, prop in reg_dict.items():
                
                keyword_ret = self._get_index(split_str, reg) # splited list, reg (int)
                if isinstance(keyword_ret, tuple):

                    reg_index = keyword_ret[0]
                    # reg_addr  = keyword_ret[1]
                    val_index = reg_index + 2
                    value     = int(split_str[val_index].strip(), 16)
                    offset    = prop["offset"]
                    msb       = prop["index"]
                    suffix    = prop["suffix"]

                    ret = 0
                    for shift in range(msb):
                        bits = (value>>shift) & 0x01
                        ret += bits * offset[shift]
                    
                    suffix = f"{suffix}={round(ret, 1)}"
                    filtered = True
        
        list_status = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12]

        for sts_addr in list_status:

            keyword_ret = self._get_index(split_str, sts_addr)
            if isinstance(keyword_ret, tuple):
                reg_index = keyword_ret[0]
                # reg_addr  = keyword_ret[1]
                val_index = reg_index + 2
                reg_value = int(split_str[val_index].strip(), 16)
            
                parsing_list = []
                for shift in range(8):
                    parsing_list.append((reg_value>>shift) & 0x1)
                parsing_list.reverse()
                
                for m in range(8):
                    suffix += f"{sts_map[sts_addr][m+1]}={parsing_list[m]}"
                    if m<7:
                        suffix += ", "
                filtered = True
        
        try:
            with open(file_path, mode, encoding="utf-8") as file:
                basic_string = f"{strings[0].strip()}"

                if filtered:
                    string_suffix = basic_string + f" --> {suffix}\n"
                else:
                    string_suffix = basic_string + f"\n"
                file.write(string_suffix)
        except:
            pass


    def log_sorting(self, file_path, keyword):
        
        dir_name, base_name = os.path.split(file_path)
        name, ext = os.path.splitext(base_name)
        stamp = log.time_stamp(display=False, ret=True)

        if ext == ".txt":
            new_base = f"{stamp} - {name}_sorting{ext}"
        else:
            new_base = f"{stamp} - {name}_sorting.txt"

        sorting_file = os.path.join(dir_name, new_base)

        # log.forcedLog(dir_name, base_name, new_base, sorting_file)

        with open(f"{self.device_path}/{self.device}_{self.revision}_status.yaml") as yaml_device:
            status_map = yaml.safe_load(yaml_device)
    
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if keyword in line:
                        # log.forcedLog(f"{keyword}, {[line]}")
                        self.save_strings_to_file(sorting_file, [line], status_map)
            return "done"
        except FileNotFoundError:
            return f"error: file not found at {file_path}"
        # except Exception as e:
        #     return f"an error occurred: {str(e)}"
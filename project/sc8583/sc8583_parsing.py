from tabulate import tabulate as tb
from interface.cui_colors import color
from interface.cui_logger import logger as log
import yaml, sys, os, re


class parsing:

    def __init__(self, obj):

        self.obj = obj

        self.basic_keyword = [
            "usb_typec_handle_id_power_status", # for PDO list
            "sb_set_dc_ta_forced_op_max_mode",
            "sb_set_dc_ta_op_max_mode",
            "sec_pd_get_apdo_max_power",
            "VOTER_SLATE",
            "sec_bat_check_dc_step_charging",
            "sec_direct_chg_check_charging_source",
            "sec_direct_chg_set_direct_charge",
            "PASS_THROUGH",
            "vwpc diff",
            "sc8583",
            "SC8583",
            "SC8583_INFO",
            "SC8583_ERR",
            "sec_direct_charger",
            "sc_charger",
            "sc8583-charger",
            "sec_bat_set_property",
            "sc8583_dump_registers", 
            "sec_wireless_set_property", 
            "sec_direct_chg_set_property"
        ]

        self.vendor_keyword = [
            "max77775",
            "usb_notify",
            "cps4059",
            "sec_bat_show_attrs",
            "mfc_set_pps_vout"
        ]

        self.keyword = None
        self.merged = None
        self.merged_keyword = self.basic_keyword + self.vendor_keyword
        self.select_keyword(merged=self.merged)
        self.ret_regpage = self.obj.get_regpage()


    def select_keyword(self, merged:bool):
        
        self.merged = merged

        if merged:
            self.keyword = self.merged_keyword
        else:
            self.keyword = self.basic_keyword


    def step_1_matching(self, dump:str, vendor_keyword:bool):

        # dump : file name
        # step 1. keyword decision
        # step 2. parsing filename desicion
        # step 3. open dump
        # step 4. compare with keyword
        # step 5. store the line when any keyword is in the line

        self.select_keyword(merged=vendor_keyword)

        file_path, file_name = os.path.split(dump)
        name, ext = os.path.splitext(file_name)

        if vendor_keyword:
            name = name + "_vendor"

        stamp = log.time_stamp(display=False, ret=True)

        if ext == "":
            new_base = f"{stamp} - {name}_parsing.txt"
        else:
            new_base = f"{stamp} - {name}_parsing{ext}"

        parsing_file = os.path.join(file_path, new_base)

        with open(dump, "rb") as dump: # binary mode

            for line in dump:
                decoded_line = line.decode("utf-8", errors="ignore")
                
                if any(keyword in decoded_line for keyword in self.keyword):

                    try:
                        with open(parsing_file, "a") as parsing:
                            parsing.write(decoded_line)
                    except:
                        pass

                    if "sc8583_dump_registers" in decoded_line:
                        ret_log = self.step_2_matching(regpage=self.ret_regpage, data=decoded_line)
                        reg_log = ""

                        for value in ret_log:
                            reg_log += (value+"\n")
                            
                        if reg_log != None:
                            with open(parsing_file, "a") as parsing:
                                parsing.write(reg_log)
                                parsing.write("\n")
                    
                    elif "sc_charger_set_property" in decoded_line:
                        reg_log = self.step_3_matching(data=decoded_line)

                        if reg_log != None:
                            with open(parsing_file, "a") as parsing:
                                parsing.write(reg_log)
                                parsing.write("\n")
                    
                    elif "sc_charger_timer_work" in decoded_line:
                        reg_log = self.step_4_matching(data=decoded_line)
                        
                        if reg_log != None:
                            with open(parsing_file, "a") as parsing:
                                parsing.write(reg_log)
                                parsing.write("\n")


    def step_2_matching(self, regpage, data):

        # regpage format
        # key : register name
        # value : list
        # value[0] : splited number
        # value[1] : name
        # value[2] : address list
        # value[3] : msb list
        # value[4] : lsb list
        # value[5] : real msb list
        # value[6] : real lsb list
        # value[7] : permission
        # value[8] : type

        # data format
        # key : register address (int)
        # value : register value (int)

        # addr_start = 0x00
        # addr_end   = 0x2b # based on the datasheet user register page

        addr_range = [
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12,
            0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 
            0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 
            0x2b
            ]

        # sweep register address
        # check step 1 : register address == address in dump
        # check step 2 : find the same register address in the info_list from regpage
        # store the register name into temp list
        # store "register[msb:lsb]=value" to ret dictionary

        splited_data = data.split("sc8583_dump_registers ")[1]
        pairs = splited_data.split(", ")

        datas = {} # key=register, value=value
        ret = list()

        for pair in pairs:
            clean_pair = pair.replace("[", "").replace("]", ",")
            addr, value = clean_pair.split(",")
            datas[int(addr,16)] = int(value,16)

        for addr in addr_range:

            temp = [0 for _ in range(8)]

            for dump_addr in datas.keys():

                if addr == dump_addr:

                    for register, info_list in regpage.items():
                        
                        if addr in info_list[2]:

                            # print(f"{addr:#04x} : {register}[{info_list[5][0]}:{info_list[6][0]}]")

                            if info_list[0] == 1:

                                temp[info_list[3][0]] = info_list[1] # store the regiser name to the list in the msb index

            for index in reversed(range(8)):

                reg_name = temp[index]
                dump_value = datas.get(addr)

                if reg_name != 0:

                    msb = regpage.get(reg_name)[3][0]
                    lsb = regpage.get(reg_name)[4][0]
                    real_msb = regpage.get(reg_name)[5][0]
                    real_lsb = regpage.get(reg_name)[6][0]

                    bit_length = msb - lsb
                    raw_value = datas.get(addr)

                    # 1. bit shift down >> lsb
                    # 2. masking high side with [7:msb+1]

                    shifted_dump_value = dump_value >> lsb

                    masking_b = 0
                    for mask in range(0, bit_length+1):
                        masking_b += (1<<mask)
                    
                    masked_value = shifted_dump_value & masking_b

                    ret.append(f"     ---------> {addr:#04x}[{msb}:{lsb}] {reg_name}={masked_value:#x}")
                    log.infoLog(f"{addr:#04x}[{msb}:{lsb}] {reg_name}={masked_value:#x} (shift={lsb}, dump value={dump_value:#04x}, masking={masking_b:#04x})")
        
        return ret
    

    def step_3_matching(self, data):

        # pattern that looks for the specific format

        pattern1 = r"set_property:\s*prop=(\d+),\s*val=(\d+)"
        match = re.search(pattern1, data)

        if match:
            prop = int(match.group(1))
            value = int(match.group(2))

            if (prop==4) and (value==0):
                ret = f"     ---------> prop={prop}, val={value} // cable detach"
            elif (prop==4) and (value==1):
                ret = f"     ---------> prop={prop}, val={value} // select wired charging"
            elif (prop==4) and (value==49):
                ret = f"     ---------> prop={prop}, val={value} // select wireless charging"
            elif prop==31:
                ret = f"     ---------> prop={prop}, val={value} // Target VBAT {value}mV"
            elif (prop==1089) or (prop==38):
                ret = f"     ---------> prop={prop}, val={value} // Target IIN {value}mA"
            elif prop==1102:
                if value==1:
                    ret = f"     ---------> prop={prop}, val={value} // DCIC Start"
                else:
                    ret = f"     ---------> prop={prop}, val={value} // DCIC Stop"
        
        if "sc_charger_set_property: POWER_SUPPLY" in data:

            match = re.search(r'sc_charger_set_property: (.*)', data)
            if match:
                res = match.group(1)
                ret = f"     ---------> {res}"
        
        else:
            ret = None

        return ret
    

    def step_4_matching(self, data):

        # pattern that looks for the specific format

        pattern = r'sc_charger_timer_work:\s*timer id=(\d+),\s*charging_state=(\w+)'
        match = re.search(pattern, data)

        ret = None

        if match:
            timer = int(match.group(1))
            state = match.group(2)  # this is a string, not an integer
        

            if timer == 0:
                ret = f"     ---------> DCIC Process state : TIMER_ID_NONE"
            elif timer == 1:
                ret = f"     ---------> DCIC Process state : TIMER_VBATMIN_CHECK"
            elif timer == 2:
                ret = f"     ---------> DCIC Process state : TIMER_PRESET_DC"
            elif timer == 3:
                ret = f"     ---------> DCIC Process state : TIMER_PRESET_CONFIG"
            elif timer == 4:
                ret = f"     ---------> DCIC Process state : TIMER_CHECK_ACTIVE"
            elif timer == 5:
                ret = f"     ---------> DCIC Process state : TIMER_ADJUST_CCMODE"
            elif timer == 6:
                ret = f"     ---------> DCIC Process state : TIMER_ENTER_CCMODE"
            elif timer == 7:
                ret = f"     ---------> DCIC Process state : TIMER_CHECK_CCMODE"
            elif timer == 8:
                ret = f"     ---------> DCIC Process state : TIMER_ENTER_CVMODE"
            elif timer == 9:
                ret = f"     ---------> DCIC Process state : TIMER_CHECK_CVMODE"
            elif timer == 10:
                ret = f"     ---------> DCIC Process state : TIMER_PDMSG_SEND"
        
        return ret


    def get_index(self, list_item, keyword):

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
                
                keyword_ret = self.get_index(split_str, reg) # splited list, reg (int)
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


    def log_sorting(self, file_path):
        
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
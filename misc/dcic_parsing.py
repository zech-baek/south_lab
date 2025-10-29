from interface.cui_colors import color
from interface.cui_logger import logger as log
from project.get_device_info import get_map, get_regpage

from tabulate import tabulate as tb
import yaml, sys, os, re


class parsing:

    def __init__(self):

        self.logging = False

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
            "sc8563",
            "SC8563",
            "SC8563_INFO",
            "SC8563_ERR",
            "sec_direct_charger",
            "sc_charger",
            "sc8583-charger",
            "sec_bat_set_property",
            "sc8583_dump_registers ", 
            "sc8563_dump_registers ", 
            "sec_wireless_set_property", 
            "sec_direct_chg_set_property",
            "UIWirelessFastCharge",
            "UIDirectChargeTest"
        ]

        self.vendor_keyword = [
            "max77775",
            "usb_notify",
            "cps4059",
            "sec_bat_show_attrs",
            "mfc_set_pps_vout",
            "mfc_wpc_irq_thread",
            "@PPS",
            "sm5446",
            "detach"
        ]

        self.merged_keyword = self.basic_keyword + self.vendor_keyword


    def init_parameter(self, source_file:str, device:str, revision:str, vendor_keyword:bool) -> None:
        
        self.source_file = source_file
        self.device = device
        self.revision = revision

        if vendor_keyword:
            self.keyword = self.merged_keyword
        else:
            self.keyword = self.basic_keyword
        
        self.regmap  = get_map(device=self.device, revision=self.revision)
        self.regpage = get_regpage(device=self.device, revision=self.revision)

        if "sc8583" in self.device:
            self.addr_range = [
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12,
            0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 
            0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 
            0x2b
            ]

        elif "sc8563" in self.device:
            self.addr_range = [
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12,
            0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 
            0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a
            ]

        else:
            raise Exception("device number is not applicable")


    def start_parsing(self, dump:str, device:str, revision:str, vendor_keyword:bool) -> None:

        # dump : file name
        # step 1. keyword decision
        # step 2. parsing filename desicion
        # step 3. open dump
        # step 4. compare with keyword
        # step 5. store the line when any keyword is in the line

        self.init_parameter(source_file=dump, device=device, revision=revision, vendor_keyword=vendor_keyword)
        self.step_1_matching()

        file_path, file_name = os.path.split(self.source_file)
        parsing_file = os.path.join(file_path, "process done")

        # clear the parameters before exit the method
        self.source_file = None
        self.device      = None
        self.revision    = None
        self.keyword     = None
        self.regmap      = None
        self.regpage     = None
        self.addr_range  = None

        print(f"[{log.time_stamp(display=False, ret=True)}] finish dump and adcparsing, clear the parameters")
        
        with open(parsing_file, "a") as parsing:
            parsing.write(f" ")


    def step_1_matching(self) -> None:

        file_path, file_name = os.path.split(self.source_file)
        name, ext = os.path.splitext(file_name)

        if self.vendor_keyword:
            name = name + "_vendor"

        stamp = log.time_stamp(display=False, ret=True)

        if ext == "":
            new_base = f"{stamp} - {name}_parsing.txt"
            adc_base = f"{stamp} - {name}_parsing_adc.txt"
        else:
            new_base = f"{stamp} - {name}_parsing{ext}"
            adc_base = f"{stamp} - {name}_parsing_adc{ext}"

        parsing_file = os.path.join(file_path, new_base)
        adc_file = os.path.join(file_path, adc_base)

        print(f"[{log.time_stamp(display=False, ret=True)}] start dump parsing -> save to {parsing_file}")
        print(f"[{log.time_stamp(display=False, ret=True)}] start adc log      -> save to {adc_file}")

        count_sc_rel = 0

        with open(self.source_file, "rb") as dump: # binary mode

            for line in dump:
                decoded_line = line.decode("utf-8", errors="ignore")

                # if "SC_REL" in decoded_line:
                if re.search(r"SC_REL", decoded_line, re.IGNORECASE):

                    driver_version = r"SC_REL\((.*?)\)"
                    is_sc_rel = re.search(driver_version, decoded_line)

                    if is_sc_rel:
                        sc_rel = is_sc_rel.group(1)
                        count_sc_rel += 1
                    if count_sc_rel == 1:
                        print(f"[{log.time_stamp(display=False, ret=True)}] SC_REL : {sc_rel}")
                
                if any(keyword in decoded_line for keyword in self.keyword):

                    try:
                        with open(parsing_file, "a") as parsing:
                            parsing.write(decoded_line)
                    except:
                        pass
                    
                    dump_code = self.device + "_dump_registers "

                    if dump_code in decoded_line:
                        ret_reglog = self.step_2_matching(dump_code=dump_code, data=decoded_line)
                        reg_log = ""

                        if ret_reglog is not None:
                            for value in ret_reglog:
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
                    
                    elif "sc_charger_check_dcmode_status" in decoded_line:
                        reg_log = self.step_5_matching(data=decoded_line)

                        if self.logging:
                            print(f"adc_file : {adc_file}")
                            print(f"reg_log : {reg_log}")

                        if reg_log != None:
                            with open(adc_file, "a") as parsing:
                                parsing.write(reg_log)
                                parsing.write("\n")
                    
                    else:
                        scan_list = {
                            "sec-battery samsung_mobile_device:battery: usb_typec_handle_id_power_status: " : "usb_typec_handle_id_power_status",
                            "sb_set_dc_ta_op_max_mode: " : "sb_set_dc_ta_op_max_mode",
                            "sc_charger_set_new_iin: " : "set_new_iin",
                            "sc_charger_set_new_voltage_and_current: sc_chg->" : "set_new_voltage_and_current",
                            "mfc_set_pps_vout" : "mfc_set_pps_vout (wpc pps request)",
                            "sc_charger_request_power" : "pps request"
                        }
                        
                        for scan_item, log_text in scan_list.items():
                            if scan_item in decoded_line:
                                reg_log = decoded_line.split(scan_item)[1]

                                if scan_item == "mfc_set_pps_vout":
                                    pps_match = re.search(r'\((\d+)mv,', decoded_line)
                                    pps = int(pps_match.group(1)) if pps_match else None
                                    rx_out_match = re.search(r'=\s*(\d+)\s*mV', decoded_line)
                                    rx_out = int(rx_out_match.group(1)) if rx_out_match else None
                                    if pps != None and rx_out != None:
                                        diff = (pps-rx_out)/1000 # mV to V scale
                                        suffix = f"diff={diff:.03f}"
                                        cleaned_decoded_line = decoded_line.strip("\n")
                                        for_excel = f"        // {cleaned_decoded_line} -- wpc pps request, {pps/1000}, {rx_out/1000}, {diff}\n"
                                else:
                                    suffix = ""
                                    for_excel = None
                                
                                with open(parsing_file, "a") as parsing:
                                    parsing.write(f"        // {log_text} : {suffix} {reg_log}")
                                    if for_excel != None:
                                        parsing.write(for_excel)
                                    parsing.write("\n")


    def step_2_matching(self, dump_code, data):

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

        # sweep register address
        # check step 1 : register address == address in dump
        # check step 2 : find the same register address in the info_list from regpage
        # store the register name into temp list
        # store "register[msb:lsb]=value" to ret dictionary

        try:
            splited_data = data.split(dump_code)[1]
            pairs = splited_data.split(", ")

            datas = {} # key=register, value=value
            ret = list()

            for pair in pairs:
                clean_pair = pair.replace("[", "").replace("]", ",")
                addr, value = clean_pair.split(",")
                datas[int(addr,16)] = int(value,16)

            for addr in self.addr_range:

                temp = [0 for _ in range(8)]

                for dump_addr in datas.keys():

                    if addr == dump_addr:

                        for register, info_list in self.regpage.items():
                            
                            if addr in info_list[2]:

                                # print(f"{addr:#04x} : {register}[{info_list[5][0]}:{info_list[6][0]}]")

                                if info_list[0] == 1:

                                    temp[info_list[3][0]] = info_list[1] # store the regiser name to the list in the msb index

                for index in reversed(range(8)):

                    reg_name = temp[index]
                    dump_value = datas.get(addr)

                    if reg_name != 0:

                        msb = self.regpage.get(reg_name)[3][0]
                        lsb = self.regpage.get(reg_name)[4][0]
                        real_msb = self.regpage.get(reg_name)[5][0]
                        real_lsb = self.regpage.get(reg_name)[6][0]

                        bit_length = msb - lsb
                        raw_value = datas.get(addr)

                        # 1. bit shift down >> lsb
                        # 2. masking high side with [7:msb+1]

                        shifted_dump_value = dump_value >> lsb

                        masking_b = 0
                        for mask in range(0, bit_length+1):
                            masking_b += (1<<mask)
                        
                        masked_value = shifted_dump_value & masking_b

                        star_suffix = [
                            "CP_SWITCHING_STAT",
                            "MODE",
                            "VIN_PRESENT_STAT",
                            "VEXT_INSERT_STAT",
                            "VEXT1_INSERT_STAT",
                            "VEXT2_INSERT_STAT",
                            "WPC_INSERT_STAT",
                            "CP_EN"
                            ]
                        
                        suffix = ""
                        for reg_check in star_suffix:
                            if re.search(reg_check, reg_name, re.IGNORECASE):
                                suffix = "        ***"

                        ret.append(f"        // {addr:#04x}[{msb}:{lsb}] {reg_name}={masked_value:#x} {suffix}")
                        # log.infoLog(f"{addr:#04x}[{msb}:{lsb}] {reg_name}={masked_value:#x} (shift={lsb}, dump value={dump_value:#04x}, masking={masking_b:#04x})")
            
            return ret
        
        except:
            print(f"[{log.time_stamp(display=False, ret=True)}] wrong format - {dump_code} {data}")
            return None
    

    def step_3_matching(self, data):

        # pattern that looks for the specific format

        pattern1 = r"set_property:\s*prop=(\d+),\s*val=(\d+)"
        match = re.search(pattern1, data)

        if match:
            prop = int(match.group(1))
            value = int(match.group(2))

            if (prop==4) and (value==0):
                ret = f"        // prop={prop}, val={value} // cable detach"
            elif (prop==4) and (value==1):
                ret = f"        // prop={prop}, val={value} // select wired charging"
            elif (prop==4) and (value==49):
                ret = f"        // prop={prop}, val={value} // select wireless charging"
            elif prop==31:
                ret = f"        // prop={prop}, val={value} // Target VBAT {value}mV"
            elif (prop==1089) or (prop==38):
                ret = f"        // prop={prop}, val={value} // Target IIN {value}mA"
            elif prop==1102:
                if value==1:
                    ret = f"        // prop={prop}, val={value} // DCIC Start"
                else:
                    ret = f"        // prop={prop}, val={value} // DCIC Stop"
        
        if "sc_charger_set_property: POWER_SUPPLY" in data:

            match = re.search(r'sc_charger_set_property: (.*)', data)
            if match:
                res = match.group(1)

                if "POWER_SUPPLY_EXT_PROP_PWR_CTRL_UPDATE" in res:
                    ret = f"        // {res}, reached to target power, sync rx vout to pps ta_vol\n"
                else:
                    ret = f"        // {res}\n"
        
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
                ret = f"        // DCIC Process state : TIMER_ID_NONE"
            elif timer == 1:
                ret = f"        // DCIC Process state : TIMER_VBATMIN_CHECK"
            elif timer == 2:
                ret = f"        // DCIC Process state : TIMER_PRESET_DC"
            elif timer == 3:
                ret = f"        // DCIC Process state : TIMER_PRESET_CONFIG"
            elif timer == 4:
                ret = f"        // DCIC Process state : TIMER_CHECK_ACTIVE"
            elif timer == 5:
                ret = f"        // DCIC Process state : TIMER_ADJUST_CCMODE"
            elif timer == 6:
                ret = f"        // DCIC Process state : TIMER_ENTER_CCMODE"
            elif timer == 7:
                ret = f"        // DCIC Process state : TIMER_CHECK_CCMODE"
            elif timer == 8:
                ret = f"        // DCIC Process state : TIMER_ENTER_CVMODE"
            elif timer == 9:
                ret = f"        // DCIC Process state : TIMER_CHECK_CVMODE"
            elif timer == 10:
                ret = f"        // DCIC Process state : TIMER_PDMSG_SEND"
            elif timer == 13:
                ret = f"        // DCIC Process state : TIMER_CHECK_BYPASSMODE"
            elif timer == 14:
                ret = f"        // DCIC Process state : TIMER_DCMODE_CHANGE"
        
        return ret


    def step_5_matching(self, data:str) -> str:

        ret = None
        re_scale = 1000_000

        if data.startswith('['):
            timeline = data.split(']')[0].replace('[', '').strip()
        else:
            parts = data.split(' ', 2)
            timeline = f"{parts[0]} {parts[1]}"
        
        iin_match         = re.search(r'iin:(\d+)', data)
        iin_target_match  = re.search(r'iin_target:(\d+)', data)
        vbat_match        = re.search(r'vbat:(\d+)', data)
        vbat_target_match = re.search(r'vbat_target:(\d+)', data)
        power_match       = re.search(r'power_uw:(\d+)', data)
        vbus_match        = re.search(r'vbus:(\d+)', data)
        vwpc_match        = re.search(r'vbus_wpc:(\d+)', data)
        vbat_dcic_match   = re.search(r'vbat_dcic:(\d+)', data)

        if self.logging:
            print(data)
            print(f"iin_match         : {iin_match        }")
            print(f"iin_target_match  : {iin_target_match }")
            print(f"vbat_match        : {vbat_match       }")
            print(f"vbat_target_match : {vbat_target_match}")
            print(f"power_match       : {power_match      }")
            print(f"vbus_match        : {vbus_match       }")
            print(f"vwpc_match        : {vwpc_match       }")
            print(f"vbat_dcic_match   : {vbat_dcic_match  }")

        if any(item is not None for item in [iin_match, iin_target_match, vbat_match, vbat_target_match, power_match, vbus_match, vwpc_match, vbat_dcic_match]):

            iin_value = int(iin_match.group(1))/re_scale if iin_match else None
            iin_target_value = int(iin_target_match.group(1))/re_scale if iin_target_match else None
            vbat_value = int(vbat_match.group(1))/re_scale if vbat_match else None
            vbat_target_value = int(vbat_target_match.group(1))/re_scale if vbat_target_match else None
            power_value = int(power_match.group(1))/re_scale if power_match else None
            vbus_value = int(vbus_match.group(1))/re_scale if vbus_match else None
            vwpc_value = int(vwpc_match.group(1))/re_scale if vwpc_match else None
            vbat_dcic_value = int(vbat_dcic_match.group(1))/re_scale if vbat_dcic_match else None

            vbat_diff = vbat_value - vbat_dcic_value

            try:
                ret = f"{timeline}, iin={iin_value:.03f}A, iin_target={iin_target_value:.03f}A, vbat={vbat_value:.03f}V, vbat_target={vbat_target_value:.03f}V, power={power_value:.03f}W, vbus={vbus_value:.03f}V, vwpc={vwpc_value:.03f}V, vbat_dcic={vbat_dcic_value:.03f}V, vbat_diff={vbat_diff:.03f}V"
            except:
                return None

            if self.logging:
                print(f"iin_value : {iin_value}")
                print(f"iin_target_value : {iin_target_value}")
                print(f"vbat_value : {vbat_value}")
                print(f"vbat_target_value : {vbat_target_value}")
                print(f"power_value : {power_value}")
                print(f"vbus_value : {vbus_value}")
                print(f"vwpc_value : {vwpc_value}")
                print(f"vbat_dcic_value : {vbat_dcic_value}")
        
        else:
            ret = None

        return ret
'''
structure

1. __init__
- define keyword

2. init_parameter
- initialize the source file, device and revision
- merge the basic keyword and vendor's keyword
- get the regmap and regpage
- define the address range regarding the device

3. start_parsing
- parameters
	- dump : file name
	- device : device name
	- revision : revision number
	- ventor_keyword (bool) : option for adding vendor's keyword
- method call
	--> init_parameter()
	--> step_1_mathcing()
		- make "_parsing.txt" and "_parsing_adc.txt"
		- open the source file in binary mode
			- check "SC_REL"
			- check "LAST KMSG"
			- check any keyword defined in init_parameter()
			- "dump_register" : call step_2_matching()
			- "sc_charger_set_property" : call step_3_mathcing()
			- "sc_charger_timer_work" : call step_4_mathcing()
			- "sc_charger_check_dcmode_status" : call step_5_matching()
			- other cases : check the words in scan_list
- make "process done" file
- clear the parameters before exit the method
'''


from interface.cui_logger import logger as log
from project.get_device_info import get_map, get_regpage

import os, re, mmap


class parsing:

    def __init__(self, logging=False):

        self.logging = logging

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
            "sc8563-charger",
            "sec_bat_set_property",
            "sc8583_dump_registers ", 
            "sc8563_dump_registers ", 
            "sec_wireless_set_property", 
            "sec_direct_chg_set_property",
            "UIWirelessFastCharge",
            "UIDirectChargeTest",
            "LAST KMSG",
            "fsck.f2fs",
            "batt_current_ua_now",
            "sc8563_enable_charge enable DCIC"
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
            "detach",
            "DETACH",
            "DETACHED"
        ]

        self.error_code = {
            0x400001 : "VIN_UVLO",
            0x400002 : "VIN_OVP",
            0x400003 : "VOUT OVP",
            0x400004 : "VOUT UVLO",
            0x400005 : "VBAT OVP",
            0x400006 : "IBUS OCP",
            0x400007 : "IBUS UCP",
            0x400008 : "IBAT OCP",
            0x400009 : "CFLY SHORT",
            0x400010 : "CN SHORT",
            0x40001A : "VIN SHORT",
            0x40001B : "VOUT SHORT",
            0x40001C : "Thermal Shutdown",
            0x40001D : "Watchdog Timer",
            0x40001E : "Charger Timer",
            0x40001F : "NTC Protection",
            0x400020 : "VBUS2VOUT Relative UVP",
            0x400021 : "VBUS2VOUT Rekative OVP",
            0x400022 : "MID2VOUT Relative UVP",
            0x400023 : "MID2VOUT Relative OVP",
            0x400024 : "VDSQRB OVP",
            0x400025 : "Reverse Blocking",
            0x400026 : "Thermal Regulation",
            0x400027 : "Die Temperature warning",
            0x400028 : "Soft Start Timeout",
            0x400029 : "PIN DIAG FAIL",
            0x40002A : "POWER NG",
            0x40002B : "VEXT1 OVLO",
            0x40002C : "VEXT2 OVLO",
            0x40002D : "VEXT1 UVLO",
            0x40002E : "VEXT2 UVLO",
            0x40002F : "CHAR RCP",
            0x400030 : "CFLY Open Detection",
            0x400031 : "BST UVP",
            0x400032 : "PVDD UVP",
            0x400033 : "Regulation_Timout",
            0x400034 : "RVSBST OCP",
            0x400035 : "CHGR RCP",
            0x400036 : "New feature1 (VBAT<3.1V or FG Vnow issue)",
            0x400037 : "New feature2 (PD communication error)",
            0x400038 : "New feature3 (Not enough WPC condition)",
            0x400039 : "New feature4",
            0x40003A : "New feature5",
            0x40003B : "New feature6",
            0x40003C : "New feature7",
            0x40003D : "New feature8 (PMID_ERROR_HI, before SW)",
            0x40003E : "New feature9 (PMID_ERROR_LO, before SW)",
            0x40003F : "New feature10 (VWPC_OVP)"
        }

        self.merged_keyword = self.basic_keyword + self.vendor_keyword


    def count_lines(self, filename:str) -> int:

        with open(filename, 'r+') as f:
            mm = mmap.mmap(f.fileno(), 0)
            count = 0
            while mm.readline():
                count += 1
            mm.close()

        return count
    

    def init_parameter(self, source_file:str, device:str, revision:str, vendor_keyword:bool) -> None:
        
        self.txt_lines = self.count_lines(source_file)
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
            0x2b, 0x40, 0x41, 0x42, 0x43, 0x44
            ]

            self.adc_range = {
                "IIN_ADC"    : [0x2c, 0x2d, 0.001875, 6],
                "VIN_ADC"    : [0x2e, 0x2f, 0.00625,  5],
                "WPC_IN_ADC" : [0x30, 0x31, 0.00625,  5],
                "VEXT_ADC"   : [0x32, 0x33, 0.00625,  5],
                "VOUT_ADC"   : [0x34, 0x35, 0.00125,  5],
                "VBAT_ADC"   : [0x36, 0x37, 0.00125,  5],
                "C1P_ADC"    : [0x3a, 0x3b, 0.00625,  5],
                "TDIE_ADC"   : [0x3e, 0x3f, 0.5,      2]
            }

        elif "sc8563" in self.device:

            self.addr_range = [
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12,
            0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 
            0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a
            ]

            self.adc_range = {
                "IIN_ADC"   : [0x2b, 0x2c, 0.001875, 6],
                "VIN_ADC"   : [0x2d, 0x2e, 0.005,    3],
                "VEXT1_ADC" : [0x2f, 0x30, 0.005,    3],
                "VEXT2_ADC" : [0x31, 0x32, 0.005,    3],
                "VOUT_ADC"  : [0x33, 0x34, 0.00125,  5],
                "VBAT_ADC"  : [0x35, 0x36, 0.00125,  5],
                "C1P_ADC"   : [0x39, 0x3a, 0.005,    3],
                "TDIE_ADC"  : [0x37, 0x38, 0.5,      2]
            }

        else:
            raise Exception("device number is not applicable")


    def print_logo(self):

        print(f",---.                   ,--.  ,--.           ,--.     ,--.                      ,--.                       ,---.                  ,--.                                 ")
        print(f"'   .-'  ,---. ,--.,--.,-'  '-.|  ,---.  ,---.|  ,---. `--' ,---.     ,-----.    |  |    ,---.  ,---.      /  O  \ ,--,--,  ,--,--.|  |,--. ,--.,-----. ,---. ,--.--.  ")
        print(f"`.  `-. | .-. ||  ||  |'-.  .-'|  .-.  || .--'|  .-.  |,--.| .-. |    '-----'    |  |   | .-. || .-. |    |  .-.  ||      \' ,-.  ||  | \  '  / `-.  / | .-. :|  .--'  ")
        print(f".-'    |' '-' ''  ''  '  |  |  |  | |  |\ `--.|  | |  ||  || '-' '               |  '--.' '-' '' '-' '    |  | |  ||  ||  |\ '-'  ||  |  \   '   /  `-.\   --.|  |     ")
        print(f"`-----'  `---'  `----'   `--'  `--' `--' `---'`--' `--'`--'|  |-'                `-----' `---' .`-  /     `--' `--'`--''--' `--`--'`--'.-'  /   `-----' `----'`--'     ")
        print(f"                                                        `--'                                `---'                                   `---'                          JY™ ")


    def start_parsing(self, dump:str, device:str, revision:str, vendor_keyword:bool) -> None:

        # dump : file name
        # step 1. keyword decision
        # step 2. parsing filename desicion
        # step 3. open dump
        # step 4. compare with keyword
        # step 5. store the line when any keyword is in the line

        self.print_logo()
        self.init_parameter(source_file=dump, device=device, revision=revision, vendor_keyword=vendor_keyword)
        self.step_1_matching()

        file_path, file_name = os.path.split(self.source_file)
        parsing_file = os.path.join(file_path, "process done")

        # clear the parameters before exit the method
        self.txt_lines   = None
        self.source_file = None
        self.device      = None
        self.revision    = None
        self.keyword     = None
        self.regmap      = None
        self.regpage     = None
        self.addr_range  = None

        print(f"[100.00%][{log.time_stamp(display=False, ret=True)}] finish dump and adc parsing, clear the parameters")
        
        with open(parsing_file, "a") as parsing:
            parsing.write(f" ")
    

    def progress(self, line_num):

        percentage = line_num / (self.txt_lines+1) * 100
        print(f'\r[{percentage:6.02f}%] ', end='', flush=True) # \r returns to the beginning of the line
    

    def print_store_comment(self, text:str, filename:str, current_line) -> None:
        
        try:
            self.progress(line_num=current_line)
            rstrip_text = text.rstrip()  # remove all trailing whitespace
            print(rstrip_text)
            
            with open(filename, "a") as parsing:
                parsing.write(text)

                if text.endswith('\n'):
                    pass
                else:
                    parsing.write("\n")

        except:
            pass


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
        self.parsing_comment = os.path.join(file_path, f"{stamp} - {name}_comments.txt")

        self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] start dump parsing    -> save to {parsing_file}", self.parsing_comment, 0)
        self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] start adc log         -> save to {adc_file}", self.parsing_comment, 0)
        self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] start parsing comment -> save to {self.parsing_comment}", self.parsing_comment, 0)
        # print(f"[{log.time_stamp(display=False, ret=True)}] start dump parsing -> save to {parsing_file}")
        # print(f"[{log.time_stamp(display=False, ret=True)}] start adc log      -> save to {adc_file}")

        count_sc_rel = 0 # driver version

        with open(self.source_file, "rb") as dump: # binary mode

            # for line in dump:
            for line_num, line in enumerate(dump, start=1):
                
                decoded_line = line.decode("utf-8", errors="ignore")

                # if "SC_REL" in decoded_line:
                if re.search(r"SC_REL", decoded_line, re.IGNORECASE):

                    driver_version = r"SC_REL\((.*?)\)"
                    is_sc_rel = re.search(driver_version, decoded_line)

                    if is_sc_rel:
                        sc_rel = is_sc_rel.group(1)
                        count_sc_rel += 1
                    if count_sc_rel == 1:
                        self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] SC_REL : {sc_rel}", self.parsing_comment, line_num)
                        # print(f"[{log.time_stamp(display=False, ret=True)}] SC_REL : {sc_rel}")
                
                # print out the line while proceed log parsing
                # -----------------------------------------------------------------------------------------------
                if re.search(r"LAST KMSG", decoded_line, re.IGNORECASE):

                    print_line = re.sub(r"\n", "", decoded_line)
                    self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] LAST KMSG : {decoded_line}", self.parsing_comment, line_num)
                
                kernel_version = [r"fsck.f2fs", r"Bootloader", r"Linux version", r"androidboot.bootloader"]

                for kernel_keyword in kernel_version:
                    if re.search(kernel_keyword, decoded_line, re.IGNORECASE):
                        print_line = re.sub(r"\n", "", decoded_line)
                        if "android" in decoded_line and " from " not in decoded_line and " to " not in decoded_line:
                            self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] bootloader version : {decoded_line}", self.parsing_comment, line_num)
                        elif "bootloader" in decoded_line or "name" in decoded_line:
                            self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] Kernel version : {decoded_line}", self.parsing_comment, line_num)

                re_text = f"{self.device}-charger"
                if re.search(re_text, decoded_line, re.IGNORECASE):
                    flag_contain = "trigger" in decoded_line and "flag" in decoded_line
                    flag_exclude = all(
                        phrase not in decoded_line
                        for phrase in [
                            "vout th", "insert", "present", "drv", "remove", "adc", "th rev", "th chg", "qb on"]) # excluded keywords
                    if flag_contain and flag_exclude:
                        print_line = re.sub(r"\n", "", decoded_line)
                        self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] warning flag -- {print_line}", self.parsing_comment, line_num)
                
                print_keyword = [r"sec_bat_show_attrs: batt_current_ua_now"]
                for scan_keyword in print_keyword:
                    if re.search(scan_keyword, decoded_line, re.IGNORECASE):
                        print_line = re.sub(r"\n", "", decoded_line)
                        self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] IOUT current read : {decoded_line}", self.parsing_comment, line_num)
                # -----------------------------------------------------------------------------------------------

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

                        if ret_reglog is not None:  # list type register value return
                            for value in ret_reglog:
                                reg_log += (value+"\n")
                                
                            if reg_log != None:
                                with open(parsing_file, "a") as parsing:
                                    short_header = decoded_line.split("[0x00]")[0]
                                    parsing.write(short_header)
                                    parsing.write("\n")
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
                                parsing.write("\n\n")
                    
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
                            "usb_typec_handle_id_power_status: "     : "usb_typec_handle_id_power_status",
                            "sb_set_dc_ta_op_max_mode: "             : "sb_set_dc_ta_op_max_mode",
                            "sc_charger_set_new_iin: "               : "set_new_iin",
                            "sc_charger_set_new_voltage_and_current" : "set_new_voltage_and_current",
                            "mfc_set_pps_vout"                       : "mfc_set_pps_vout (wpc pps request)",
                            "sc_charger_request_power"               : "pps request",
                            "sc_charger_prob"                        : "load the charger driver",
                            "dc Start fail"                          : "retry fail",
                            "vbus/vout"                              : "initial vbus/vout ratio",
                            "detach"                                 : "detach log in the line",
                            "health_status"                          : "health_status",
                            "POWER_SUPPLY_EXT_PROP_DC_ERROR_CAUSE"   : "POWER_SUPPLY_EXT_PROP_DC_ERROR_CAUSE",
                            "dcic_err_code"                          : "DCIC error code",
                            "ps rdy is 0"                            : "PD Error : PS_RDY=0",
                            "retry charging start"                   : "retry charging",
                            "Maximum retries reached"                : "reached to max retries"
                        }
                        
                        to_dump_text = None

                        for scan_item, log_text in scan_list.items():
                            if scan_item.lower() in decoded_line.lower():
                                
                                if scan_item == "mfc_set_pps_vout":
                                    pps_match = re.search(r'\((\d+)mv,', decoded_line)
                                    pps = int(pps_match.group(1)) if pps_match else None
                                    rx_out_match = re.search(r'=\s*(\d+)\s*mV', decoded_line)
                                    rx_out = int(rx_out_match.group(1)) if rx_out_match else None

                                    if pps != None and rx_out != None:
                                        diff = (pps-rx_out) / 1000 # mV to V scale
                                        suffix = f"diff={diff:.03f}"
                                        cleaned_decoded_line = decoded_line.strip("\n")

                                        to_dump_text = f"        // {suffix} : {log_text} // {decoded_line}"
                                        for_excel    = f"        // {cleaned_decoded_line} -- wpc pps request, {pps/1000}, {rx_out/1000}, {diff}\n"

                                elif scan_item == "detach":
                                    suffix = "detach keyword"
                                    for_excel = None
                                    to_dump_text = f"        // {suffix} : {log_text} // {decoded_line}"
                                
                                elif scan_item == "sc_charger_request_power":
                                    if "pps_vol" in decoded_line and "vbus_adc" in decoded_line:
                                        for_excel = None

                                        pps_vol_match = re.search(r'pps_vol=(\d+)', decoded_line)
                                        if pps_vol_match:
                                            pps_vol = float(pps_vol_match.group(1))/1000 # mV scale

                                        vbus_adc_match = re.search(r'vbus_adc=(\d+)', decoded_line)
                                        if vbus_adc_match:
                                            vbus_adc = float(vbus_adc_match.group(1))/1000_000 # uV scale
                                        
                                        try:
                                            diff_pps_vbus = pps_vol - vbus_adc
                                            to_dump_text = f"        // pps request : pps_vol({pps_vol:.03f}V) - vbus_adc({vbus_adc:.06f}V) = {diff_pps_vbus:.06f}V\n"
                                        except:
                                            pass
                                
                                elif scan_item == "dcic_err_code":
                                    if "sc_charger_get_property" in decoded_line and "cp_err_code" in decoded_line:
                                        dcic_code_match = re.search(r'dcic_err_code=((?:0x)?[0-9a-fA-F]+)', decoded_line) # hex or dec
                                        if dcic_code_match:
                                            dcic_code = int(dcic_code_match.group(1), 16)
                                        cp_code_match = re.search(r'cp_err_code=((?:0x)?[0-9a-fA-F]+)', decoded_line) # hex or dec
                                        if cp_code_match:
                                            cp_code = int(cp_code_match.group(1), 16)
                                        vbat_code_match = re.search(r'vbat_err_code=((?:0x)?[0-9a-fA-F]+)', decoded_line) # hex or dec
                                        if vbat_code_match:
                                            vbat_code = int(vbat_code_match.group(1), 16)
                                        pd_code_match = re.search(r'pd_comm_err_code=((?:0x)?[0-9a-fA-F]+)', decoded_line) # hex or dec
                                        if pd_code_match:
                                            pd_code = int(pd_code_match.group(1), 16)
                                        wpc_code_match = re.search(r'wpc_err_code=((?:0x)?[0-9a-fA-F]+)', decoded_line) # hex or dec
                                        if wpc_code_match:
                                            wpc_code = int(wpc_code_match.group(1), 16)
                                        error = "Not matched"
                                        to_dump_text = f"        // POWER_SUPPLY_EXT_PROP_DC_ERROR_CAUSE : dcic {self.error_code.get(dcic_code, error)}, cp {self.error_code.get(cp_code, error)}, vbat {self.error_code.get(vbat_code, error)}, pd {self.error_code.get(pd_code, error)}, wpc {self.error_code.get(wpc_code, error)}"
                                        self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] POWER_SUPPLY_EXT_PROP_DC_ERROR_CAUSE : dcic {self.error_code.get(dcic_code, error)}, cp {self.error_code.get(cp_code, error)}, vbat {self.error_code.get(vbat_code, error)}, pd {self.error_code.get(pd_code, error)}, wpc {self.error_code.get(wpc_code, error)}", self.parsing_comment, line_num)
                                        for_excel = None
                                
                                elif scan_item == "retry charging start" or scan_item == "Maximum retries reached":
                                    suffix = "retry keyword"

                                    retry_match = re.search(r'sc_charger_check_active_state:\s*(.*)', decoded_line)
                                    if retry_match:
                                        retry_result = retry_match.group(1)
                                    for_excel = None
                                    to_dump_text = f"        // {suffix} : {retry_result}"
                                    self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] {suffix} : {retry_result}", self.parsing_comment, line_num)

                                else:
                                    to_dump_text = f"        // {log_text} : {decoded_line}"
                                    for_excel = None
                                
                                try:
                                    with open(parsing_file, "a") as parsing:
                                        parsing.write(to_dump_text)
                                        if for_excel != None:
                                            parsing.write(for_excel)
                                        parsing.write("\n")
                                except:
                                    pass
                    
                    if "ret" in decoded_line:
                        pattern = r'ret\s*=\s*([+-]?\d+)' # pattern matches "ret=" with any whitespace
                        match_int_list = [int(num) for num in re.findall(pattern, decoded_line)] # matched integer list
                        for_excel = None

                        if len(match_int_list) != 0:
                            if any(x != 0 for x in match_int_list):
                                to_dump_text = f"        // Return error : {str(match_int_list)}"
                                self.print_store_comment(f"[{log.time_stamp(display=False, ret=True)}] Return error : {str(match_int_list)}", self.parsing_comment, line_num)

                                try:
                                    with open(parsing_file, "a") as parsing:
                                        parsing.write(to_dump_text)
                                        if for_excel != None:
                                            parsing.write(for_excel)
                                        parsing.write("\n")
                                except:
                                    pass


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
            splited_data = splited_data.rstrip(", ").rstrip(", ").rstrip("\n")
            # if splited_data.endswith(",\n"):
            #     splited_data = splited_data[:-2]
            pairs = splited_data.split(", ")

            datas = {} # key=register (int), value=value (int)
            ret = list()

            for pair in pairs:
                try:
                    clean_pair = pair.replace("[", "").replace("]", ",").replace(" ", "")
                    addr, value = clean_pair.split(",")
                    address = int(addr, 16)
                    reg_value = int(value, 16)
                    datas[address] = reg_value
                    # print(addr, type(addr), value, type(value))
                except:
                    # print(f"conversion fail : {addr}={value}")
                    pass
            
            adc_ret = dict()

            for adc_name, adc_reg in self.adc_range.items():
                adc_ret[adc_name] = [0, 0]
                
                for dump_addr, dump_value in datas.items():

                    for n in [0, 1]:
                        if dump_addr == adc_reg[n]:
                            if n == 0:
                                adc_ret[adc_name][n] = dump_value << 8
                            else:
                                adc_ret[adc_name][n] = dump_value

            for key_channel, value_adc in adc_ret.items():
                for adc_name, adc_reg in self.adc_range.items():
                    lsb = adc_reg[2]
                    decimal_pooint = adc_reg[3]

                    if key_channel == adc_name:
                        adc = lsb * (value_adc[0] + value_adc[1])
                        adc_final = round(adc, decimal_pooint+1)
                ret.append(f"        // {key_channel} : {adc_final}")

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
            
            '''
            adc_ret = dict()

            for adc_name, adc_reg in self.adc_range.items():
                adc_ret[adc_name] = [0, 0]
                
                for dump_addr, dump_value in datas.items():

                    for n in [0, 1]:
                        if dump_addr == adc_reg[n]:
                            if n == 0:
                                adc_ret[adc_name][n] = dump_value << 8
                            else:
                                adc_ret[adc_name][n] = dump_value

            for key_channel, value_adc in adc_ret.items():
                for adc_name, adc_reg in self.adc_range.items():
                    lsb = adc_reg[2]
                    decimal_pooint = adc_reg[3]

                    if key_channel == adc_name:
                        adc = lsb * (value_adc[0] + value_adc[1])
                        adc_final = round(adc, decimal_pooint+1)
                ret.append(f"        // {key_channel} : {adc_final}")
            '''

            return ret
        
        except:
            print(f"[{log.time_stamp(display=False, ret=True)}] wrong format - {dump_code} {data}")
            # print(f"[{log.time_stamp(display=False, ret=True)}] wrong format - {dump_code} {data}")
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
                    ret = f"        // reached to target power, sync rx vout to pps ta_vol, {res}\n"
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
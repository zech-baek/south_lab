from interface.cui_logger import logger as log
from interface.cui_colors import color
from project.get_device_info import get_map, get_regpage

import os, re, mmap, yaml


class parsing:

    def __init__(self, logging):

        self.__slots__ = ("txt_lines", "source_file", "device", "revision", "keyword",
                "regmap", "regpage", "addr_range", "file_path", "file_name",
                "trg_kmsg", "parsing_file", "adc_file")
        # pps_request : 3 items
        # sc_charger_check_dcmode_status : 14 items
        # others : from adc
        self.__adc__   = ["time", "pps_v", "pps_i", "vbus", "iin target", "iin", "iin diff", "vbat target", "vbat ifpm", "vbat diff", "vbat dcic", "vbat adc diff", "power", "vbus", "vwpc"]

        self.logging = logging
    

    def count_lines(self, filename: str) -> int:

        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    

    def init_parameter(self, source_file:str, device:str, revision:str, vendor_keyword:bool) -> None:
        
        self.txt_lines   = self.count_lines(source_file)
        self.source_file = source_file
        self.device      = device
        self.revision    = revision
        self.trg_kmsg    = False

        self.file_path, self.file_name = os.path.split(self.source_file)
        self.keyword = self.merged_keyword if vendor_keyword else self.basic_keyword
        self.regmap  = get_map(device=self.device, revision=self.revision)
        self.regpage = get_regpage(device=self.device, revision=self.revision)

        if "sc8583" in self.device:
            self.addr_range = self.global_keyword["sc8583_addr_range"]
            self.adc_range  = self.global_keyword["sc8583_adc_range"]

        elif "sc8563" in self.device:
            self.addr_range = self.global_keyword["sc8563_addr_range"]
            self.adc_range  = self.global_keyword["sc8563_adc_range"]

        else:
            raise Exception("device number is not applicable")


    def clear_parameter(self) -> None:

        for attr in self.__slots__:
            setattr(self, attr, None)
        self.trg_kmsg = False 

    def print_logo(self):

        print(f",---.                   ,--.  ,--.           ,--.     ,--.                      ,--.                       ,---.                  ,--.                                 ")
        print(f"'   .-'  ,---. ,--.,--.,-'  '-.|  ,---.  ,---.|  ,---. `--' ,---.     ,-----.    |  |    ,---.  ,---.      /  O  \ ,--,--,  ,--,--.|  |,--. ,--.,-----. ,---. ,--.--.  ")
        print(f"`.  `-. | .-. ||  ||  |'-.  .-'|  .-.  || .--'|  .-.  |,--.| .-. |    '-----'    |  |   | .-. || .-. |    |  .-.  ||      \' ,-.  ||  | \  '  / `-.  / | .-. :|  .--'  ")
        print(f".-'    |' '-' ''  ''  '  |  |  |  | |  |\ `--.|  | |  ||  || '-' '               |  '--.' '-' '' '-' '    |  | |  ||  ||  |\ '-'  ||  |  \   '   /  `-.\   --.|  |     ")
        print(f"`-----'  `---'  `----'   `--'  `--' `--' `---'`--' `--'`--'|  |-'                `-----' `---' .`-  /     `--' `--'`--''--' `--`--'`--'.-'  /   `-----' `----'`--'     ")
        print(f"                                                           `--'                                `---'                                   `---'                       JY™ ")


    def start_parsing(self, dump:str, keyword:str, device:str, revision:str, vendor_keyword:bool) -> None:
        
        with open(keyword) as keyword_file:
            self.global_keyword = yaml.safe_load(keyword_file)

        self.basic_keyword  = self.global_keyword["basic_keyword"]
        self.vendor_keyword = self.global_keyword["vendor_keyword"]
        self.error_code     = self.global_keyword["error_code"]
        self.merged_keyword = self.basic_keyword + self.vendor_keyword

        self.print_logo()
        self.init_parameter(source_file=dump, device=device, revision=revision, vendor_keyword=vendor_keyword)
        self.matching_start()

        process_done = os.path.join(self.file_path, f"process done - {self.file_name}")
        print(f"[100.00%] finish dump and adc parsing, clear the parameters")
        with open(process_done, "a") as parsing:
            parsing.write(f" ")

        self.clear_parameter() # clear the parameters before exit the method
    

    def progress(self, line_num):

        percentage = line_num / (self.txt_lines+1) * 100
        print(f'\r[{percentage:6.01f}%] ', end='', flush=True) # \r returns to the beginning of the line
    

    def print_comment(self, text:str, current_line) -> None:
        
        try:
            self.progress(line_num=current_line)
            rstrip_text = text.rstrip()  # remove all trailing whitespace
            print(rstrip_text)
            
        except:
            pass
    

    def file_write(self, handler, message):

        if self.trg_kmsg:
            message = "(LAST KMSG)  " + message
        handler.write(message+"\n")


    def get_timestamp(self, content) -> str:

        match = re.search(r'\[\s*(\d+\.\d+)\]', content)
        if match:
            return match.group(1)
        
        match = re.search(r'(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})', content)
        if match:
            return match.group(1)
        
        return ""


    def matching_start(self) -> None:

        name, ext = os.path.splitext(self.file_name)
        stamp = log.time_stamp(display=False, ret=True)

        self.parsing_file  = os.path.join(self.file_path, f"{stamp} - {name}_parsing.txt")
        self.adc_file = os.path.join(self.file_path, f"{stamp} - {name}_parsing_adc.csv")
        self.print_comment(f"start dump parsing    -> save to {self.parsing_file}", 0)
        self.print_comment(f"start adc log         -> save to {self.adc_file}", 0)

        log.output_set_filename(title=self.adc_file)
        log.output_csv(message=(self.__adc__+sorted(self.adc_range))) # append sorted adc list at the end of __adc__
        
        count_sc_rel = 0 # driver version
        dump_code = self.device + "_dump_registers "

        with open(self.source_file, "rb") as dump: # binary mode
            for line_num, line in enumerate(dump, start=1):
                
                # -------------------------------------------------------------------------------------------------
                decoded_line = re.sub(r"\n", "", line.decode("utf-8", errors="ignore")).rstrip() # remove line feed
                # -------------------------------------------------------------------------------------------------
                
                if re.search(r"SC_REL", decoded_line, re.IGNORECASE):
                    driver_version = r"SC_REL\((.*?)\)"
                    is_sc_rel = re.search(driver_version, decoded_line)

                    if is_sc_rel:
                        sc_rel = is_sc_rel.group(1)
                        count_sc_rel += 1
                        
                    if count_sc_rel == 1:
                        self.print_comment(color.red+f"SC_REL : {sc_rel}"+color.end, 0)

                        with open(self.parsing_file, "a") as parsing:
                            self.file_write(handler=parsing, message=decoded_line)
                            self.file_write(handler=parsing, message=f"        // SC_REL : {sc_rel}\n")
                
                # -----------------------------------------------------------------------------------------------
                # print out prefix while proceed log parsing
                # -----------------------------------------------------------------------------------------------
                if re.search(r"LAST KMSG", decoded_line, re.IGNORECASE):
                    self.print_comment(color.cyan+f"LAST KMSG : {decoded_line}"+color.end, line_num)
                    self.trg_kmsg = True
                
                kernel_version = [r"fsck.f2fs", r"Bootloader", r"Linux version", r"androidboot.bootloader"]

                for kernel_keyword in kernel_version:
                    if re.search(kernel_keyword, decoded_line, re.IGNORECASE):
                        if "android" in decoded_line and " from " not in decoded_line and " to " not in decoded_line:
                            self.print_comment(f"bootloader version : {decoded_line}", line_num)
                        elif "bootloader" in decoded_line or "name" in decoded_line:
                            self.print_comment(f"kernel version : {decoded_line}", line_num)
                
                re_text = f"{self.device}-charger"
                if re.search(re_text, decoded_line, re.IGNORECASE):
                    excluded_flag = self.global_keyword["excluded_flag"]
                    flag_contain = "trigger" in decoded_line and "flag" in decoded_line
                    flag_exclude = all(
                        phrase not in decoded_line
                        for phrase in excluded_flag)
                    if flag_contain and flag_exclude:
                        self.print_comment(color.red+f"warning flag -- {decoded_line}"+color.end, line_num)
                
                print_keyword = [r"sec_bat_show_attrs: batt_current_ua_now"]
                for scan_keyword in print_keyword:
                    if re.search(scan_keyword, decoded_line, re.IGNORECASE):
                        self.print_comment(color.green+f"IOUT read by AT Command : {decoded_line}"+color.end, line_num)
                        with open(self.parsing_file, "a") as parsing:
                            self.file_write(handler=parsing, message=decoded_line)
                            self.file_write(handler=parsing, message=f"        // IOUT read by AT Command : {decoded_line}\n")
                # -----------------------------------------------------------------------------------------------

                if any(keyword in decoded_line for keyword in self.keyword):

                    try:
                        if "adc done flag" in decoded_line:
                            pass
                        else:
                            with open(self.parsing_file, "a") as parsing:
                                self.file_write(handler=parsing, message=decoded_line) # store the matched line first, then find suffix at matching function
                    except:
                        pass
                    
                    if dump_code in decoded_line:

                        ret_reglog = self.reg_matching(dump_code=dump_code, data=decoded_line)
                        reg_log = ""

                        if ret_reglog is not None:  # list type register value return
                            for value in ret_reglog:
                                reg_log += (value+"\n")
                                
                            with open(self.parsing_file, "a") as parsing:
                                short_header = decoded_line.split("[0x00]")[0]
                                self.file_write(handler=parsing, message=short_header)
                                self.file_write(handler=parsing, message=reg_log)
                    
                    elif "sc_charger_set_property" in decoded_line:
                        if "POWER_SUPPLY_EXT_PROP_PWR_CTRL_UPDATE" in decoded_line:
                            with open(self.parsing_file, "a") as parsing:
                                self.file_write(handler=parsing, message=f"        // reached to target power, sync rx vout to pps ta_vol\n")
                    
                    elif "sc_charger_timer_work" in decoded_line:
                        reg_log = self.process_matching(data=decoded_line)
                        
                        if reg_log != None:
                            with open(self.parsing_file, "a") as parsing:
                                self.file_write(handler=parsing, message=reg_log)
                                self.file_write(handler=parsing, message="\n")
                    
                    elif "sc_charger_check_dcmode_status" in decoded_line:
                        adc_suffix = self.adc_matching(data=decoded_line)

                        if adc_suffix != None:
                            with open(self.parsing_file, "a") as parsing:
                                self.file_write(handler=parsing, message=adc_suffix)
                    
                    elif f"{self.device}_info" in decoded_line.lower():
                        match_iin  = re.search(r'set ibus regulation is\s+(\d+)', decoded_line.lower())
                        match_vbat = re.search(r'set vbat regulation is\s+(\d+)', decoded_line.lower())
                        if match_iin:
                            result_iin = int(match_iin.group(1))
                            with open(self.parsing_file, "a") as parsing:
                                    self.file_write(handler=parsing, message=f"        // iin regulation : {result_iin/1e+6:.04f}A\n")
                        if match_vbat:
                            result_vbat = int(match_vbat.group(1))
                            with open(self.parsing_file, "a") as parsing:
                                    self.file_write(handler=parsing, message=f"        // vbat regulation : {result_vbat/1e+6:.04f}V\n")

                    else:
                        scan_list = self.global_keyword["scan_list"]
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
                                        suffix = f"diff = {diff:.03f}"
                                        to_dump_text = f"        // {suffix} : {log_text}\n        // wpc pps request, {pps/1000}, {rx_out/1000}, {diff}"

                                elif scan_item == "health_status":
                                    suffix = "health status found"
                                    to_dump_text = f"        // {suffix}"
                                
                                elif scan_item == "detach" and "muic" not in decoded_line.lower():
                                    suffix = "detach keyword"
                                    to_dump_text = f"        // {suffix} : {log_text}"
                                
                                elif scan_item == "sc_charger_request_power":
                                    if "pps_vol" in decoded_line and "vbus_adc" in decoded_line:

                                        pps_vol_match = re.search(r'pps_vol=(\d+)', decoded_line)
                                        if pps_vol_match:
                                            pps_vol = float(pps_vol_match.group(1))/1000 # mV scale

                                        vbus_adc_match = re.search(r'vbus_adc=(\d+)', decoded_line)
                                        if vbus_adc_match:
                                            vbus_adc = float(vbus_adc_match.group(1))/1000_000 # uV scale

                                        pps_cur_match = re.search(r'pps_cur=(\d+)', decoded_line)
                                        if pps_cur_match:
                                            pps_cur = float(pps_cur_match.group(1))/1000 # mA scale
                                        
                                        time_stamp = self.get_timestamp(content=decoded_line)

                                        try:
                                            diff_pps_vbus = pps_vol - vbus_adc
                                            to_dump_text = f"        // pps request : pps_vol({pps_vol:.03f}V) - vbus_adc({vbus_adc:.03f}V) = {diff_pps_vbus:.03f}V"
                                            log.output_csv(message=[time_stamp, pps_vol, pps_cur, vbus_adc])
                                        except:
                                            pass
                                
                                elif scan_item == "dcic_err_code":

                                    if "sc_charger_get_property" in decoded_line and "cp_err_code" in decoded_line:
                                        error_codes = {}
                                        patterns = {
                                            "dcic_err_code"    : r'dcic_err_code=((?:0x)?[0-9a-fA-F]+)',
                                            "cp_err_code"      : r'cp_err_code=((?:0x)?[0-9a-fA-F]+)',
                                            "vbat_err_code"    : r'vbat_err_code=((?:0x)?[0-9a-fA-F]+)',
                                            "pd_comm_err_code" : r'pd_comm_err_code=((?:0x)?[0-9a-fA-F]+)',
                                            "wpc_err_code"     : r'wpc_err_code=((?:0x)?[0-9a-fA-F]+)'
                                        }
                                        for code_name, pattern in patterns.items():
                                            match = re.search(pattern, decoded_line)
                                            if match:
                                                error_codes[code_name] = int(match.group(1), 16) if match else None
                                        
                                        error_msg = "Not matched"
                                        err_comment = (f"POWER_SUPPLY_EXT_PROP_DC_ERROR_CAUSE : "
                                                    f"dcic {self.error_code.get(error_codes['dcic_err_code'], error_msg)}, "
                                                    f"cp {self.error_code.get(error_codes['cp_err_code'], error_msg)}, "
                                                    f"vbat {self.error_code.get(error_codes['vbat_err_code'], error_msg)}, "
                                                    f"pd {self.error_code.get(error_codes['pd_comm_err_code'], error_msg)}, "
                                                    f"wpc {self.error_code.get(error_codes['wpc_err_code'], error_msg)}")
                                        
                                        to_dump_text = f"        // {err_comment}"
                                        self.print_comment(color.red+f"{err_comment}"+color.end, line_num)
                                
                                elif scan_item.lower() in {"retry charging start", "maximum retries reached"}:
                                    retry_match = re.search(r'sc_charger_check_active_state:\s*(.*)', decoded_line)
                                    if retry_match:
                                        retry_result = retry_match.group(1)

                                    to_dump_text = f"        // retry keyword : {retry_result}"
                                    self.print_comment(f"retry keyword : {retry_result}", line_num)
                                
                                elif scan_item == "max77775_current_pdo" and any(x.lower() in decoded_line.lower() for x in ("FIXED", "APDO")):
                                    to_dump_text = f"        // {log_text}"
                                
                                elif scan_item == "usbpd-sm5714b" and any(x.lower() in decoded_line.lower() for x in ("FIXED volt", "Augmented min_volt")):
                                    to_dump_text = f"        // {log_text}"

                                else:
                                    to_dump_text = f"        // {log_text}"
                                
                                try:
                                    with open(self.parsing_file, "a") as parsing:
                                        self.file_write(handler=parsing, message=to_dump_text+"\n")
                                        
                                except:
                                    pass
                    
                    if "ret" in decoded_line:

                        pattern = r'ret\s*=\s*([+-]?\d+)' # pattern matches "ret=" with any whitespace
                        match_int_list = [int(num) for num in re.findall(pattern, decoded_line)] # matched integer list

                        if len(match_int_list) != 0:

                            if any(x != 0 for x in match_int_list):
                                return_suffix = f"        // return error : {str(match_int_list)}\n"
                                try:
                                    with open(self.parsing_file, "a") as parsing:
                                        self.file_write(handler=parsing, message=return_suffix)
                                except:
                                    pass


    def reg_matching(self, dump_code, data):

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

            adc_dict = dict()
            for key_channel, value_adc in adc_ret.items():
                for adc_name, adc_reg in self.adc_range.items():
                    lsb = adc_reg[2]
                    decimal_point = adc_reg[3]

                    if key_channel == adc_name:
                        adc = lsb * (value_adc[0] + value_adc[1])
                        adc_final = round(adc, decimal_point+1)
                        adc_dict[key_channel] = adc_final
                ret.append(f"        // {key_channel} : {adc_final}")

            time_stamp = self.get_timestamp(content=data)
            sorted_adc = [adc_dict[k] for k in sorted(adc_dict)]
            adc_log = [time_stamp,
                999, 999, 999, 999, 999,
                999, 999, 999, 999, 999,
                999, 999, 999, 999] + sorted_adc
            log.output_csv(message=adc_log)

            for addr in self.addr_range:                
                temp = [0 for _ in range(8)]

                for dump_addr in datas.keys():

                    if addr == dump_addr:

                        for register, info_list in self.regpage.items():                            

                            if addr in info_list[2]:
                                
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
                        star_suffix = self.global_keyword["star_suffix"]                        
                        suffix = ""
                        
                        for reg_check in star_suffix:
                            if re.search(reg_check, reg_name, re.IGNORECASE):
                                suffix = "        ***"

                        if "8583" in self.device:
                            if reg_name == "VEXT_OVP":
                                remark = f"     --->  11V+{masked_value} = {11+masked_value:.01f}V"
                            elif reg_name == "VBAT_REG":
                                if masked_value <= 0b01010000:
                                    masked_value = 0b01010000
                                elif masked_value >= 0b11100110:
                                    masked_value = 0b11100110
                                remark = f"     --->  3.4V+{0.005*masked_value}V = {3.4+0.005*masked_value:.03f}V"
                            elif reg_name == "VBAT_OVP":
                                if masked_value <= 0b01111000:
                                    masked_value = 0b01111000
                                elif masked_value >= 0b11110000:
                                    masked_value = 0b11110000
                                remark = f"     --->  3.4V+{0.005*masked_value}V = {3.4+0.005*masked_value:.03f}V"
                            elif reg_name == "VOUT_OVP":
                                remark = f"     --->  4.7V+{masked_value*0.2}V = {4.7+masked_value*0.2:.01f}V"
                            elif reg_name == "IIN_REG":
                                if masked_value <= 0b00001010:
                                    masked_value = 0b00001010
                                elif masked_value >= 0b10100000:
                                    masked_value = 0b10101010
                                remark = f"     --->  {0.0375*masked_value:.04f}A"
                            elif reg_name == "IIN_OCP":
                                if masked_value <= 0b00001010:
                                    masked_value = 0b00001010
                                elif masked_value >= 0b10101010:
                                    masked_value = 0b10101010
                                remark = f"     --->  {0.0375*masked_value:.04f}A"
                            else:
                                remark = ""

                        ret.append(f"        // {addr:#04x}[{msb}:{lsb}] {reg_name}={masked_value:#x} {suffix} {remark}")
                        # log.infoLog(f"{addr:#04x}[{msb}:{lsb}] {reg_name}={masked_value:#x} (shift={lsb}, dump value={dump_value:#04x}, masking={masking_b:#04x})")
            
            flag_info = list()
            stat_info = list()
            flag_info.append(" ")
            stat_info.append(" ")

            for index, value in enumerate(ret):
                if "flag" in value.lower() and "=0x1" in value.lower():
                    flag_info.append(value)
                if "stat" in value.lower() and "=0x1" in value.lower():
                    stat_info.append(value)

            return ret + flag_info + stat_info
        
        except:
            print(f" wrong format - {dump_code} {data}")
            return None
    

    def reached_target_power(self, data):

        if "POWER_SUPPLY_EXT_PROP_PWR_CTRL_UPDATE" in data:
            return f"        // reached to target power, sync rx vout to pps ta_vol"
        else:
            return None
        

    def adc_matching(self, data:str) -> str:

        re_scale = 1000_000
        time_stamp = self.get_timestamp(content=data)

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

        if any(item is not None for item in [iin_match, iin_target_match, vbat_match, vbat_target_match, power_match, vbus_match, vwpc_match, vbat_dcic_match]):

            iin_value = int(iin_match.group(1))/re_scale if iin_match else None
            iin_target_value = int(iin_target_match.group(1))/re_scale if iin_target_match else None
            vbat_ifpm_value = int(vbat_match.group(1))/re_scale if vbat_match else None
            vbat_target_value = int(vbat_target_match.group(1))/re_scale if vbat_target_match else None
            power_value = int(power_match.group(1))/re_scale if power_match else None
            vbus_value = int(vbus_match.group(1))/re_scale if vbus_match else None
            vwpc_value = int(vwpc_match.group(1))/re_scale if vwpc_match else None
            vbat_dcic_value = int(vbat_dcic_match.group(1))/re_scale if vbat_dcic_match else None

            vbat_diff = vbat_target_value - vbat_ifpm_value
            vbat_adc_diff = vbat_ifpm_value - vbat_dcic_value
            iin_diff  = iin_target_value - iin_value

            if self.logging:
                print(f"iin_value : {iin_value}")
                print(f"iin_target_value : {iin_target_value}")
                print(f"vbat_ifpm_value : {vbat_ifpm_value}")
                print(f"vbat_target_value : {vbat_target_value}")
                print(f"power_value : {power_value}")
                print(f"vbus_value : {vbus_value}")
                print(f"vwpc_value : {vwpc_value}")
                print(f"vbat_dcic_value : {vbat_dcic_value}")

            try:
                ret = ""
                value_dict = {
                    "iin target"    : [iin_target_value, "A"],
                    "iin"           : [iin_value, "A"],
                    "iin diff"      : [iin_diff, "A"],
                    "vbat target"   : [vbat_target_value, "V"],
                    "vbat ifpm"     : [vbat_ifpm_value, "V"],
                    "vbat diff"     : [vbat_diff, "V"],
                    "vbat dcic"     : [vbat_dcic_value, "V"],
                    "vbat adc diff" : [vbat_adc_diff, "V"],
                    "power"         : [power_value, "W"],
                    "vbus"          : [vbus_value, "V"],
                    "vwpc"          : [vwpc_value, "V"]                
                }

                for item, value in value_dict.items():
                    ret = ret + f"        // {item} : {value[0]:.03f}{value[1]}\n"
                
                csv_list = [time_stamp, 999, 999, 999,
                            iin_target_value, iin_value      , iin_diff     , vbat_target_value, vbat_ifpm_value,
                            vbat_diff,        vbat_dcic_value, vbat_adc_diff, power_value      , vbus_value     ,
                            vwpc_value]
                log.output_csv(message=csv_list)

                return ret
            
            except:
                return None
        
        else:
            return None


    def process_matching(self, data) -> str:

        pattern = r'sc_charger_timer_work:\s*timer id=(\d+),\s*charging_state=(\w+)'
        match = re.search(pattern, data)
        ret = None

        if match:
            timer = int(match.group(1))
            state = match.group(2)  # this is a string, not an integer
            process_no = self.global_keyword["process_no"]

            if timer in process_no.keys():
                ret = process_no[timer]

        elif "health_status".lower() in data.lower():
            suffix = "health status found"
            ret = f"        // {suffix} : {data}"

        return ret
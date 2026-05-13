from interface.cui_logger import logger as log
from interface.cui_colors import color
from project.get_device_info import get_map, get_regpage
from tqdm import tqdm # pip install tqdm

import os, re, mmap, yaml, time
import tkinter as tk
import threading
import queue



log_queue = queue.Queue()
log_color = {
    "blue"   : "#00BFFF",
    "green"  : "#00FF7F",
    "orange" : "#FFA500",
    "red"    : "#F5B1FC",
    "black"  : "#000000"
}

def create_log_window(q):
    
    root = tk.Tk()
    root.title("Log output")
    root.geometry("1200x768")
    root.configure(bg="#B9B9B9")

    text = tk.Text(
        root, wrap="word",
        font=("Consolas", 12),
        bg="#1e1e1e",
        fg="#FFFFFF",
        insertbackground="white"
        )
    
    scrollbar = tk.Scrollbar(root, command=text.yview)
    text.configure(yscrollcommand=scrollbar.set)

    # register the color set
    for level, color in log_color.items():
        text.tag_configure(level, foreground=color)

    scrollbar.pack(side="right", fill="y")
    text.pack(expand=True, fill="both")

    def polling_queue():
        while not q.empty():
            message, level = q.get_nowait()
            text.insert("end", message + "\n", level)
            text.see("end")
        root.after(100, polling_queue)  # check the queue in every 100ms

    polling_queue()
    root.mainloop()



class parsing:

    def __init__(self):

        self.__slots__ = ("txt_lines", "source_file", "device", "revision", "keyword",
                "regmap", "regpage", "addr_range", "file_path", "file_name",
                "trg_kmsg", "parsing_file", "adc_file")
        # pps_request : 3 items
        # sc_charger_check_dcmode_status : 14 items
        # others : from adc
        self.__adc__ = ["time", "pps_v", "pps_i", "vbus", "pps_vbus_diff", "iin target", "iin", "iin diff", "vbat target", "vbat ifpm", "vbat diff", "vbat dcic", "vbat adc diff", "power", "vbus", "vwpc", "r_calc1", "r_calc2", "batt_current_ua_now"]
        self.t = threading.Thread(target=create_log_window, args=(log_queue,), daemon=True)
        self.t.start()
    

    def count_lines(self, filename: str) -> int:

        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    

    def init_parameter(self, source_file:str, device:str, revision:str, vendor_keyword:bool) -> None:
        
        self.txt_lines   = self.count_lines(source_file)
        self.source_file = source_file
        self.device      = device
        self.revision    = revision
        self.trg_kmsg    = False
        self.trg_sc_rel  = 0
        self.store_ppsv  = None
        self.batt_curr   = 999999
        
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
        self.trg_sc_rel = 0
        self.line_flag  = True
        self.store_ppsv  = None
        self.batt_curr = 999999

    def print_logo(self):

        print(f",---.                   ,--.  ,--.           ,--.     ,--.                      ,--.                       ,---.                  ,--.                                 ")
        print(f"'   .-'  ,---. ,--.,--.,-'  '-.|  ,---.  ,---.|  ,---. `--' ,---.     ,-----.    |  |    ,---.  ,---.      /  O  \ ,--,--,  ,--,--.|  |,--. ,--.,-----. ,---. ,--.--.  ")
        print(f"`.  `-. | .-. ||  ||  |'-.  .-'|  .-.  || .--'|  .-.  |,--.| .-. |    '-----'    |  |   | .-. || .-. |    |  .-.  ||      \' ,-.  ||  | \  '  / `-.  / | .-. :|  .--'  ")
        print(f".-'    |' '-' ''  ''  '  |  |  |  | |  |\ `--.|  | |  ||  || '-' '               |  '--.' '-' '' '-' '    |  | |  ||  ||  |\ '-'  ||  |  \   '   /  `-.\   --.|  |     ")
        print(f"`-----'  `---'  `----'   `--'  `--' `--' `---'`--' `--'`--'|  |-'                `-----' `---' .`-  /     `--' `--'`--''--' `--`--'`--'.-'  /   `-----' `----'`--'     ")
        print(f"                                                           `--'                                `---'                                   `---'                       JY™ \n\n")


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

        '''
        process_done = os.path.join(self.file_path, f"process done - {self.file_name}")
        print(f"[100.00%] finish dump and adc parsing, clear the parameters")
        with open(process_done, "a") as parsing:
            parsing.write(f" ")
        '''

        self.clear_parameter() # clear the parameters before exit the method
    

    def progress(self, line_num):

        percentage = line_num / (self.txt_lines+1) * 100
        print(f'\r[{percentage:6.01f}%] ', end='', flush=True) # \r returns to the beginning of the line
    

    def print_comment(self, text:str, current_line:int, level="blue") -> None:
        
        try:
            # self.progress(line_num=current_line)
            rstrip_text = text.rstrip()  # remove all trailing whitespace
            log_queue.put((f"[{current_line/(self.txt_lines+1)*100:6.01f}%] {rstrip_text}", level))
            # print(rstrip_text)
            
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
        self.print_comment(f"start dump parsing    -> save to {self.parsing_file}", 0, "blue")
        self.print_comment(f"start adc log         -> save to {self.adc_file}", 0, "blue")

        log.output_set_filename(title=self.adc_file)
        log.output_csv(message=(self.__adc__+sorted(self.adc_range))) # append sorted adc list at the end of __adc__
        
        self.trg_sc_rel = 0 # driver version
        dump_code = self.device + "_dump_registers "

        with tqdm(total=100, desc="Parsing progress ", unit="%") as pbar:

            with open(self.source_file, "rb") as dump: # binary mode
                for line_num, line in enumerate(dump, start=1):
                    
                    line_percentage = int(line_num / (self.txt_lines+1) * 100) + 1
                    if line_percentage in list(i for i in range(0, 101, 5)):
                        pbar.n = line_percentage
                        pbar.refresh()
                        
                    # -------------------------------------------------------------------------------------------------
                    decoded_line = re.sub(r"\n", "", line.decode("utf-8", errors="ignore")).rstrip() # remove line feed
                    # -------------------------------------------------------------------------------------------------
                    
                    if re.search(r"SC_REL", decoded_line, re.IGNORECASE):
                        driver_version = r"SC_REL\((.*?)\)"
                        self.trg_sc_rel += 1
                        
                        try:
                            is_sc_rel = re.search(driver_version, decoded_line)
                            sc_rel = is_sc_rel.group(1)

                            if self.trg_sc_rel == 1:
                                self.print_comment(f"SC_REL : {sc_rel}", line_num, "blue")
                                with open(self.parsing_file, "a") as parsing:
                                    self.file_write(handler=parsing, message=decoded_line)
                                    self.file_write(handler=parsing, message=f"        // SC_REL : {sc_rel}\n")
                        except:
                            pass
                    
                    # -----------------------------------------------------------------------------------------------
                    # print out prefix while proceed log parsing
                    # -----------------------------------------------------------------------------------------------
                    if re.search(r"LAST KMSG", decoded_line, re.IGNORECASE):
                        self.print_comment(f"LAST KMSG : {decoded_line}", line_num, "orange")
                        self.trg_kmsg = True
                    
                    kernel_version = [r"kernel version", r"bootloader version"]

                    '''
                    for kernel_keyword in kernel_version:
                        if re.search(kernel_keyword, decoded_line, re.IGNORECASE):
                            if "android" in decoded_line and " from " not in decoded_line and " to " not in decoded_line:
                                self.print_comment(f"bootloader version : {decoded_line}", line_num)
                            elif "bootloader" in decoded_line or "name" in decoded_line:
                                self.print_comment(f"kernel version : {decoded_line}", line_num)
                    '''

                    for kernel_keyword in kernel_version:
                        if re.search(kernel_keyword, decoded_line, re.IGNORECASE):
                            if "android" in decoded_line or "bootloader" in decoded_line:
                                self.print_comment(f"bootloader version : {decoded_line}", line_num, "blue")
                    
                    re_text = f"{self.device}-charger"
                    if re.search(re_text, decoded_line, re.IGNORECASE):
                        excluded_flag = self.global_keyword["excluded_flag"]
                        flag_contain = "trigger" in decoded_line and "flag" in decoded_line
                        flag_exclude = all(
                            phrase not in decoded_line
                            for phrase in excluded_flag)
                        if flag_contain and flag_exclude:
                            self.print_comment(f"warning flag -- {decoded_line}", line_num, "red")
                    
                    print_keyword = [r"sec_bat_show_attrs: batt_current_ua_now"]
                    for scan_keyword in print_keyword:
                        if re.search(scan_keyword, decoded_line, re.IGNORECASE):
                            self.print_comment(f"IOUT read by AT Command : {decoded_line}", line_num, "green")
                            with open(self.parsing_file, "a") as parsing:
                                self.file_write(handler=parsing, message=decoded_line)
                                self.file_write(handler=parsing, message=f"        // IOUT read by AT Command : {decoded_line}\n")
                            
                            match = re.search(r'\((\d+)\)', decoded_line)
                            if match:
                                self.batt_curr = int(match.group(1))/1e+6
                            else:
                                self.batt_curr = 999999

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
                                    self.file_write(handler=parsing, message="\n")
                                    self.file_write(handler=parsing, message=short_header)
                                    self.file_write(handler=parsing, message=reg_log)
                        
                        elif "sc_charger_set_property" in decoded_line:
                            if "POWER_SUPPLY_EXT_PROP_PWR_CTRL_UPDATE" in decoded_line:
                                with open(self.parsing_file, "a") as parsing:
                                    self.file_write(handler=parsing, message=f"        // reached to target power, sync rx vout to pps ta_vol\n")
                        
                        elif "sc_charger_timer_work" in decoded_line:

                            if "timer id" in decoded_line.lower():
                                reg_log = self.process_matching(data=decoded_line)
                                
                                if reg_log != None:
                                    with open(self.parsing_file, "a") as parsing:
                                        self.file_write(handler=parsing, message=reg_log)
                                        # self.file_write(handler=parsing, message="\n")
                            else:
                                configured_iin = re.search(r'iin_cc=\s*(\d+)', decoded_line.lower())
                                requested_iin  = re.search(r'iin_cfg=\s*(\d+)', decoded_line.lower())

                                if configured_iin:
                                    result_conf_iin = int(configured_iin.group(1))
                                else:
                                    result_conf_iin = None

                                if requested_iin:
                                    result_req_iin = int(requested_iin.group(1))
                                else:
                                    result_req_iin = None
                                    
                                if result_conf_iin != None and result_req_iin != None:
                                    with open(self.parsing_file, "a") as parsing:
                                        self.file_write(handler=parsing, message=f"        // requested iin={result_req_iin} --> configured iin={result_conf_iin}\n")
                        
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
                        
                        elif "sm5714" in decoded_line.lower():
                            # vbus_match = re.search(r'vbus_voltage=(\d+)', decoded_line) or re.search(r'vbus_voltage:(\d+)', decoded_line)
                            vbus_match = re.search(r'vbus_voltage=(\d+)', decoded_line)
                            if vbus_match:
                                ifpmic_vbus = int(vbus_match.group(1))
                                with open(self.parsing_file, "a") as parsing:
                                    if "mv" in decoded_line.lower():
                                        self.file_write(handler=parsing, message=f"        // found vbus voltage adc from ifpmic : {ifpmic_vbus/1000}V\n")
                                    else:
                                        self.file_write(handler=parsing, message=f"        // found vbus voltage adc from ifpmic : {ifpmic_vbus}V\n")

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
                                                self.store_ppsv = pps_vol
                                                to_dump_text = f"        // pps request : pps_vol({pps_vol:.03f}V) - vbus_adc({vbus_adc:.03f}V) = {diff_pps_vbus:.03f}V"
                                                log.output_csv(message=[time_stamp, pps_vol, pps_cur, vbus_adc, diff_pps_vbus])
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
                                            self.print_comment(f"{err_comment}", line_num, "red")
                                    
                                    elif scan_item.lower() in {"retry charging start", "maximum retries reached"}:
                                        retry_match = re.search(r'sc_charger_check_active_state:\s*(.*)', decoded_line)
                                        if retry_match:
                                            retry_result = retry_match.group(1)

                                        to_dump_text = f"        // retry keyword : {retry_result}"
                                        self.print_comment(f"retry keyword : {retry_result}", line_num, "red")
                                    
                                    elif scan_item == "max77775_current_pdo" or scan_item == "usbpd-sm5714b" or scan_item == "usbpd-pdic_max77775":

                                        if any(x.lower() in decoded_line.lower() for x in ("FIXED", "APDO", "Augmented min_volt")):
                                            to_dump_text = f"        // FPDO {log_text}"
                                        elif any(x.lower() in decoded_line.lower() for x in ("APDO", "Augmented min_volt")):
                                            to_dump_text = f"        // APDO {log_text}"
                                    
                                    # elif "vbus_handle_notification".lower() in scan_item:
                                    #     to_dump_text = f"        // vbus_handle_notification"
                                    #     self.print_comment(color.yellow+f"{decoded_line}"+color.end, line_num)

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
            adc_info = list()

            for key_channel, value_adc in adc_ret.items():
                for adc_name, adc_reg in sorted(self.adc_range.items()):
                    lsb = adc_reg[2]
                    decimal_point = adc_reg[3]

                    if key_channel == adc_name:
                        adc = lsb * (value_adc[0] + value_adc[1])
                        adc_final = round(adc, decimal_point+1)
                        adc_dict[key_channel] = adc_final
                adc_info.append(f"        // {key_channel} : {adc_final}")

            time_stamp = self.get_timestamp(content=data)
            sorted_adc = [adc_dict[k] for k in sorted(adc_dict)]
            adc_log = [time_stamp,
                999999, 999999, 999999, 999999, 999999,
                999999, 999999, 999999, 999999, 999999,
                999999, 999999, 999999, 999999, 999999,
                999999, 999999] + sorted_adc
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

                        remark = ""
                        mode_bit = None
                        if "8583" in self.device:
                            if reg_name == "MODE":
                                if masked_value in [0, 4]: mode_bit = 4
                                elif masked_value in [1, 5]: mode_bit = 3
                                elif masked_value in [2, 6]: mode_bit = 2
                                elif masked_value in [3, 7]: mode_bit = 1
                            if reg_name == "VIN_OVP":
                                vin_ovp_offset = [3.75, 7.5, 11.25, 15]
                                if mode_bit != None:
                                    remark = f"     --->  {vin_ovp_offset[mode_bit-1]+0.2*mode_bit*masked_value:.02f}V"
                            elif reg_name == "VEXT_OVP":
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
                        
                        elif "8563" in self.device:
                            ext_ovp = [6.5, 13, 13.5, 17, 17.5, 18, 18.5, 19]
                            if reg_name == "MODE":
                                if masked_value in [0, 4]: mode_bit = 3
                                elif masked_value in [1, 5]: mode_bit = 2
                                elif masked_value in [2, 3, 6, 7]: mode_bit = 1
                            if reg_name == "VIN_OVP":
                                vin_ovp_offset = [4.8, 9.6, 14.4]
                                if mode_bit != None:
                                    remark = f"     --->  {vin_ovp_offset[mode_bit-1]+0.1*mode_bit*masked_value:.01f}V"
                            elif reg_name == "EXT1_OVP":
                                remark = f"     --->  {ext_ovp[masked_value]:.01f}V"
                            elif reg_name == "EXT2_OVP":
                                remark = f"     --->  {ext_ovp[masked_value]:.01f}V"
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
            
            stat_info.append(" ")

            return adc_info + flag_info + stat_info + ret
        
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

            if self.store_ppsv != None:
                if vbus_value/self.store_ppsv*100 > 50:
                    calculated_r_vbus = (self.store_ppsv - vbus_value) / iin_value * 1000
                    # print(f"r1 = ({self.store_ppsv}-{vbus_value})/{iin_value}*1000 = {calculated_r_vbus}")
                else:
                    calculated_r_vbus = 999999
                if vwpc_value/self.store_ppsv*100 > 50:
                    calculated_r_vwpc = (self.store_ppsv - vwpc_value) / iin_value * 1000
                    # print(f"r2 = ({self.store_ppsv}-{vwpc_value})/{iin_value}*1000 = {calculated_r_vwpc}")
                else:
                    calculated_r_vwpc = 999999

            try:
                vbat_diff = vbat_target_value - vbat_ifpm_value
                vbat_adc_diff = vbat_ifpm_value - vbat_dcic_value
                iin_diff  = iin_target_value - iin_value

                '''
                if self.logging:
                    print(f"iin_value : {iin_value}")
                    print(f"iin_target_value : {iin_target_value}")
                    print(f"vbat_ifpm_value : {vbat_ifpm_value}")
                    print(f"vbat_target_value : {vbat_target_value}")
                    print(f"power_value : {power_value}")
                    print(f"vbus_value : {vbus_value}")
                    print(f"vwpc_value : {vwpc_value}")
                    print(f"vbat_dcic_value : {vbat_dcic_value}")
                '''
                
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
                    "vwpc"          : [vwpc_value, "V"],
                    "calculated_r1" : [calculated_r_vbus, "mR"],
                    "calculated_r2" : [calculated_r_vwpc, "mR"]
                }

                for item, value in value_dict.items():
                    ret = ret + f"        // {item} : {value[0]:.03f}{value[1]}\n"
                
                csv_list = [time_stamp, 999999, 999999, 999999, 999999,
                            iin_target_value, iin_value      , iin_diff     , vbat_target_value, vbat_ifpm_value,
                            vbat_diff,        vbat_dcic_value, vbat_adc_diff, power_value      , vbus_value     ,
                            vwpc_value,       calculated_r_vbus,              calculated_r_vwpc, self.batt_curr]
                log.output_csv(message=csv_list)
                
                self.batt_curr = 999999
                
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
            ret = f"        // {suffix} : {data}\n"

        return ret
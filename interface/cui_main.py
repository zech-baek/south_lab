# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib

try:
    # try to use __file__
    interface_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        interface_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        interface_dir = os.getcwd()

log_dir = pathlib.Path(interface_dir).parent/"log"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)
#     print(f"created directory: {log_dir}")

# print(f"interface_dir dir : {interface_dir}")
# print(f"log directory : {log_dir}")


from interface.cui_logger import logger as log
from interface.cui_register import register_mapping
from interface.cui_colors import color
from interface.docs.output_excel import excel_frame

from tabulate import tabulate as tb
import sys
import pandas as pd


def log_wrapping(header, message, is_logging):
    
    msg = f"[{header} {sys._getframe(2).f_code.co_name}] {message}"
    log.forcedLog(msg) if is_logging else log.debugLog(msg)


class cache:
    
    initialized = False

    i2c_a    = None
    i2c_h    = None
    device   = None
    reg_map  = None
    reg_page = None
    retry    = 1
    logging  = True
    is_gui   = False

    read_header = [
            "Reg",
            "Split",
            "Addr",
            "MSB",
            "LSB",
            "BitH",
            "BitL",
            "MaskH",
            "MaskL",
            "ReadByte",
            "MaskedData",
            "RelocatedData"
        ]

    write_header = [
            "Reg",
            "Split",
            "Addr",
            "MSB",
            "LSB",
            "BitH",
            "BitL",
            "ReadByte",
            "SplitMsk",
            "SplitData",
            "nMask",
            "MaskedData",
            "NewByte",
            "Readback",
            "MaskReadback"
        ]
    


class cui_frame:

    def __init__(self, regmap, i2c_info, i2c_h, device, logging=False, is_gui=False):
        
        cache.reg_map = regmap
        cache.i2c_a   = i2c_info["i2c_address"]["default"] # 7bit format
        cache.i2c_h   = i2c_h
        cache.device  = device
        cache.logging = logging
        
        cache.is_gui = False if is_gui else True # disable logging if is_gui is True

        i2c_pool = i2c_info["i2c_address"]["alternative"]
        
        log_wrapping(
            self.__class__.__name__,
            f"assigned {color.blue}{cache.i2c_a:#04x} by default address{color.end} in 7bit",
            cache.logging
            )
        
        for key, value in i2c_pool.items():
            log_wrapping(
                self.__class__.__name__,
                f"{color.blue}alt address[{key}] {value:#04x}{color.end} : read {(value<<1)+1:#04x} write {value<<1:#04x}",
                cache.logging
                )
        
        # pdb.set_trace()
        
        self.regmap_gen(cache.reg_map)
        cache.initialized = True

        log_wrapping(f"{cache.device}", f"initialized with i2c address {cache.i2c_a:#04x} by default", True)
    
    
    def close(self):
        
        cache.initialized = False
        cache.i2c_a    = None
        cache.i2c_h    = None
        cache.device   = None
        cache.reg_map  = None
        cache.reg_page = None
        cache.retry    = 1
        cache.logging  = True
        
        log_wrapping(
            self.__class__.__name__,
            f"cleanup the class object",
            cache.is_gui
        )


    def __del__(self):
        
        log_wrapping(
            self.__class__.__name__,
            f"class object destroyed",
            cache.is_gui
        )


    def regmap_gen(self, reg_map):

        cache.reg_page = dict()

        for key in reg_map.keys():

            reg_name  = key

            reg_addr = list()
            reg_msb  = list()
            reg_lsb  = list()
            reg_bith = list()
            reg_bitl = list()

            reg_split = sum(1 for item in reg_map[key] if "address" in item)

            for n in range(reg_split):
                reg_addr.append(reg_map[key][f"address{n+1}"])
                reg_lsb.append(reg_map[key][f"lsb{n+1}"])
                reg_msb.append(reg_map[key][f"msb{n+1}"])
                reg_bith.append(reg_map[key][f"bith{n+1}"])
                reg_bitl.append(reg_map[key][f"bitl{n+1}"])

            reg_auth  = reg_map[key]["permission"]
            reg_rw    = reg_map[key]["rw"]
            
            cache.reg_page[reg_name] = [
                reg_split,
                reg_name,
                reg_addr,
                reg_msb,
                reg_lsb,
                reg_bith,
                reg_bitl,
                reg_auth,
                reg_rw
                ]
            
        # df = pd.DataFrame(cache.reg_page)
        # print(tb.tabulate(df.T, headers=["Key", "Singular", "Name", "Address", "LSB", "MSB", "BITH", "BITL", "Permission", "Read/Write"]))

        for key, value in cache.reg_page.items():
            log.debugLog(f"reg_map[{key}] : {value}")
            setattr(self, key, register_mapping(parm=value))
    
    
    def retry(self, count):
        
        pre_config = cache.retry
        cache.retry = count
        log_wrapping(
            self.__class__.__name__,
            f"chagne the number for retry : {pre_config} --> {count}",
            cache.is_gui
        )
        
        
    def get_i2c_address(self):
        return cache.i2c_a
    
    
    def get_i2c_handler(self):
        return cache.i2c_h
    
    
    def get_regmap(self):
        return cache.reg_map


    def get_regpage(self):
        return cache.reg_page
    
    
    def get_regmap_excel(self):
        
        rows = []
        for key, values in cache.reg_map.items():
            row = {'key': key}  # add top-level key as "key" column
            row.update(values)   # merge sub-dictionary into row
            rows.append(row)

        df = pd.DataFrame(rows)
        filename = log.time_stamp(display=False, ret=True) + f"_{cache.device}_regmap.xlsx"
        df_excel = log_dir/filename
        df.to_excel(df_excel, index=False)
    
    
    def log_enable(self):
        
        cache.logging = True
        cache.i2c_h.logging = True
        
        log_wrapping(
            self.__class__.__name__,
            f"enable logging",
            cache.logging
            )
    
    
    def log_disable(self):
        
        cache.logging = False
        cache.i2c_h.logging = False
        
        log_wrapping(
            self.__class__.__name__,
            f"disable logging",
            cache.logging
            )
    
    
    def i2c_scan(self, update=True):

        ret = cache.i2c_h.smbus_scan()
        len_ret = len(ret)

        if len_ret > 0:
            log_wrapping(
                self.__class__.__name__,
                f"acked address list : {color.bgyel}{color.blue}{ret}{color.end}",
                cache.is_gui
            )

            if update:
                if isinstance(ret[0], int):
                    self.update_i2c_address(address_7bit=ret[0])
            else:
                log_wrapping(
                    self.__class__.__name__,
                    f"manually update i2c address is required at self.update_i2c_address() (current i2c address : {cache.i2c_a}, {cache.i2c_a:#04x})",
                    cache.is_gui
                )
                
            return ret
        
        else:
            log_wrapping(
                self.__class__.__name__,
                f"{color.red}device not found{color.end}",
                cache.is_gui
            )
            return None
    
    
    def update_i2c_address(self, address_7bit):
        
        pre_addr    = cache.i2c_a
        cache.i2c_a = address_7bit
        
        log_wrapping(
            self.__class__.__name__,
            f"update i2c address : {pre_addr:#04x} --> {color.bold}{color.blue}{cache.i2c_a:#04x}{color.end}",
            cache.is_gui
        )
    
    
    def register_dump(self, *args):
        
        len_args = len(args)
        
        # case 1 : autoset the filename
        if len_args == 0:
            filename = log.time_stamp(display=False, ret=True) + f"_{cache.device}_dump"
            xl = excel_frame(file=filename)
            xl.worksheet_title = cache.device
            self.excel_dump(obj=xl, filename=filename)
        
        # case 2 : setup the filename by manual input
        else:
            xl = excel_frame(file=filename)
            xl.worksheet_add = f"{cache.device}_dump"
            self.excel_dump(obj=xl, filename=filename)


    def excel_dump(self, obj, filename):
        
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

        for key in cache.reg_page.keys():
            
            start_row += 1
            readback = getattr(self, key)
            temp = [key, readback, f"{readback:#x}"]
            xl.insert_list = start_row, 2, temp
            log.output_csv(temp)
        
        xl.close
    
    
    def _read(self, name):
        
        reg   = self.__dict__[name]
        i2c_a = cache.i2c_a
        i2c_h = cache.i2c_h

        split_index = reg.split # counted in the self.regmap_gen()

        ret_list = list()
        tb_map   = list()
        tb_map.append(cache.read_header)
        
        for index in range(split_index):
            
            reg_address   = reg.addr[index]
            msb_msk       = 0
            lsb_msk       = 0
            msb_index     = reg.msb[index]
            lsb_index     = reg.lsb[index]
            high_position = reg.bith[index]
            low_position  = reg.bitl[index]
            
            readbyte = i2c_h.i2c_read(i2c_a, reg_address)
            
            # masking range
            msb_msk += sum((1<<msb) for msb in range(msb_index + 1, 8))
            lsb_msk += sum((1<<lsb) for lsb in range(0, lsb_index))
            
            masked_value = ((readbyte & (~msb_msk)) & (~lsb_msk)) >> lsb_index
            relocated_value = masked_value << low_position
            ret_list.append(relocated_value)

            if cache.logging:
                item_list = [
                    name,
                    f"{index+1}/{split_index}",
                    f"{reg_address:#04x}",
                    msb_index,
                    lsb_index,
                    high_position,
                    low_position,
                    f"{msb_msk:#04x}",
                    f"{lsb_msk:#04x}",
                    f"{readbyte:#04x}",
                    f"{masked_value:#04x}",
                    f"{relocated_value:#04x}"
                    ]
                tb_map.append(item_list)
        
        if cache.logging:
            print(tb(tb_map, headers="firstrow"))
        
        return sum(ret_list)
            
    
    def _write(self, name, value):
        
        reg   = self.__dict__[name]
        i2c_a = cache.i2c_a
        i2c_h = cache.i2c_h
        
        split_index = reg.split
        value_limit = (1 << (max(reg.bith) + 1)) - 1
        
        tb_map = list()
        tb_map.append(cache.write_header)
        
        if reg.rw == "R":
            log_wrapping(
                self.__class__.__name__,
                f"{name} is read-only type ({reg.rw})",
                cache.is_gui
            )
        
        elif reg.rw == "RC":
            log_wrapping(
                self.__class__.__name__,
                f"{name} is read and clear type ({reg.rw})",
                cache.is_gui
            )
            
        elif value > value_limit:
            log_wrapping(
                self.__class__.__name__,
                f"input value {value} exceeds the limit {value_limit}",
                cache.is_gui
            )
        
        else:
            for index in range(split_index):
                
                reg_address   = reg.addr[index]
                msb_index     = reg.msb[index]
                lsb_index     = reg.lsb[index]
                high_position = reg.bith[index]
                low_position  = reg.bitl[index]
                
                readbyte = i2c_h.i2c_read(i2c_a, reg_address)
                
                # split the value to match with index
                split_mask = (1 << (high_position - low_position + 1)) - 1
                split_data = (value >> low_position) & split_mask
                
                # clear the taget bits between msb and lsb
                mask        = ~(((1 << (msb_index - lsb_index + 1)) -1) << lsb_index)
                masked_data = readbyte & mask
                new_data    = masked_data | (split_data << lsb_index)
                
                i2c_h.i2c_write(i2c_a, reg_address, new_data)

                if cache.logging:
                    readback = i2c_h.i2c_read(i2c_a, reg_address)
                    masked_readback = readback & (~mask)

                    item_list = [
                        name,
                        f"{index+1}/{split_index}",
                        f"{reg_address:#04x}",
                        msb_index,
                        lsb_index,
                        high_position,
                        low_position,
                        f"{readbyte:#04x}",
                        f"{split_mask:#04x}",
                        f"{split_data:#04x}",
                        f"{~mask:#04x}",
                        f"{masked_data:#04x}",
                        f"{new_data:#04x}",
                        f"{readback:#04x}",
                        f"{masked_readback:#04x}"
                        ]
                    tb_map.append(item_list)
                
            if cache.logging:
                print(tb(tb_map, headers="firstrow"))
    
    
    def read_byte(self, reg_8h):
        
        ret   = cache.i2c_h.i2c_read(cache.i2c_a, reg_8h)
        
        log_wrapping(
            self.__class__.__name__,
            f"byte read : {reg_8h:#04x}={ret:#04x}",
            cache.logging
            )
        
        return ret
    
    
    def write_byte(self, reg_8h, value):
        
        cache.i2c_h.i2c_write(cache.i2c_a, reg_8h, value)
        
        log_wrapping(
            self.__class__.__name__,
            f"byte write : {reg_8h:#04x}={value:#04x}",
            cache.logging
            )
        
        
    def __setattr__(self, name, value):
        
        # if cache._initialized is False,
        # __getattribute__ will call the __settattr__ to asign the attribute
        
        if cache.initialized:
            if name in cache.reg_map.keys():
                self._write(name, value)
            else:
                super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)
            
    
    def __getattr__(self, name):
        
        # code for variable not in cache.reg_map
        if name == "_read":
            object._read(name)
        else:
            # execute if the variable doesn't exist in the instance properties
            raise AttributeError(f"{name} not found")
            # return super().__setattr__(name, None)
    
    
    def __getattribute__(self, name):
        
        # execute first whenever the varible is called
        # if the variable doesn't exist, __getattr__ is executed next

        if cache.initialized:
            if name in cache.reg_map.keys():
                return self._read(name=name)
            else:
                # call the super class to avoid recursion error
                return object.__getattribute__(self, name)
        else:
            # call the super class to avoid recursion error
            return super().__getattribute__(name)
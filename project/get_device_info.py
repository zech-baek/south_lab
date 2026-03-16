# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib

try:
    # try to use __file__
    temp_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        temp_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        temp_dir = os.getcwd()

base_dir = pathlib.Path(temp_dir)
root_dir = pathlib.Path(base_dir).parent
log_dir  = pathlib.Path(base_dir).parent/"log"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)

from interface.cui_logger import logger as log
import pandas as pd
import yaml


def get_map(device, revision):
    
    with open(base_dir/f"{device}/{device}_{revision}_reg.yaml") as reg:
        regmap = yaml.safe_load(reg)
    
    return regmap


def get_i2c_info(device):
    
    with open(base_dir/f"{device}/{device}_i2c.yaml") as reg:
        i2c_info = yaml.safe_load(reg)
    
    return i2c_info


def get_status(device, revision):
    
    with open(base_dir/f"{device}/{device}_{revision}_status.yaml") as reg:
        reg_status = yaml.safe_load(reg)
    
    return reg_status


def get_regpage(device, revision):

    reg_map = get_map(device=device, revision=revision)

    reg_page = dict()

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
        
        reg_page[reg_name] = [
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
    
    return reg_page


def get_reg_table(device, revision):
    
    reg_map = get_map(device, revision)
    sts_map = get_status(device, revision)
    
    addr_list = list(sts_map.keys())
    addr_list.sort(key=abs)
    
    # column order for the table
    # value[0] : address
    # value[1] : register name
    # value[2] : register type
    # value[3] : previous value
    # value[4] : current value
    # value[5] ~[12] : bit7 ~ 0
    
    reg_table = dict()
    
    for addr in addr_list:
        reg_table[addr] = ["Rsvd" for _ in range(14)] # for reserved bit
    
    for key, value in reg_map.items():
        
        cnt = sum(1 for item in value if "address" in item) # for seperated register
        try: 
            if cnt == 1 and  value["msb1"] == value["lsb1"]:
                address = value["address1"]
                reg_table[address][0] = address
                reg_table[address][1] = value["register1"]
                reg_table[address][2] = value[f"rw"]
                reg_table[address][3] = 0
                reg_table[address][4] = 0
                msb = value["msb1"]
                
                reg_table[address][12-msb] = key
                permission = value["permission"]
                reg_table[address][13] = permission
                
            else:
                cnt = sum(1 for item in value if "address" in item) # for seperated register
            
                for index in range(cnt):
                    address = value[f"address{index+1}"]
                    bith = value[f"bith{index+1}"]
                    bitl = value[f"bitl{index+1}"]
                    msb  = value[f"msb{index+1}"]
                    lsb  = value[f"lsb{index+1}"]
                    
                    reg_table[address][0] = address
                    reg_table[address][1] = value[f"register{index+1}"]
                    reg_table[address][2] = value[f"rw"]
                    reg_table[address][3] = 0
                    reg_table[address][4] = 0
                    
                    for name_index in range(msb, lsb-1, -1):
                        # log.forcedLog(f"{key}, cnt={cnt}, {12-name_index}, singluar={singular}, bith={bith}, bitl={bitl}, msb={msb}, lsb={lsb}")
                        reg_table[address][12-name_index] = f"{key}[{bith}]"
                        bith -= 1
                    
                    permission = value["permission"]
                    reg_table[address][13] = permission
        except:
            print(f"error : key={key}, value={value}, index={index}")
            
    return reg_table


def get_excel_regmap(device, revision):

    with open(base_dir/f"{device}/{device}_{revision}_reg.yaml") as reg:
        regmap = yaml.safe_load(reg)
    
    # convert dictionary to list of rows
    rows = []
    
    for key, value in regmap.items():
        row = {'key': key}  # add top-level key as 'key' column
        row.update(value)   # merge sub-dictionary into row
        rows.append(row)

    # create DataFrame
    df = pd.DataFrame(rows)
    file_name = log.time_stamp(display=False, ret=True) + f"regmap_output.xlsx"
    df.to_excel(log_dir/file_name, index=False)
    
    print("converted the register map to excel file : regmap_output.xlsx")

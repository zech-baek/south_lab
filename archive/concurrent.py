from concurrent.futures import ThreadPoolExecutor

def change_ocp():
    # delay(0.08)
    ic.IIN_OCP = 0
    return "change ocp"

def change_vout():
    module_info = ["01", "11", "10", "08", "01", "13", "88", "00", "00", "00", "00", "00"] # 5.0V
    ret_crc16 = crc_generate(" ".join(module_info))
    module_info.extend(ret_crc16)

    len_packet = len(module_info)

    for i in list(range(len_packet)):
        dev.write(bytes.fromhex(module_info[i]))

    return "change vout"


with ThreadPoolExecutor(max_workers=2) as executor:
    func1 = executor.submit(change_ocp)
    func2 = executor.submit(change_vout)
    ret_ocp = func1.result()
    ret_vout = func2.result()
    
    print(ret_ocp, ret_vout)


delay(0.1)

module_info = ["01", "11", "10", "08", "01", "0f", "a0", "00", "00", "00", "00", "00"] # 5.0V
ret_crc16 = crc_generate(" ".join(module_info))
module_info.extend(ret_crc16)

for c in module_info:
    dev.write(bytes.fromhex(c))


















from phy.multimeter import keithley_dm6500 as dmm
from interface.cui_logger import logger as log
from time import sleep as delay
import time

dm1 = dmm(id1)
dm2 = dmm(id2)
dm3 = dmm(id3)

def func_iin():
    iin = dm3.voltage_1E_1 / 0.002
    return iin

def func_vbus_sub():
    vbus_sub  = dm2.voltage_100
    return vbus_sub

def func_vbus_main():
    vbus_main = dm1.voltage_100
    return vbus_main

start = time.time()

while True:
    lap = time.time() - start
    with ThreadPoolExecutor(max_workers=2) as executor:
        t_iin  = executor.submit(func_iin)
        t_sub  = executor.submit(func_vbus_sub)
        t_main = executor.submit(func_vbus_main)
        ret_iin  = t_iin.result()
        ret_sub  = t_sub.result()
        ret_main = t_main.result()
    print(f"{lap:.02f} {ret_iin:.06f} {ret_sub:.06f} {ret_main:.06f}")
    delay(0.2)
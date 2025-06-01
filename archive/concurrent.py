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

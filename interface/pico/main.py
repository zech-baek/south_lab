# Purpose of this file: Main file for Pico GUI, run the file prior to executing GUI python code

from machine import Pin, I2C, UART
import sys
import select

#############################PARAMETERS#################################
sda = Pin(14)  # sda pin
scl = Pin(15)  # scl pin
i2c = I2C(1, sda=sda, scl=scl, freq=400_000)  # i2c initialization
########################################################################

def change_i2c_frequency(freq):
    global i2c
    # Re-initialize the I2C object with the new frequency
    i2c = I2C(1, sda=sda, scl=scl, freq=freq)
    return f"Frequency set to {freq} Hz"

def i2c_read(SID, regAddr, num_bytes=1):
    try:
        a = i2c.readfrom_mem(SID, regAddr, num_bytes) # Reads data from the register
        return "0x" + ''.join('{:02X}'.format(byte) for byte in reversed(a))  # Join bytes as hex string in little-endian order
    except OSError as e:
        return "Error: SID got a nak for read: input SID: 0x{:02X}, input regAddr = 0x{:02X}. Please reenter the correct SID or press 'Detect Device.'".format(SID, regAddr)

def i2c_write(SID, regAddr, data):
    try:
        #data_bytes = bytes.fromhex(data)
        a = i2c.writeto_mem(SID, regAddr, data)
        return "Write successful"
    except OSError as e:
        return "Error: SID got a nak for write: input SID: 0x{:02X}, input regAddr = 0x{:02X}, data = 0x{:02X}. Please reenter the correct SID or press 'Detect Device.'".format(SID, regAddr, data)

def detect_device():
    devices = i2c.scan()
    if devices:
        return " ".join([hex(dev) for dev in devices])
    else:
        return "No devices found"
    
def read_all_registers(SID, start_addr, end_addr):
    result = []
    for regAddr in range(start_addr, end_addr + 1):
        bytes_to_read = 1
        read_result = i2c_read(SID, regAddr, bytes_to_read)
        result.append(f"Register Read [0x{regAddr:02X}] --> {read_result}")
    return "\n".join(result)

while True:
    if select.select([sys.stdin], [], [], 0)[0]:
        command = sys.stdin.readline().strip()
    #if True:
    #    command = "WRITE 10 1C 64".strip()
    #    command = "READ 10 1C 1".strip()
        parts = command.split()
        if parts[0] == "READ":
            _, sid, reg_addr, num_bytes = parts
            sid = int(sid, 16)
            reg_addr = int(reg_addr, 16)
            num_bytes = int(num_bytes)
            result = i2c_read(sid, reg_addr, num_bytes)
            print(result)
        elif parts[0] == "WRITE":
            _, sid, reg_addr, data = parts
            sid = int(sid, 16)
            reg_addr = int(reg_addr, 16)
            data = bytes([int(data, 16)])
            result = i2c_write(sid, reg_addr, data)
            print(result)
        elif parts[0] == "FREQ":
            _, freq = parts
            freq = int(freq)
            result = change_i2c_frequency(freq)
            print(result)
        elif parts[0] == "DETECT":
            result = detect_device()
            print(result)
        elif parts[0] == "READALL":
            _, sid, start_addr, end_addr = parts
            sid = int(sid, 16)
            start_addr = int(start_addr, 16)
            end_addr = int(end_addr, 16)
            result = read_all_registers(sid, start_addr, end_addr)
            print(result)

#! /usr/bin/env python3
# coding=utf-8

import usb.core
import usb.util
import contextlib

from usb.core import Device
from collections import namedtuple
from ctypes import c_int32
from time import perf_counter
from sys import byteorder, exit

import os
import sys
import pathlib
import serial

from interface.cui_logger import logger as log
from interface.cui_colors import color
from time import sleep as delay
from misc.twos_complement import twos_complement as twos

try:
    # try to use __file__
    phy_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        phy_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        phy_dir = os.getcwd()

root_dir = pathlib.Path(phy_dir).parent
equipment_dir = pathlib.Path(phy_dir).parent/"equipment"
log_dir = pathlib.Path(phy_dir).parent/"log"


class km003c:

    Vendor_Id  = 0x5fc9
    Product_Id = 0x63

    def __init__(self, vid=None, pid=None, logging=False, port=None):
        
        # interface 0 : write_address=0x1, read_address=0x81, bInterfaceClass=Vendor Specific, ~1000 samples/sec
        # interface 1 : write_address=0x5, read_address=0x85, bInterfaceClass=HID, ~500 samples/sec
        # interface 3 : write_address=0x3, read_address=0x83, bInterfaceClass=CDC Data, ~ 1000 samples/sec

        self.logging     = logging
        self.log_raw     = None
        self.log_voltage = None
        self.log_current = None
        self.byteorde    = byteorder # little

        self.vid = vid or self.Vendor_Id
        self.pid = pid or self.Product_Id
        self.port = port
        self.connect_usb(self.vid, self.pid)
        self.connect_uart(self.port)
    

    def connect_usb(self, vid, pid):

        self.interface = usb.core.find(idVendor=vid, idProduct=pid)
        if self.interface is None:
            raise ValueError(f"power-z km003c not found")
        
        self._interface_num = 0 # vendor specific message
        self._write_addr = 0x1
        self._read_addr  = 0x81

        usb.util.claim_interface(self.interface, self._interface_num)

        self.dev_struct = namedtuple("device", ["interface", "write_addr", "read_addr"])
        self.h = self.dev_struct(self.interface, self._write_addr, self._read_addr)
    

    def connect_uart(self, port):
        self.uart_handler = serial.Serial(port=port, baudrate=115200)


    def uart_wpd(self, cmd):
        self.uart_handler.write((cmd + "\n").encode("ascii"))


    def uart_rpd(self):
        ret = self.uart_handler.readline().decode('utf-8')
        return ret
    

    @property
    def init_powerz(self):

        self.uart_wpd("pdm open")
        self.uart_wpd("pdm set type=0,em=0,sink=0")
        self.uart_wpd("entry pd")


    @property
    def hard_reset(self):
        self.uart_wpd("reset")
    

    @property
    def cfg_all(self):
        pass


    @cfg_all.setter
    def cfg_all(self, *args):
        
        len_args = len(args)
        
        if len_args == 1:
            pps_v = args[0][0]
            pps_curr = args[0][1]

            conv_pps_v = int(pps_v * 1000)     # 10V order
            conv_pps_i = int(pps_curr * 10000) # 1A order
            self.uart_wpd(f"pd req=5,volt={conv_pps_v},curr={conv_pps_i}")
        else:
            log.forcedLog(f"configuration error, require pps voltage and pps current input (e.g. self.cfg_all = 5, 0.2)")

        conv_pps_v = int(pps_v * 1000)     # 10V order
        conv_pps_i = int(pps_curr * 10000) # 1A order
        self.uart_wpd(f"pd req=5,volt={conv_pps_v},curr={conv_pps_i}")


    def close(self):

        if self.interface is not None:
            try:
                if self.interface.is_kernel_driver_active(0):
                    self.interface.detach_kernel_driver(0)
            except:
                pass

            usb.util.dispose_resources(self.interface)
            self.interface = None
            self.dev_struct = None
            self.h = None
            self.log_list_r  = None
            self.log_voltage = None
            self.log_current = None

            log.forcedLog("remove the km003c device interface")


    def __del__(self):
        self.close()

    
    def __enter__(self):
        return self
    

    def reset(self):

        self.close()
        self.connect_dev(self.vid, self.pid)
        log.forcedLog("reset the km003c device interface")
    

    def send_data(self, cmd):

        ret = self.h.interface.write(self.h.write_addr, cmd)
        if ret != 4:
            log.forcedLog(f"failed to write the bytes, length is not 4 : ret={ret}")
    

    def read_data(self):

        ret = self.h.interface.read(self.h.read_addr, 64)
        return ret
    

    def read_raw(self) -> list:

        cmd = bytes([0xc, 0x0, 0x2, 0x0]).decode("utf-8")
        self.send_data(cmd)
        data = self.read_data()
        return data


    def convert_data(self, data, start):

        raw_voltage = data[start] + (data[start+1]<<8) + (data[start+2]<<16) + (data[start+3]<<24)
        voltage = raw_voltage / 1000_000
        # voltage = int.from_bytes(data[8:12], self.byteorde) / 1000000

        raw_current = data[start+4] + (data[start+5]<<8) + (data[start+6]<<16) + (data[start+7]<<24)
        current = abs(twos.convert_signed_int(raw_current, 32) / 1000_000)
        # current = c_int32(int.from_bytes(data[12:16], self.byteorde)).value / 1000000 # convert negative to 2s compliment

        if self.logging:
            log.forcedLog(f"[{log.time_stamp(display=False, ret=True)}] read data : {data}")
            self.log_raw = data
            self.log_voltage = data[8:12]
            self.log_current = data[12:16]
        
        return [voltage, current]
    

    @property
    def voltage(self):

        raw_data = self.read_raw()
        ret_list = self.convert_data(raw_data, start=8)
        return ret_list[0]
    

    @voltage.setter
    def voltage(self):
        pass
    
    
    @property
    def current(self):

        raw_data = self.read_raw()
        ret_list = self.convert_data(raw_data, start=8)
        return ret_list[1]


    @current.setter
    def current(self):
        pass


    @property
    def voltage_oneshot(self):
        raw_data = self.read_raw()
        ret_list = self.convert_data(raw_data, start=16)
        return ret_list[0]
    

    @voltage_oneshot.setter
    def voltage_oneshot(self):
        pass
    
    
    @property
    def current_oneshot(self):
        raw_data = self.read_raw()
        ret_list = self.convert_data(raw_data, start=16)
        return ret_list[1]


    @current_oneshot.setter
    def current_oneshot(self):
        pass
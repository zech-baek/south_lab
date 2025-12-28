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

    def __init__(self, vid=0x5fc9, pid=0x63, logging=False):
        
        # interface 0 : write_address=0x1, read_address=0x81, bInterfaceClass=Vendor Specific, ~1000 samples/sec
        # interface 1 : write_address=0x5, read_address=0x85, bInterfaceClass=HID, ~500 samples/sec
        # interface 3 : write_address=0x3, read_address=0x83, bInterfaceClass=CDC Data, ~ 1000 samples/sec

        self.logging     = logging
        self.log_raw     = None
        self.log_voltage = None
        self.log_current = None
        self.byteorde    = byteorder # little

        self.vid = vid
        self.pid = pid
        self.connect_dev(self.vid, self.pid)
    

    def connect_dev(self, vid, pid):

        self.interface = usb.core.find(idVendor=vid, idProduct=pid)
        self._interface_num = 0 # vendor specific message
        self._write_addr = 0x1
        self._read_addr  = 0x81

        usb.util.claim_interface(self.interface, self._interface_num)

        self.dev_struct = namedtuple("device", ["interface", "write_addr", "read_addr"])
        self.h = self.dev_struct(self.interface, self._write_addr, self._read_addr)
    

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
    

    def read_raw(self) -> float:

        cmd = bytes([0xc, 0x0, 0x2, 0x0]).decode("utf-8")
        ret_write = self.h.interface.write(self.h.write_addr, cmd)

        if ret_write != 4:
            log.forcedLog(f"failed to write the bytes, length is not 4 : ret={ret_write}")

        data = self.h.interface.read(self.h.read_addr, 64)

        raw_voltage = data[8] + (data[9]<<8) + (data[10]<<16) + (data[11]<<24)
        voltage = raw_voltage / 1000_000
        # voltage = int.from_bytes(data[8:12], self.byteorde) / 1000000

        raw_current = data[12] + (data[13]<<8) + (data[14]<<16) + (data[15]<<24)
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
        return self.read_raw()[0]
    

    @voltage.setter
    def voltage(self):
        pass
    
    
    @property
    def current(self):
        return self.read_raw()[1]


    @current.setter
    def current(self):
        pass
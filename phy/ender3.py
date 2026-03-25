# ! /usr/bin/env python
# coding=utf-8

import os, sys,pathlib

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

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)


from interface.cui_logger import logger as log
from interface.cui_colors import color
from tabulate import tabulate as tb
from time import sleep as delay
import serial


class preset:

    parm_reset = "G28" # move to origin
    parm_abs   = "G90" # absolute coordinate
    parm_rel   = "G92" # relative coordinate, set the current coordinate to 0
    parm_mov   = "G0"
    parm_limit = "240" # absolute mode : 0 ~ 240
    abs_coor   = [0, 0, 0]
    rel_coor   = [120, 120, 50] # adjusted coordinate


# F number : moving speed (lower than 3000 for x and y, z for max 300)

class ender3(serial.Serial):

    def __init__(self, port=None, baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=1, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None):
        
        super().__init__(port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts, write_timeout, dsrdtr, inter_byte_timeout, exclusive)

        while self.in_waiting:
            print(self.readline().decode().strip()) # make empty log
        
        self.mode = None
        self.coor_now = [0, 0, 0]
        self.coor_rel = [120, 120, 50]
    

    def set_abs_mode(self):
        self.mode = "abs"
    

    def set_rel_mode(self):
        self.mode = "rel"


    def reset_abs_origin(self):

        self.set_abs_mode()
        self.send(preset.parm_reset)
        self.coor_now = preset.abs_coor
        log.forcedLog(f"reset [x, y, z] coordinate to {preset.abs_coor} in {self.mode} mode")
    

    def reset_rel_origin(self):

        preset.parm_coor = [120, 120, 50]
        self.set_rel_mode()
        self.coor_now = preset.rel_coor
        log.forcedLog(f"reset [x, y, z] coordinate to {preset.rel_coor} in {self.mode} mode")
    

    def status(self):

        if "abs" in self.mode:
            log.forcedLog(f"coordinate in {self.mode} mode : x={self.coor_now[0]}, y={self.coor_now[1]}, z={self.coor_now[2]}")
        elif "rel" in self.mode:
            log.forcedLog(f"coordinate in {self.mode} mode : x={self.coor_now[0]} ({self.coor_rel[0]}), y={self.coor_now[1]} ({self.coor_rel[1]}), z={self.coor_now[2]} ({self.coor_rel[2]})")
    

    def send_packet(self, cmd):

        self.write((cmd + "\n").encode())
        delay(0.5)
        
        while self.in_waiting:
            print(self.readline().decode().strip())
    

    def close(self):
        self.close()
    

    def check_limit(self, coordinate):

        if self.mode is "abs":
            if coordinate > preset.limit:
                coordinate = preset.limit
            elif coordinate < 0:
                coordinate = 0
    

    def set_abs_mode(self):

        self.mode = "absolute"
        self.reset_origin()
    

    def set_rel_mode(self):

        self.mode = "relative"
        self.reset_origin()
    

    def reset_device(self):

        self.send_packet(cmd=preset.origin)
        self.set_mode(abs=True)
        log.forcedLog(f"reset to (0, 0, 0) and absolute coordinate mode")
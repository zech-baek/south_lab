# ! /usr/bin/env python
# coding=utf-8

import re
import serial
import threading
import os, sys,pathlib
from interface.cui_logger import logger as log
from interface.cui_colors import color
from tabulate import tabulate as tb
from time import sleep as delay


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



class preset:

    axis_min = 0
    axis_max = 240 # for x and y axis
    marging  = 20
    safe_min = 20
    safe_max = 220
    abs_default = (20, 20, 50)
    rel_default = (120, 120, 50)

    code_home     = "G28" # move to home
    code_abs      = "G90" # absolute coordinate
    code_one      = "G91" # move based on current coordinate, call one-shot
    code_redefine = "G92" # redefine the given coordinate to origin (e.g. G92 X0, Y0, Z0)
    code_move     = "G0"
    code_status   = "M114"



class ender3(serial.Serial):

    """
    - ender-3 3d printer coordinate controller via pyserial
    - absolute mode
        G90
        G0 X100 --> head is X=100
    - relative mode
        G90
        G0 X50
        G91
        G0 X30 --> move head to X=50+30
    - redefine
        G90
        G0 X50
        G92 X0 --> rename current position as X0 (buy physically X=50)
        G0 X50 --> move head to X=50+50
    - default absolute mode after initialization
    - f number : moving speed (lower than 3000 for x and y, z for max 300)
    - method definition
        set_abs_mode
        set_rel_mode
        reset_coordinate
        move_x
        move_y
        move_z
        status
    """

    def __init__(
            self,
            abs_mode:bool=False,
            rel_mode:bool=False,
            one_shot:bool=False,
            port:str=None, 
            baudrate:int=115200,
            timeout:int=1,
            bytesize:int=8
            ):
        
        try:
            super().__init__(port=port, baudrate=baudrate, timeout=timeout, bytesize=bytesize)
        except serial.SerialException as e:
            raise ConnectionError(f"failed to connect to {port}: {e}")

        while self.in_waiting:
            print(self.readline().decode().strip()) # make empty log

        self.mode = None
        self.origin = list() # current origin
        self.coordinate = list() # current coordinate

        if abs_mode and rel_mode:
            raise ValueError("abs_mode and rel_mode cannot both be true")
        
        delay(5)
        log.forcedLog("require zeroing via reset_abs_default")
    

    def flush(self):
        
        # while self.in_waiting:
            # print(self.readline().decode().strip())
        self.reset_input_buffer()
    
    
    @property
    def set_abs_mode(self):

        self.mode = "abs"
        self.origin = [20, 20, 20]
        self.coordinate = [0, 0, 0]
        self.send_packet(f"{preset.code_abs}") # set coordinate to default
        self.move_x = self.coordinate[0]+20
        self.move_y = self.coordinate[1]+20
        self.move_z = self.coordinate[2]+20
        log.forcedLog(f"set to {self.mode} mode and coordinate {self.origin}")
    

    @property
    def set_rel_mode(self):

        self.mode = "rel"
        self.origin = [self.coordinate[0], self.coordinate[1], self.coordinate[2]]
        self.coordinate = [0, 0, 0]
        self.send_packet(f"{preset.code_redefine} X{self.origin[0]} Y{self.origin[1]} Z{self.origin[2]}") # set coordinate to default
        log.forcedLog(f"set to {self.mode} mode and coordinate {self.origin}")
    

    @property
    def set_one_shot(self):

        self.mode = "one_shot"
        self.origin = [self.coordinate[0], self.coordinate[1], self.coordinate[2]]
        self.coordinate = [0, 0, 0]
        self.send_packet(f"{preset.code_one}")
        log.forcedLog(f"set to {self.mode} mode and coordinate {self.origin}")
    

    @property
    def reset_rel_origin(self):

        self.mode = "rel"
        self.origin = [self.coordinate[0], self.coordinate[1], self.coordinate[2]]
        self.send_packet(f"{preset.code_redefine} X{self.origin[0]} Y{self.origin[1]} Z{self.origin[2]}") # reset current coordinate to origin
        self.status
    
    
    @property
    def reset_abs_default(self):

        self.mode = "abs"
        self.origin = [0, 0, 0]
        self.coordinate = [20, 20, 50]
        self.send_packet(preset.code_home)
        self.move_x = self.coordinate[0]
        self.move_y = self.coordinate[1]
        self.move_z = self.coordinate[2]
        self.status
    

    @property
    def reset_rel_default(self):

        self.mode = "rel"
        self.origin = [120, 120, 50]
        self.coordinate = [120, 120, 50]
        self.send_packet(f"{preset.code_redefine} X{self.origin[0]} Y{self.origin[1]} Z{self.origin[2]}")
        self.move_x = self.coordinate[0]
        self.move_y = self.coordinate[1]
        self.move_z = self.coordinate[2]
        self.status
    

    @property
    def zeroing(self):
        self.reset_abs_default
    
    
    @property
    def move_x(self):
        pass

    @move_x.setter
    def move_x(self, value:int) -> None:
        self.send_packet(f"{preset.code_move} X{value}")
    

    @property
    def move_y(self):
        pass

    @move_y.setter
    def move_y(self, value:int) -> None:
        self.send_packet(f"{preset.code_move} Y{value}")
    

    @property
    def move_z(self):
        pass

    @move_z.setter
    def move_z(self, value:int) -> None:
        self.send_packet(f"{preset.code_move} Z{value}")
    

    @property
    def status(self):

        header = ["mode", color.cyan+"origin_x"+color.end, color.cyan+"origin_y"+color.end, color.cyan+"origin_z"+color.end, "coordinate_x", "coordinate_y", "coordinate_z"]
        data = [self.mode, self.origin[0], self.origin[1], self.origin[2], self.coordinate[0], self.coordinate[1], self.coordinate[2]]
        ret = [header, data]
        print(tb(ret, headers="firstrow"))
    

    def send_packet(self, cmd):

        if self.is_open:

            self.write((cmd+"\n").encode("utf-8"))
            
            # while self.in_waiting:
            #     print(self.readline().decode().strip())

            res_line = []
            while True:
                line = self.readline().decode("utf-8").strip()
                if line:
                    res_line.append(line)
                if "ok" in line.lower():
                    break

            return "\n".join(res_line)
        
        else:
            raise ConnectionError("serial port is not open")
    

    def update_position(self):

        """
        ask for actual position
        internal tracking
        return absolute coordinates
        """

        if self.mode == None:
            log.forcedLog("require zeroing before update position")

        else:
            res = self.send_packet(preset.code_status)
            ret = {}
            temp = res.replace(" ", "").lower()
            part1, part2 = re.split(r"count", temp)
            for a, b in re.findall(r"([xyz]):([0-9.]+)", part1):
                ret["rel_"+a] = int(float(b))
            for c, d in re.findall(r'([xyz]):(\d+)', part2):
                ret["abs_"+c] = int(d)
            
            tb_list = list()
            header = [
                "mode",
                color.cyan+"rel_x"+color.end,
                color.cyan+"rel_y"+color.end,
                color.cyan+"rel_z"+color.end,
                "abs_x",
                "abs_y",
                "abs_z"
                ]
            
            data = [
                self.mode,
                ret["rel_x"],
                ret["rel_y"],
                ret["rel_z"],
                ret["abs_x"],
                ret["abs_y"],
                ret["abs_z"]
                ]
            tb_list = [header, data]
            print(tb(tb_list, headers="firstrow"))

            return ret


    def close(self):

        if self.is_open:
            self.close()
    

    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
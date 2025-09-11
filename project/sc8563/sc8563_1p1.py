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
root_dir = pathlib.Path(temp_dir).parent
log_dir  = pathlib.Path(temp_dir).parent/"log"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)


from interface.cui_main import cui_frame
from interface.cui_i2c import allcoation
from interface.cui_logger import logger as log
from project.get_device_info import get_map, get_i2c_info

# customizing module
from project.sc8563.sc8563_function import function
from project.sc8563.sc8563_parsing import parsing

log.initLogger(log.error)


class project(cui_frame, function, parsing):

    def __init__(self, **kwargs):

        self.device      = kwargs.get("device")
        self.revision    = kwargs.get("revision")
        self.device_path = base_dir
        emulator         = kwargs.get("emulator")
        is_gui           = kwargs.get("is_gui")
        
        if "logging" in kwargs.keys():
            is_logging = kwargs.get("logging")
        else:
            is_logging = False
        
        if is_logging:
            print(f"- base directory    : {root_dir}")
            print(f"- project directory : {base_dir}")
            
        if not emulator or not self.revision or not self.revision:
            raise Exception(f"required mandatory parameters : device, revision and emulator")
        
        else:
            # with open(self.path+f"/{self.device}_i2c.yaml") as yaml_i2c:
            #     i2c_info = yaml.safe_load(yaml_i2c)

            # with open(self.path+f"/{self.device}_{self.revision}_reg.yaml") as yaml_device:
            #     reg_map = yaml.safe_load(yaml_device)

            reg_map  = get_map(device=self.device, revision=self.revision)
            i2c_info = get_i2c_info(device=self.device)
            
            i2c = allcoation.bridge_allcoation(emulator=emulator, logging=is_logging)
            
            super().__init__(regmap=reg_map, i2c_info=i2c_info, i2c_h=i2c, device=self.device, logging=is_logging, is_gui=is_logging)
            function.__init__(self, obj=self)
            parsing.__init__(self, obj=self)
    
    
    def close(self):
        
        super().close()  # call parent cleanup
        print("cleanup the class object")


    def __del__(self):
        print("class object destroyed")
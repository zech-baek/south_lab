# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib

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
from time import sleep as delay
import pyvisa as visa
import yaml, sys



class function:
    
    def __init__(self, protocol, channel):
        
        self._protocol = protocol
        self._channel  = channel
        # self._remote_sense = self._protocol.query(f"VOLT:SENS:SOUR? (@{self._channel})")
    
    
    @property
    def remote_sense(self):

        self._protocol.send(f"VOLT:SENS:SOUR EXT, (@{self._channel})")
        delay(0.5)
    

    @property
    def local_sense(self):

        self._protocol.send(f"VOLT:SENS:SOUR INT, (@{self._channel})")
        delay(0.5)
    
    
    @property
    def enable(self):
        
        self._protocol.send(f"OUTP ON, (@{self._channel})")
        delay(0.5)
    
    
    @property
    def disable(self):
        
        self._protocol.send(f"OUTP OFF, (@{self._channel})")
        delay(0.5)
    
    
    @property
    def iset(self):
        pass


    @iset.setter
    def iset(self, current):
        self._protocol.send(f"CURR:LEV {current}, (@{self._channel})")
    
    
    @property
    def vset(self):
        pass


    @vset.setter
    def vset(self, voltage):
        self._protocol.send(f"VOLT:LEV {voltage}, (@{self._channel})")
    
    
    @property
    def cfg_all(self):
        pass


    @cfg_all.setter
    def cfg_all(self, *args):
        
        len_args = len(args)
        if len_args == 1:
            self.vset = args[0][0]
            self.iset = args[0][1]
        else:
            log.forcedLog(f"configuration error, require voltage and current input (e.g. self.cfg_all = 5, 0.2)")
    
    
    @property
    def voltage(self):
        return  float(self._protocol.query(f"MEAS:VOLT? (@{self._channel})"))
    
    
    @property
    def current(self):
        return float(self._protocol.query(f"MEAS:CURR? (@{self._channel})"))


    @property
    def clear_protection(self):
        self._protocol.send(f"OUTP:PROT:CLE (@{self._channel})")



class keysight_N6705:
    
    def __init__(self, resource_name=None):
        
        log.initLogger(log.info)
        self.rm = visa.ResourceManager()

        if resource_name == None:

            with open(equipment_dir/"devices.yaml") as yaml_dev:
                power_supply_list = yaml.safe_load(yaml_dev)
            ps_id = power_supply_list["power_analyzer"]["keysight_n6705"]

            try:
                self.device = self.rm.open_resource(ps_id)
                self.__dict__["ch1"] = function(self, 1)
                self.__dict__["ch2"] = function(self, 2)
                log.forcedLog(f"initialized the keysight n6705 connection")
            except:
                log.errorLog(f"{color.bgred}failed to initialize n6705{color.end}")
        
        else:
            self.device = self.rm.open_resource(resource_name)
            self.__dict__["ch1"] = function(self, 1)
            self.__dict__["ch2"] = function(self, 2)
            log.forcedLog(f"initialized the keysight n6705 connection")
        
        self._offset = 0
        
        
    def send(self, command):
        self.device.write(command)
        
        
    def query(self, command):
        
        self.send(command)
        try:
            ret = self.device.read()
        except:
            ret = self.device.read()
        return ret
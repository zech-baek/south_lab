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
from time import sleep
from datetime import datetime
from tabulate import tabulate as tb

import vxi11
import pyvisa as visa
import cv2 as cv
import yaml
import getmac
import sys


def log_wrapping(header, message, is_logging=True):
    
    msg = f"[{header} {sys._getframe(2).f_code.co_name}] {message}"
    log.forcedLog(msg) if is_logging else log.debugLog(msg)



class function:
    
    def __init__(self, handler, channel):
        
        self.device  = handler
        self.channel = channel
        
        self.device.send(f":OUTPut{self.channel}:SYNC:STATe OFF") # external sync off
        self.device.send(f":OUTPut{self.channel}:VOLLimit:STATe OFF") # voltage limit off
        
        log_wrapping(self.__class__.__name__, f"__init__(), channel {self.channel}", self.device.logging)
        
        """
        source command for dg2502
        - sine : 1uHz to 50MHz
        - square : 1uHz to 15MHz
        - ramp : 1uHz to 1.5MHz
        - pulse : 1uHz to 15MHz
        - harmonic : 1uHz to 20MHz
        - noise (-3db) : 100MHz bandwidth
        - arbitrary : 1uHz to 15MHz
        - dual tone : 1uHz to 20MHz
        - PRBS : 2kbps to 40Mbps
        - rs232 : 9600, 14400, 19200, 38400, 57600, 115200, 128000, 230400
        - equence : 2k to 60MSa/s
        """
        scpi_group = {
            "polarity": {
                "cmd_1"  : "OUTPut",
                "cmd_2"  : "POLarity",
                "suffix" : ["NORMal", "INVerted"]
            },
            "state": {
                "cmd_1"  : "OUTPut",
                "cmd_2"  : "STATe",
                "suffix" : ["ON", "OFF"]
            }
        }
        
        for key in scpi_group.keys():
            method = key
            cmd_1  = scpi_group[key]["cmd_1"]
            cmd_2  = scpi_group[key]["cmd_2"]
            suffix = scpi_group[key]["suffix"]
            
            if suffix is not False:
                for option in suffix:
                    self._property_generator(method, cmd_1, cmd_2, option)
            else:
                self._property_generator(method, cmd_1, cmd_2, False)
    
    
    def _property_generator(self, method:str, cmd_1:str, cmd_2:str, suffix:str):
        
        def setter(instance=None):
            send_cmd = f":{cmd_1}{self.channel}:{cmd_2} {suffix}" if suffix else f":{cmd_1}{self.channel}:{cmd_2}"
            self.device.send(send_cmd)
            
            query_cmd = f":{cmd_1}{self.channel}:{cmd_2}?"
            log_wrapping(self.__class__.__name__, f"{method} : set {send_cmd}, return {self.device.query(query_cmd)}", self.device.logging)
        
        
        def getter(instance=None):
            pass
        
        property_name = f"{method}_{suffix}" if suffix else method
        setattr(self.__class__, property_name, property(setter, getter))
    
    
    @property
    def impedance(self):
        
        ret = self.device.query(f":OUTPut{self.channel}:IMPedance?")
        return int(float(ret))
        
    @impedance.setter
    def impedance(self, ohm):
        """
        - purpose : set the output impedance of the output connector of the specified channel
        - parameter : 1R to 10kR
        - default : 50R
        - hi-z : 9.9E+37
        """
        self.device.send(f":OUTPut{self.channel}:IMPedance {ohm}")
    
    
    @property
    def configuration(self):
        
        ret = self.device.query(f":SOURce{self.channel}:APPLy?").strip().strip('"')
        converted_ret = ret.split(",")
        header  = ["function", "frequency", "amplitude", "offset", "start phase"]
        tb_list = list()
        for n in converted_ret:
            try:
                tb_list.append(float(n))
            except:
                tb_list.append(n)
        print(tb([header, tb_list], headers="firstrow"))
    
    
    @property
    def source_harmonic(self):
        self.configuration
        
    @source_harmonic.setter
    def source_harmonic(self, *args):
        """
        parameter:
        - frequency : 1uHz to 25MHz
        - amplitude : 5Vpp
        - offset : depends on impedance and high limit
        - phase : 0 to 360
        """
        frequency = args[0][0]
        amplitude = args[0][1]
        offset    = args[0][2]
        phase     = args[0][3]
        self.device.send(f":SOURce{self.channel}:APPLy:HARMonic {frequency},{amplitude},{offset},{phase}")


    @property
    def source_noise(self):
        self.configuration
        
    @source_noise.setter
    def source_noise(self, *args):
        """
        parameter:
        - amplitude : 5Vpp
        - offset : depends on impedance and high limit
        """
        amplitude = args[0][0]
        offset    = args[0][1]
        self.device.send(f":SOURce{self.channel}:APPLy:NOISe {amplitude},{offset}")
    
    
    @property
    def source_prbs(self):
        self.configuration
        
    @source_prbs.setter
    def source_prbs(self, *args):
        """
        parameter:
        - frequency : 2kbps to 60Mbps
        - amplitude : 5Vpp
        - offset : depends on impedance and high limit
        """
        frequency = args[0][0]
        amplitude = args[0][1]
        offset    = args[0][2]
        self.device.send(f":SOURce{self.channel}:APPLy:PRBS {frequency},{amplitude},{offset}")
    
    
    @property
    def source_pulse(self):
        self.configuration
        
    @source_pulse.setter
    def source_pulse(self, *args):
        """
        parameter:
        - frequency : 1uHz to 25MHz
        - amplitude : 5Vpp
        - offset : depends on impedance and high limit
        - phase : 0 to 360
        - duty : 0.001 ~ 99.999
        """
        frequency = args[0][0]
        amplitude = args[0][1]
        offset    = args[0][2]
        phase     = args[0][3]
        duty      = args[0][4]
        self.device.send(f":SOURce{self.channel}:APPLy:PULSe {frequency},{amplitude},{offset},{phase}")
        self.device.send(f":SOURce{self.channel}:FUNCtion:PULSe:DCYCle {duty}")
    
    
    @property
    def source_ramp(self):
        self.configuration
        
    @source_ramp.setter
    def source_ramp(self, *args):
        """
        parameter:
        - frequency : 1uHz to 2MHz
        - amplitude : 5Vpp
        - offset : depends on impedance and high limit
        - phase : 0 to 360
        """
        frequency = args[0][0]
        amplitude = args[0][1]
        offset    = args[0][2]
        phase     = args[0][3]
        self.device.send(f":SOURce{self.channel}:APPLy:RAMP {frequency},{amplitude},{offset},{phase}")
    
    
    @property
    def source_sequence(self):
        self.configuration
        
    @source_sequence.setter
    def source_sequence(self, *args):
        """
        parameter:
        - frequency : 2kSa/s to 60MSa/s
        - amplitude : 5Vpp
        - offset : depends on impedance and high limit
        - phase : 0 to 360
        """
        frequency = args[0][0]
        amplitude = args[0][1]
        offset    = args[0][2]
        phase     = args[0][3]
        self.device.send(f":SOURce{self.channel}:APPLy:SEQuence {frequency},{amplitude},{offset},{phase}")
    
    
    @property
    def source_sinusoid(self):
        self.configuration
        
    @source_sinusoid.setter
    def source_sinusoid(self, *args):
        """
        parameter:
        - frequency : 1uHz to 100MHz
        - amplitude : 5Vpp
        - offset : depends on impedance and high limit
        - phase : 0 to 360
        """
        frequency = args[0][0]
        amplitude = args[0][1]
        offset    = args[0][2]
        phase     = args[0][3]
        self.device.send(f":SOURce{self.channel}:APPLy:SINusoid {frequency},{amplitude},{offset},{phase}")
    
    
    @property
    def source_square(self):
        self.configuration
        
    @source_square.setter
    def source_square(self, *args):
        """
        parameter:
        - frequency : 1uHz to 25MHz
        - amplitude : 5Vpp
        - offset : depends on impedance and high limit
        - phase : 0 to 360
        """
        frequency = args[0][0]
        amplitude = args[0][1]
        offset    = args[0][2]
        phase     = args[0][3]
        self.device.send(f":SOURce{self.channel}:APPLy:SQUare {frequency},{amplitude},{offset},{phase}")



class counter:
    
    def __init__(self, handler):
        
        self.device = handler
        
        log_wrapping(self.__class__.__name__, f"__init__()", self.device.logging)
        
        self.device.send(f":COUNter:AUTO")
        self.device.send(f":COUNter:SENSitive HIGh")
        self.device.send(f":COUNter:STATIstics:CLEAr")
        
        scpi_group = {
            "gatetime": {
                "send_cmd"  : f":COUNter:GATEtime",
                "query_cmd" : f":COUNter:GATEtime?",
                "suffix"    : ["USER1", "USER2", "USER3", "USER4", "USER5", "USER6"]
            },
            "coupling_dc": {
                "send_cmd"  : f":COUNter:COUPling DC",
                "query_cmd" : f":COUNter:COUPling?",
                "suffix"    : False
                },
            "coupling_ac": {
                "send_cmd"  : f":COUNter:COUPling AC",
                "query_cmd" : f":COUNter:COUPling?",
                "suffix"    : False
            },
            "hf_rejection": {
                "send_cmd"  : f":COUNter:HF",
                "query_cmd" : f":COUNter:HF?",
                "suffix"    : ["ON", "OFF"]
            }
        }
        
        for key in scpi_group.keys():
            method_name = key
            set_cmd     = scpi_group[key]["send_cmd"]
            query_cmd   = scpi_group[key]["query_cmd"]
            suffix      = scpi_group[key]["suffix"]
            
            if suffix is not False:
                for option in suffix:
                    self._property_generator(method_name, set_cmd, query_cmd, option)
            else:
                self._property_generator(method_name, set_cmd, query_cmd, suffix)
    
    
    def _property_generator(self, method_name, set_cmd, query_cmd, suffix):
        
        def setter(instance=None):
            if suffix is not False:
                self.device.send(f"{set_cmd}_{suffix}")
            else:
                self.device.send(set_cmd)
            log_wrapping(self.__class__.__name__, f"{method_name} : set {set_cmd}, return {self.device.query(query_cmd)}", self.device.logging)
            
        def getter(instance=None):
            # ret = self.device.query(query_cmd)
            # log_wrapping(self.__class__.__name__, f"{method_name} : get {query_cmd}, return {ret}", self.device.logging)
            # return ret
            pass
        
        if suffix is not False:
            setattr(self.__class__, f"{method_name}_{suffix}", property(setter))
        else:
            setattr(self.__class__, method_name, property(setter))
    
    
    @property
    def trigger_level(self):
        self.device.query(f":COUNter:LEVEl?")
        
    @trigger_level.setter
    def trigger_level(self, level):
        """
        - purpose : set the trigger level of the frequency counter
        - parameter : up to 1.5V
        """
        self.device.send(f":COUNter:LEVEl {level}")
    
    
    @property
    def measure(self):
        ret = self.device.query(f":COUNter:MEASure?").strip()
        header  = ["frequency", "period", "duty", "positive pulse width", "negative pulse width"]
        ret_list = list(map(float, ret.split(",")))
        print(tb([header, ret_list], headers="firstrow"))
        return ret_list



class ch1(function):
    
    def __init__(self, handler, channel):
        
        self.handler = handler
        self.channel = channel
        super().__init__(self.handler, self.channel)



class ch2(function):
    
    def __init__(self, handler, channel):
        
        self.handler = handler
        self.channel = channel
        super().__init__(self.handler, self.channel)



class rigol_dg2052(ch1, ch2, counter):
    
    def __init__(self, resource_name=None):
        
        self.logging = True
        self.rm      = visa.ResourceManager()
        
        if resource_name != None:
            self.dev = self.rm.open_resource(resource_name)
            log_wrapping(self.__class__.__name__, f"initialized connection with {resource_name}", self.logging)
            
        else:
            with open(equipment_dir/"devices.yaml") as yaml_dev:
                function_gen = yaml.safe_load(yaml_dev)["function_generator"]
            
            dg2052_id = function_gen["dg2052"]
            self.dev = self.rm.open_resource(dg2052_id)
        
        '''
        for channel_no in [1, 2]:
            function_instance = function(self, channel_no)
            function_instance.channel = channel_no
            self.__dict__[f"ch{channel_no}"] = function_instance
        '''
        
        # distinguish the class to use dynamic assign for the method
        self.__dict__[f"ch1"] = ch1(self, 1)
        self.__dict__[f"ch2"] = ch2(self, 2)
        
        self.__dict__["counter"] = counter(self)
        
        self.send(f":ROSCillator:SOURce INT") # use the internal oscillator
        self.send(f":DISPlay:BRIGhtness 90")
        self.send(f"*CLS")
    
    
    def send(self, command:str) -> None:
        
        self.dev.write(command)
        log_wrapping(self.__class__.__name__, f"send {command}", self.logging)
        
        
    def query(self, command:str) -> str:
        
        '''
        self.send(command)
        sleep(0.5)
        
        for n in range(3):
            try:
                ret = self.dev.read()
                log_wrapping(self.__class__.__name__, f"send {command}", self.logging)
                return ret
            except:
                log_wrapping(self.__class__.__name__, f"read error, retry {n+1}/3", self.logging)
                if n == 2:
                    self.send(f"*CLS")
        '''
        
        ret = self.dev.query(command)
        log_wrapping(self.__class__.__name__, f"send {command}", self.logging)
        return ret
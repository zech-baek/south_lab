# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib
import yaml
import pyvisa as visa
import serial
import threading
import serial.tools.list_ports

from interface.cui_logger import logger as log
from interface.cui_colors import color
from time import sleep

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



class sdl1030x:
    
    def __init__(self, resource=None) -> None:
        
        log.initLogger(log.info)
        self.rm = visa.ResourceManager()
        
        if resource is not None:
            
            try:
                self.device = self.rm.open_resource(resource)
                self.mode = None # VOTLAGE / CURRENT / RESISTANCE
                log.infoLog(f"initialized the e-loader connection")
            except:
                log.errorLog(f"{color.bgred}failed to initialize loader{color.end}")
                
        else:
            
            try:
                with open(equipment_dir/"devices.yaml") as yaml_dev:
                    devices = yaml.safe_load(yaml_dev)
                    
                loader_id = devices["e-loader"]["sdl1030x"]
                self.device = self.rm.open_resource(loader_id)
                self.mode = None # VOTLAGE / CURRENT / RESISTANCE
                log.infoLog(f"initialized the e-loader connection")
            except:
                log.errorLog(f"{color.bgred}failed to initialize loader{color.end}")
    
    
    @property
    def update_mode(self):
        
        ret = self.device.query(":SOUR:FUNC?").replace("\n", "")
        self.mode = ret
    
    
    def send(self, command):
        
        if self.mode is None:
            self.update_mode
        self.device.write(command)
    
    
    def read(self, command):
        
        if self.mode is None:
            self.update_mode
            
        ret = self.device.query(command)
        return ret
    
    
    @property
    def set_cc(self):
        
        self.send(":SOUR:FUNC CURR")
        self.send(":SOUR:CURR:IRANG 30")
        self.send(":SOUR:CURR:VRANG 36")
        self.update_mode
    
    
    @property
    def set_cv(self):
        
        self.send(":SOUR:FUNC VOLT")
        self.send(":SOUR:VOLT:IRANG 30")
        self.send(":SOUR:VOLT:VRANG 36")
        self.update_mode
    
    
    @property
    def set_cr(self):
        
        self.send(":SOUR:FUNC RES")
        self.send(":SOUR:RES:IRANG 30")
        self.send(":SOUR:RES:VRANG 36")
        self.update_mode
    
    
    @property
    def iset(self):
        
        ret = float(self.read(f":SOUR:CURR?"))
        log.forcedLog(f"current setting in cc mode : {ret}")
    
    
    @iset.setter
    def iset(self, current):
        
        if self.mode != "CURRENT":
            self.set_cc
        self.send(f":SOUR:CURR {current}")
    
    
    @property
    def vset(self):
        
        ret = float(self.read(":SOUR:VOLT?"))
        log.forcedLog(f"voltage setting in cv mode : {ret}")
    
    
    @vset.setter
    def vset(self, voltage):
        
        if self.mode != "VOLTAGE":
            self.set_cv
        self.send(f":SOUR:VOLT {voltage}")
    
    
    @property
    def rset(self):
        
        ret = float(self.read(":SOUR:VOLT?"))
        log.forcedLog(f"voltage setting in cv mode : {ret}")
    
    
    @rset.setter
    def rset(self, resistance):
        
        if self.mode != "RESISTANCE":
            self.set_cr
        self.send(f":SOUR:RES {resistance}")
    
    
    @property
    def enable(self):
        self.send(":SOUR:INP:STAT ON")
    
    
    @property
    def disable(self):
        self.send(":SOUR:INP:STAT OFF")
    
    
    @property
    def voltage(self):
        
        ret = float(self.read("MEAS:VOLT:DC?"))
        return ret
    
    
    @property
    def current(self):
        
        ret = float(self.read("MEAS:CURR:DC?"))
        return ret
    
    
    @property
    def resistance(self):
        
        ret = float(self.read("MEAS:RES:DC?"))
        return ret
    
    
    @property
    def power_recycle(self):
        
        self.disable
        sleep(2)
        self.enable
        sleep(1)


class gwinstek_pel3021(serial.Serial):
    
    def __init__(self, resource=None):
        
        log.initLogger(log.info)
        
        if resource is None:
            comport_list = [comport.device for comport in serial.tools.list_ports.comports()]
            resource = comport_list[0]
            log.infoLog(f"returned list of the com ports {comport_list}")
            
        serial.Serial.__init__(self, port=resource, baudrate=9600, timeout=10)
        
        # clean the buffer
        if "No error" not in self.query(":SYST:ERR?"):
            self.send("*CLS")

        self.send(":MODE:CRAN HIGH")
        self.send(":MODE:VRAN HIGH")
        self.reset_input_buffer()
        self.reset_output_buffer()
        
        self.disable
        


    def send(self, command):
        self.write((command + "\n").encode("ascii"))
    
    
    def query(self, command):
        
        self.send(command)
        try:
            ret = self.readline().decode("utf-8")
        except:
            log.infoLog(f"[pel3021] read error, retry reading")
            ret = self.readline().decode("utf-8")
        return ret
        
        
    @property
    def cc_mode(self):
        self.send(":MODE CC")
    
    
    @property
    def cv_mode(self):
        self.send(":MODE CV")
    
    
    @property
    def cr_mode(self):
        
        self.send(":MODE CR")
        self.send(":CRU OHM")
    
    
    @property
    def iset(self):
        
        ret = self.query(f":CURR:VA?")
        return ret


    @iset.setter
    def iset(self, current):
        self.send(f":CURR:VA {current}")
    
    
    @property
    def vset(self):

        ret = self.query(f":VOLT:VA?")
        return ret


    @vset.setter
    def vset(self, voltage):

        self.send(f":VOLT:VA {voltage}")
    
    
    @property
    def voltage(self):
        
        ret = self.query("MEAS:VOLT:DC?")
        return float(ret)
    
    
    @property
    def current(self):
        
        ret = self.query("MEAS:CURR:DC?")
        return float(ret)

    
    @property
    def disable(self):
        self.send(":INP OFF")
    
    
    @property
    def enable(self):
        self.send(":INP ON")
    
    
    @property
    def power_recycle(self):
        
        self.disable
        sleep(2)
        self.enable
        sleep(1)



class it8511a_cc:

    def __init__(self, handler):
        
        self.handler = handler
    

    @property
    def set_cc(self):
        self.handler.send("SOUR:MODE CURR")

    
    @property
    def mode_check(self):

        if self.handler.mode != "CURRent":
            self.set_cc
        self.handler.mode = self.handler.query("SOUR:MODE?")
    

    @property
    def iset(self):
        
        ret = float(self.handler.query("SOUR:CURR:LEVEL?"))
        return ret


    @iset.setter
    def iset(self, current):

        self.mode_check
        self.handler.send(f"SOUR:CURR:LEVEL {current}")
        

    @property
    def set_islew_rise(self):

        '''
        slew rate : A/us
        min : 0.001
        max : 3
        '''
        
        ret = float(self.handler.query(f"CURR:SLEW?"))
        return ret


    @set_islew_rise.setter
    def set_islew_rise(self, slew):

        self.mode_check
        self.handler.send(f"CURR:SLEW {slew}")


    @property
    def set_islew_fall(self):

        '''
        slew rate : A/us
        '''
        
        ret = float(self.handler.query(f"SOURCE:CURRENT:SLEW:FALL?"))
        return ret


    @set_islew_fall.setter
    def set_islew_fall(self, slew):

        self.mode_check
        self.handler.send(f"SOURCE:CURRENT:SLEW:FALL {slew}")
    

    @property
    def set_iprot(self):

        '''
        protection level unit : A
        '''
        
        ret = float(self.handler.query(f"SOURCE:CURRENT:PROTECTION?"))
        return ret


    @set_iprot.setter
    def set_iprot(self, slew):

        self.mode_check
        self.handler.send(f"SOURCE:CURRENT:PROTECTION {slew}")


class it8511a_cr:

    def __init__(self, handler):
        
        self.handler = handler
    

    @property
    def set_cr(self):
        self.handler.send("SOUR:MODE RES")

    
    @property
    def mode_check(self):

        if self.handler.mode != "RESistance":
            self.set_cr
        self.handler.mode = self.handler.query("SOUR:MODE?")
    

    @property
    def rset(self):
        
        ret = float(self.handler.query("SOUR:RES:LEVEL?"))
        return ret


    @rset.setter
    def rset(self, voltage):

        self.mode_check
        self.handler.send(f"SOUR:RES:LEVEL {voltage}")


class it8511a_cv:

    def __init__(self, handler):
        
        self.handler = handler
    

    @property
    def set_cv(self):
        self.handler.send("SOUR:MODE VOLT")

    
    @property
    def mode_check(self):

        if self.handler.mode != "VOLTage":
            self.set_cv
        self.handler.mode = self.handler.query("SOUR:MODE?")
    

    @property
    def vset(self):
        
        ret = float(self.handler.query("SOUR:VOLT:LEVEL?"))
        return ret


    @vset.setter
    def vset(self, voltage):

        self.mode_check
        self.handler.send(f"SOUR:VOLT:LEVEL {voltage}")


class it8511a(serial.Serial, it8511a_cc, it8511a_cv, it8511a_cr):
    
    def __init__(self, resource:int=None):
        
        log.initLogger(log.info)
        
        if resource is None:
            comport_list = [comport.device for comport in serial.tools.list_ports.comports()]
            resource = comport_list[0]
            log.infoLog(f"returned list of the com ports {comport_list}")
        else:
            try:
                serial.Serial.__init__(self, port=f"COM{resource}", baudrate=9600, timeout=5)
                super().__dict__["cc"] = it8511a_cc(self)
                super().__dict__["cv"] = it8511a_cv(self)
                super().__dict__["cr"] = it8511a_cr(self)

                log.forcedLog(f"initialized the it8511a connection to {resource}")
                self.remote_mode
                self.send("*CLS")
                self.disable

                # CURRent, VOLTage, RESistance
                self.mode = self.query("SOUR:MODE?").strip()
            except:
                log.errorLog(f"{color.bgred}failed to initialize it8511a{color.end}")


    def send(self, command):
        self.write((command + "\n").encode("ascii"))
    
    
    def query(self, command):
        
        self.send(command)
        try:
            ret = self.readline().decode("utf-8")
        except:
            log.infoLog(f"[it8511a] read error, retry reading")
            ret = self.readline().decode("utf-8")
        return ret
    

    @property
    def remote_mode(self):
        self.send("SYSTEM:REMOTE")
    

    @property
    def local_mode(self):
        self.send("SYSTEM:LOCAL")

    
    @property
    def disable(self):
        self.send("SOURCE:INPUT OFF")
    
    
    @property
    def enable(self):
        self.send("SOURCE:INPUT ON")
    
    
    @property
    def power_recycle(self):
        
        self.disable
        sleep(1)
        self.enable
        sleep(0.5)
    

    @property
    def short_on(self):

        self.send("INP:SHORT 1")
        self.enable
    

    @property
    def short_off(self):

        self.send("INP:SHORT 0")
        self.disable


    @property
    def voltage(self):
        
        ret = self.query("MEAS:VOLT:DC?")
        return float(ret)
    
    
    @property
    def current(self):

        ret = self.query("MEASURE:CURRENT:DC?")
        return float(ret)
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
# import vxi11
import pyvisa as visa
import yaml, sys


class function_siglent:
    
    @property
    def voltage(self):
        
        ret = float(self.read("MEASure:VOLTage? CH1"))
        return ret
    
    
    @property
    def current(self):
        
        ret = float(self.read("MEASure:CURRent? CH1"))
        return ret
    
    
    @property
    def cfg_all(self):

        volt = self.vset
        curr = self.iset
        log.forcedLog(f"configured voltage is {volt}")
        log.forcedLog(f"configured current is {curr}")


    @cfg_all.setter
    def cfg_all(self, *args):
        
        for tup in args:
            len_args = len(args)
            if len_args == 1:
                self.vset = tup[0]
                self.iset = tup[1]
            else:
                log.forcedLog(f"configuration error, require voltage and current input (e.g. self.cfg_all = 5, 0.2)")
        
    
    @property
    def iset(self):

        ret = self.read("CURRent?")
        return ret
    

    @iset.setter
    def iset(self, curr):
        
        self.send(f"CH1:CURRent {curr}")
        # log.infoLog(f"set the current to {curr}")
    
    
    @property
    def vset(self):

        ret = self.read("VOLTage?")
        return ret
    

    @vset.setter
    def vset(self, volt):
        
        self.send(f"CH1:VOLTage {volt}")
        # log.infoLog(f"set the voltage to {volt}")
    
    
    @property
    def disable(self):
        self.send("OUTP CH1,OFF")
    
    
    @property
    def enable(self):
        self.send("OUTP CH1,ON")
    

    @property
    def power_recycle(self):

        self.disable
        delay(2)
        self.enable
        delay(1)

'''
class siglent_spd1168x_tcp(vxi11.Instrument, function_siglent):
    
    def __init__(self, resource_name=None, **kwargs):
        
        try:
            # power_analyzer.__init__(self,**kwargs)
            vxi11.Instrument.__init__(self, resource_name)
            
            self.send("INSTrument CH1")
            # log.infoLog(f"[spd1168x] selected channel is {self.query('INSTrument?')}")
        except:
            log.errorLog(f"failed to initialize spd1168x")
        
        
    def send(self, command):
        self.write(command)
'''        


class siglent_spd1168x_usb(function_siglent):
    
    '''
    Siglent SPD1168X
    - single channel power supply
    '''
    
    def __init__(self, resource_name=None, **kwargs):
        
        self.rm = visa.ResourceManager()
        
        if resource_name is not None:
            try:
                self.device = self.rm.open_resource(resource_name)
                # self.device = usbtmc.Instrument(resource_name)
            
                self.send("INSTrument CH1")
                # log.infoLog(f"[spd1168x] selected channel is {self.read('INSTrument?')}")
            except:
                log.errorLog(f"failed to initialize spd1168x")
        else:
            log.infoLog("resource name is required to initialization")

        
    def send(self, command):
        self.device.write(command)
        
        
    def read(self, command):
        
        '''
        self.send(command)
        try:
            ret = self.device.read()
        except:
            log.infoLog(f"[spd1168x] read error, retry reading")
            ret = self.device.read()
        '''
        
        ret = self.device.query(command)
        return ret
    
    
class siglent_spd1305x_usb(function_siglent):
    
    def __init__(self, resource_name=None):
        
        self.rm = visa.ResourceManager()
    
        if resource_name is not None:
            try:
                self.device = self.rm.open_resource(resource_name)
                # self.device = usbtmc.Instrument(resource_name)
                # log.infoLog("[spd1305] connection is initialized")
            except:
                log.errorLog(f"failed to initialize spd1168x")
        else:
            log.errorLog(f"{color.bgred}resource name is required to initialization{color.end}")
    
    
    def send(self, command):
        self.device.write(command)
        
    
    def read(self, command):
        
        '''
        self.send(command)
        try:
            ret = self.device.read()
        except:
            log.infoLog(f"[spd1305x] read error, retry reading")
            ret = self.device.read()
        '''
        ret = self.device.query(command)
        return ret
    
    
class function_rigol:
    
    def __init__(self, protocol, channel):

        self._protocol = protocol
        self._channel  = channel
        self._offset = 0
        

    def send(self, command):
        self._protocol.write(command)
        
        
    def query(self, command):
        
        self.send(command)
        try:
            ret = self._protocol.read()
        except:
            ret = self._protocol.read()
        return ret
    
    
    @property
    def set_offset(self):

        ret = self._offset
        return ret
    

    @set_offset.setter
    def set_offset(self, offset):
        
        self._offset = offset
        
        
    @property
    def voltage(self):
        
        ret = float(self.query(f":MEASure:VOLTage:DC? CH{self._channel}"))
        return ret
    
    
    @property
    def current(self):
        
        ret = float(self.query(f"MEASure:CURRent? CH{self._channel}"))
        return ret
    
    
    @property
    def cfg_all(self):

        volt = self.vset
        curr = self.iset
        log.forcedLog(f"configured voltage is {volt}")
        log.forcedLog(f"configured current is {curr}")


    @cfg_all.setter
    def cfg_all(self, *args):
        
        len_args = len(args)
        if len_args == 1:
            self.vset = args[0][0]
            self.iset = args[0][1]
        else:
            log.forcedLog(f"configuration error, require voltage and current input (e.g. self.cfg_all = 5, 0.2)")

    
    @property
    def iset(self):

        ret = self.query(f":SOUR{self._channel}:CURR?")
        return ret
    

    @iset.setter
    def iset(self, curr):
        
        self.send(f":SOUR{self._channel}:CURR {curr}")
        # log.infoLog(f"set the current to {curr}")
    
    
    @property
    def vset(self):
        
        ret = self.query(f":SOUR{self._channel}:VOLT?")
        return ret


    @vset.setter
    def vset(self, volt):
        
        target_voltage = volt + self._offset
        self.send(f":SOUR{self._channel}:VOLT {target_voltage}")
        # log.infoLog(f"set the voltage to {volt}")
    
    
    @property
    def disable(self):
        self.send(f":OUTP CH{self._channel},OFF")
    
    
    @property
    def enable(self):
        self.send(f":OUTP CH{self._channel},ON")
    

    @property
    def power_recycle(self):

        self.disable
        delay(2)
        self.enable
        delay(1)
        
        
class rigol_dp821a:
    
    def __init__(self, resource_name=None):
        
        log.initLogger(log.info)
        self.rm = visa.ResourceManager()
        
        try:
            with open(equipment_dir/"devices.yaml") as yaml_dev:
                power_supply_list = yaml.safe_load(yaml_dev)
                    
            ps_id = power_supply_list["power_supply"]["rigol_dp821a"]
            self.device = self.rm.open_resource(ps_id)
            for ch in [1, 2]:
                self.__dict__[f"ch{ch}"] = function_rigol(self.device, ch)
                log.forcedLog(f"initialized the rigol dp821a connection and assign channel {ch}")
                
        except:
            log.errorLog(f"{color.bgred}failed to initialize rigol dp821a{color.end}")
        
    
    def send(self, command):
        self.device.write(command)
        
        
    def query(self, command):
        
        self.send(command)
        try:
            ret = self.device.read()
        except:
            ret = self.device.read()
        return ret
    
    
    @property
    def IDN(self) :
        self.device.write("*IDN?")
        ret = self.device.read()
        log.infoLog(ret)
        return ret


class rigol_dp811a:
    
    def __init__(self, resource_name):
        
        rm = visa.ResourceManager()
        
        try:
            self.device = rm.open_resource(resource_name)
            # self.device = usbtmc.Instrument(resource_name)
            self._offset = 0
        except:
            log.errorLog(f"{color.bgred}failed to initialize spd1168x{color.end}")
    
    
    def send(self, command):
        self.device.write(command)
        
        
    def query(self, command):
        
        self.send(command)
        try:
            ret = self.device.read()
        except:
            ret = self.device.read()
        return ret
    
    
    '''
    def set_current(self, curr):
        
        self.send(f":SOUR:CURR {curr}")
        # log.infoLog(f"set the current to {curr}")
    
    
    def set_voltage(self, volt):
        
        target_voltage = volt + self._offset
        self.send(f":SOUR:VOLT {target_voltage}")
        # log.infoLog(f"set the voltage to {volt}")
    '''


    @property
    def voltage(self):

        ret = self.query(":MEASURE:VOLTAGE:DC?")
        return float(ret)


    @property
    def current(self):

        ret = self.query(":MEASURE:CURRENT:DC?")
        return float(ret)


    @property
    def iset(self):

        ret = self.query(f":SOUR:CURR?")
        return ret
    

    @iset.setter
    def iset(self, curr):
        
        self.send(f":SOUR:CURR {curr}")
        # log.infoLog(f"set the current to {curr}")
    
    
    @property
    def vset(self):
        
        ret = self.query(f":SOUR:VOLT?")
        return ret


    @vset.setter
    def vset(self, volt):
        
        target_voltage = volt + self._offset
        self.send(f":SOUR:VOLT {target_voltage}")
        # log.infoLog(f"set the voltage to {volt}")
    

    @property
    def cfg_all(self):

        volt = self.vset
        curr = self.iset
        log.forcedLog(f"configured voltage is {volt}")
        log.forcedLog(f"configured current is {curr}")


    @cfg_all.setter
    def cfg_all(self, *args):
        
        for tup in args:
            len_args = len(args)
            if len_args == 1:
                self.vset = tup[0]
                self.iset = tup[1]
            else:
                log.forcedLog(f"configuration error, require voltage and current input (e.g. self.cfg_all = 5, 0.2)")
    
    
    @property
    def disable(self):
        self.send(f":OUTP OFF")
    
    
    @property
    def enable(self):
        self.send(f":OUTP ON")
    

    @property
    def power_recycle(self):

        self.disable
        delay(2)
        self.enable
        delay(1)


class ps_auto:

    '''
    Class for auto-connection with the multi power supply environment
    - usage
        self.rg821.ch1 & ch2
        self.rg811
        self.s1168
        self.s1305
    '''

    def __init__(self):
        
        # log.initLogger(log.info)
        
        with open(equipment_dir/"devices.yaml") as yaml_dev:
            power_supply_list = yaml.safe_load(yaml_dev)
        
        ps_id = dict(power_supply_list["power_supply"].items())
        self.rm = visa.ResourceManager()
        ret_devices = list(self.rm.list_resources())
        # ret_devices = usbtmc.list_devices()

        for device in ret_devices:
            for k, (bus_id, alias) in ps_id.items():

                if bus_id in device:
                    if "spd1168x" in k:
                        try:
                            setattr(self, alias, siglent_spd1168x_usb(device))
                            # log.forcedLog(f"connected to {alias} {device} {bus_id}")
                        except:
                            log.forcedLog(f"connection error : {alias} {device} {bus_id}")
                    if "spd1305" in k:
                        try:
                            setattr(self, alias, siglent_spd1305x_usb(device))
                            # log.forcedLog(f"connected to {alias} {device} {bus_id}")
                        except:
                            log.forcedLog(f"connection error : {alias} {device} {bus_id}")
                    if "dp821" in k:
                        try:
                            setattr(self, alias, rigol_dp821a(device))
                            # log.forcedLog(f"connected to {alias} {device} {bus_id}")
                        except:
                            log.forcedLog(f"connection error : {alias} {device} {bus_id}")
                    if "dp811" in k:
                        try:
                            setattr(self, alias, rigol_dp811a(device))
                            # log.forcedLog(f"connected to {alias} {device} {bus_id}")
                        except:
                            log.forcedLog(f"connection error : {alias} {device} {bus_id}")

                    log.infoLog(f"initialized the power supply connection and assign ps.{alias}")


class rigol_auto:
    
    '''
    class for assign the rigol power supply to channels
    - usage
        self.ch1
        self.ch2
    '''
    
    def __init__(self) -> None:
        
        with open(equipment_dir/"devices.yaml") as yaml_dev:
            dmm_list = yaml.safe_load(yaml_dev)
            
        usb_id = dict(dmm_list["power_supply"]["rigol_dp811a"].items()) 
        
        rm = visa.ResourceManager()
        ret_devices = list(rm.list_resources())
        
        for device in ret_devices:
            # log.infoLog(f"visa resource : {device}")
            for k, v in usb_id.items():
                if device == v:
                    super().__dict__[k] = rigol_dp811a(v)
                    log.forcedLog(f"initialized connection with {v}")
    
    
class keithley_2470:
    
    def __init__(self, resource_name=None):
        
        # log.initLogger(log.info)
        
        rm = visa.ResourceManager()

        if resource_name == None:

            with open(equipment_dir/"devices.yaml") as yaml_dev:
                power_supply_list = yaml.safe_load(yaml_dev)
            bus_id = power_supply_list["source_meter"]["keithley_2470"]
            
            try:
                self.device = rm.open_resource(bus_id)
                log.forcedLog(f"initialized the 2470 source meter")
                self.init_property()
            except:
                log.errorLog(f"{color.bgred}failed to initialize 2470{color.end}")
                
        else:
            self.device = rm.open_resource(resource_name)
            self.init_property()
        
    
    def init_property(self):
        
        self.send("SOURce:FUNCtion VOLT")
        self.send("SOURce:VOLTage:RANGe 20")
        self.send('SENSe:FUNCtion "CURR"')
        self.send("SENS:CURR:RANG:AUTO ON")
        self.send(":OUTP:CURR:SMOD HIMP")
        self.send("COUN 10")

        self.voltage_cfg = 0
        self.current_cfg = 0
        
        self.c_range = ["10E-9", "100E-9", "1E-6", "10E-6", "100E-6", "1E-3", "10E-3", "100E-3", "1"]
        self.v_range = ["2E-1", "2", "20", "200", "1000"]
        self.create_property("current_range", self.c_range)
        self.create_property("voltage_range", self.v_range)
    
    
    def create_property(self, prefix, config_list):

        for cfg in config_list:
            setattr(self.__class__, f"{prefix}_{cfg.replace('-', '_')}", property(lambda self, cfg=cfg: getattr(self, prefix)(cfg)))    
            
            
    def current_range(self, cfg):
        self.send(f"SENS:CURR:RANG {cfg}")
    
    
    def voltage_range(self, cfg):
        self.send(f"SOUR:VOLT:RANG {cfg}")
    
    
    def send(self, command):
        self.device.write(command)
        
        
    def query(self, command):
        
        self.send(command)
        try:
            ret = self.device.read()
        except:
            ret = self.device.read()
        return ret
    
    
    @property
    def disable(self):
        self.send(f"OUTP:STAT OFF")
    
    
    @property
    def enable(self):
        self.send(f"OUTP:STAT ON")
    

    @property
    def power_recycle(self):

        self.disable
        delay(2)
        self.enable
        delay(1)
    

    @property
    def set_4wire(self):
        self.send("SENS:CURR:RSEN ON")
    

    @property
    def set_2wire(self):
        self.send("SENS:CURR:RSEN OFF")
    
    
    def compare_range(self, value, cfg):
        
        float_cfg = [float(value) for value in cfg]
        ret = None
        
        for compare in float_cfg:
            if compare > value:
                if (ret is None) or (compare < ret):
                    ret = compare
        
        return ret
    
    
    @property
    def vset(self):
        
        ret = self.query(f"SOUR:VOLT?")
        return ret
    
    @vset.setter
    def vset(self, volt):
        
        # ret = self.compare_range(volt, self.v_range)
        self.voltage_range(cfg=volt)
        self.voltage_cfg = volt
        self.send(f"SOUR:VOLT {volt}")
    

    @property
    def iset(self):
        
        ret = self.query(f"SOUR:VOLT:ILIM?")
        return ret
    

    @iset.setter
    def iset(self, lim):
        
        # ret = self.compare_range(lim, self.c_range)
        self.current_range(cfg=lim)
        
        '''
        if lim > 0.74:
            self.send(f"SENS:CURR:RANG {7}")
        elif lim < 0.01:
            self.send(f"SENS:CURR:RANG {1e-2}")
        else:
            self.send(f"SENS:CURR:RANG {1}")
        '''
        
        self.current_cfg = lim
        self.send(f"SOUR:VOLT:ILIM {lim}")
        
    @property
    def cfg_all(self):
        
        volt = self.vset
        curr = self.iset
        log.forcedLog(f"configured value : {volt}V, {curr}A")
        
        
    @cfg_all.setter
    def cfg_all(self, *args):
        
        for tup in args:
            len_args = len(args)
            if len_args == 1:
                self.vset = tup[0]
                self.iset = tup[1]
            else:
                log.forcedLog(f"configuration error, require voltage and current input (e.g. self.cfg_all = 5, 0.2)")
    

    @property
    def voltage(self):

        self.send("TRAC:CLEAR")
        self.send("TRAC:TRIG")
        # for _ in range(2):
        ret_list = self.query("TRAC:DATA? 1, 5, 'defbuffer1', SOUR")
        string_list = ret_list.split(",")
        float_list = [float(num.strip()) for num in string_list]
        average = sum(float_list) / len(float_list)

        return average
    

    @property
    def current(self):

        self.send("TRAC:CLEAR")
        # for _ in range(3):
        ret = self.query("READ?")
        return float(ret)


class keysight_e36232a:
    
    def __init__(self, resource_name=None):
        
        log.initLogger(log.info)
        self.rm = visa.ResourceManager()
        
        try:
            with open(equipment_dir/"devices.yaml") as yaml_dev:
                power_supply_list = yaml.safe_load(yaml_dev)
                    
            ps_id = power_supply_list["power_supply"]["keysight_e36232a"]
            self.device = self.rm.open_resource(ps_id)
            log.forcedLog(f"initialized the keysight e36232a connection")
                
        except:
            log.errorLog(f"{color.bgred}failed to initialize keysight e36232a{color.end}")
        
    
    def send(self, command):
        self.device.write(command)
        
        
    def query(self, command):
        
        self.send(command)
        try:
            ret = self.device.read()
        except:
            ret = self.device.read()
        return ret
    
    
    @property
    def IDN(self) :
        self.device.write("*IDN?")
        ret = self.device.read()
        log.infoLog(ret)
    
    @property
    def voltage(self):
        
        ret = float(self.query(f"MEAS:VOLT?"))
        return ret
    
    
    @property
    def current(self):
        
        ret = float(self.query(f"MEAS:CURR?"))
        return ret
    
    
    @property
    def cfg_all(self):

        volt = self.vset
        curr = self.iset
        log.forcedLog(f"configured voltage is {volt}")
        log.forcedLog(f"configured current is {curr}")


    @cfg_all.setter
    def cfg_all(self, *args):
        
        len_args = len(args)
        if len_args == 1:
            self.vset = args[0][0]
            self.iset = args[0][1]
        else:
            log.forcedLog(f"configuration error, require voltage and current input (e.g. self.cfg_all = 5, 0.2)")

    
    @property
    def iset(self):

        ret = self.query(f"SOUR:CURR?")
        return ret
    

    @iset.setter
    def iset(self, curr):
        
        self.send(f"SOUR:CURR {curr}")
        # log.infoLog(f"set the current to {curr}")
    
    
    @property
    def vset(self):
        
        ret = self.query(f"SOUR:VOLT?")
        return ret


    @vset.setter
    def vset(self, volt):
        
        self.send(f"SOUR:VOLT {volt}")
        # log.infoLog(f"set the voltage to {volt}")
    
    
    @property
    def disable(self):
        self.send(f"OUTP 0")
    
    
    @property
    def enable(self):
        self.send(f"OUTP 1")
    

    @property
    def power_recycle(self):

        self.disable
        delay(2)
        self.enable
        delay(1)
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
import serial
import pyvisa as visa
import yaml



class function:
    
    def get_average(self, list_data):
        
        string_list = list_data.split(",")
        float_list = [float(num.strip()) for num in string_list]
        average = sum(float_list) / len(float_list)
        
        return average
    
    
    @property
    def set_sampling(self):
        
        ret = self.read("SAMP:COUN?")
        log.forcedLog(f"sampling count : {ret}")
        
    
    @set_sampling.setter
    def set_sampling(self, cfg):
        
        t_spl = 200 # 0.2 second per 1 sample
        self.sampling = cfg
        self.send(f"SAMP:COUN {self.sampling}")
        self.device.timeout = t_spl * cfg * 2
    
    
    @property
    def set_nplc(self):
        
        i_nplc = self.read("CURR:DC:NPLC?")
        v_nplc = self.read("VOLT:DC:NPLC?")
        log.forcedLog(f"volt:nplc={v_nplc}")
        log.forcedLog(f"curr:nplc={i_nplc}")
    
    
    @set_nplc.setter
    def set_nplc(self, cfg):
        
        self.nplc = cfg
        self.send(f"CURR:DC:NPLC {self.nplc}")
        self.send(f"VOLT:DC:NPLC {self.nplc}") # option 1, 10, 100, 0.5
    
    
    def current(self, cfg):
        
        self.mode = "current"
        
        if cfg == "auto":
            if (self.mode != "current") or (self.rang != "auto") or (self.cparm != "auto"):
                self.rang = "auto"
                self.cparm = "auto"
                self.send("CONF:CURR:DC AUTO")
        elif cfg == "classic":
            if (self.mode != "current") or (self.rang != "auto" or (self.cparm != "auto")):
                self.mode = "current"
                self.rang = "auto"
                self.cparm = "auto"
                self.send(f"CONF:CURR:DC AUTO")
            ret = self.read("MEAS:CURR:DC?")
            return float(ret) 
        else:
            if (self.mode != "current") or (self.rang != "fixed" or (self.cparm != cfg)):
                self.rang = "fixed"
                self.cparm = cfg
                self.send(f"CONF:CURR:DC {cfg}")        
                self.send(f"CURR:DC:NPLC {self.nplc}")
                self.send(f"SAMP:COUN {self.sampling}")
                
        self.send("CALC:AVER:STAT ON")
        self.send("INIT")
        delay(0.1)
        ret = self.read("FETC?")
        # ret = self.read("READ?")
        average_ret = self.get_average(list_data=ret)
        return average_ret
    
    
    def voltage(self, cfg):
        
        self.mode = "voltage"
        
        if cfg == "auto":
            if (self.rang != "auto") or (self.vparm != None):
                self.rang = "auto"
                self.vparm = None
                self.send("CONF:VOLT:DC AUTO")
                self.send(f"VOLT:DC:NPLC {self.nplc}") # option 1, 10, 100, 0.3
                self.send(f"SAMP:COUN {self.sampling}")
        elif cfg == "hiz":            
            if (self.rang != "hiz") or (self.vparm != "hiz"):
                self.rang = "hiz"
                self.vparm = "hiz"
                self.send("VOLT:DC:RANG 2V")
                self.send("VOLT:DC:IMP 10G")
                self.send(f"VOLT:DC:NPLC {self.nplc}") # option 1, 10, 100, 0.3
                self.send(f"SAMP:COUN {self.sampling}")
        elif cfg =="classic":
            if (self.rang != "auto") or (self.vparm != "auto"):
                self.rang = "auto"
                self.vparm = "auto"
                self.send(f"CONF:VOLT:DC AUTO")
                self.send(f"VOLT:DC:NPLC {self.nplc}") # option 1, 10, 100, 0.3
                self.send(f"SAMP:COUN {self.sampling}")
            ret = self.read("MEAS:VOLT:DC?")
            return float(ret)
        else:
            if (self.rang != "fixed") or (self.vparm != cfg):
                self.rang = "fixed"
                self.vparm = cfg
                self.send(f"CONF:VOLT:DC {cfg}")
                self.send(f"VOLT:DC:NPLC {self.nplc}") # option 1, 10, 100, 0.3
                self.send(f"SAMP:COUN {self.sampling}")
        
        self.send("CALC:AVER:STAT ON")
        self.send("INIT")
        ret = self.read("FETC?")
        # ret = self.read("READ?")
        average_ret = self.get_average(list_data=ret)
        return average_ret
    
    
    @property
    def resistance(self):
        
        if self.mode != "resistance":
            self.mode  = "resistance"
            self.rang  = None
            self.vparm = None
            self.cparm = None
            self.send("CONF:RES AUTO")
            
        # ret = self.read("MEAS:RES?")
        ret = self.read("READ?")
        
        return float(ret)

    
    @property
    def diode(self):
        
        if self.mode != "diode":
            self.mode  = "diode"
            self.rang  = None
            self.vparm = None
            self.cparm = None
            self.send("CONFigure:DIODe")
            
        ret = self.read("READ?")
        
        return float(ret)


    @property
    def frequency(self):
        
        if self.mode != "frequency":
            self.mode = "frequency"
            self.rang = None
            self.send("CONF:FREQ")
            self.send(f"SAMP:COUN 1")
            self.device.timeout = 5000
            delay(1)    
        
        ret = self.read("READ?").split(",")[0]
        # ret = self.read("MEAS:FREQ?")
        return float(ret)
    
    
    @property
    def frequency_classic(self):
        
        ret = self.read("MEAS:FREQ?")
        return float(ret)
    
    
    @property
    def temp_mode(self):
        
        self.send("CONF:TEMP THER,KITS90")
        
    @property
    def temperature(self):
        
        ret = self.read("MEAS:TEMP? THER,KITS90")
        return float(ret)
    
    
    def create_property(self, prefix, config_list):

        for cfg in config_list:
            setattr(self.__class__, f"{prefix}_{cfg}", property(lambda self, cfg=cfg: getattr(self, prefix)(cfg)))


class multi_dmm(function):
    
    def __init__(self, rm, resource_name):
        
        self.device = rm.open_resource(resource_name)
        
        self.device.timeout = 5000 # 5seconds
        self.sampling = 5
        self.nplc = 1
        
        self.set_nplc = self.nplc
        self.set_sampling = self.sampling
        
        self.mode  = None
        self.rang  = None
        self.vparm = None
        self.cparm = None

        current_range = ["200uA", "2mA", "20mA", "200mA", "2A", "10A", "auto"]
        voltage_range = ["200mV", "2V", "20V", "200V", "1000V", "auto", "hiz"]

        self.create_property("voltage", voltage_range)
        self.create_property("current", current_range)
        
    '''
    def create_property(self, prefix, config_list):

        for cfg in config_list:
            setattr(self.__class__, f"{prefix}_{cfg}", property(lambda self, cfg=cfg: getattr(self, prefix)(cfg)))
    '''
    
    
    def read(self, command):
        
        self.send(command)
        # delay(0.2)
        try:
            ret = self.device.read()
        except:
            log.errorLog(f"[dmm] read error, retry reading")
            ret = self.device.read()
            log.errorLog(f"[dmm] retry, return {ret}")
        return ret
    
    
    def send(self, command):
        self.device.write(command)


class siglent_sdm3055_auto(multi_dmm):
    
    '''
    Siglent SDM3055
    - assign the device after searching the USB resources
    - USB interface
    '''
    
    def __init__(self):
        
        log.initLogger(log.info)
        
        with open(equipment_dir/"devices.yaml") as yaml_dev:
            dmm_list = yaml.safe_load(yaml_dev)
        
        usb_id = dict(dmm_list["digital_multimeter"]["siglent_sdm3055"].items())
        
        rm = visa.ResourceManager()
        ret_devices = list(rm.list_resources())
        
        # ret_devices = usbtmc.list_devices()
        # log.infoLog("[info] SDM3055 Current range : 200uA, 2mA, 20mA, 200mA, 2A, 10A, AUTO")
        # log.infoLog("[info] SMD3055 Voltage range : 200mA, 2V, 20V, 200V, 1000V, AUTO")
        
        for device in ret_devices:
            for k, v in usb_id.items():
                if v in device:
                    try:
                        super().__dict__[k] = multi_dmm(rm, device)
                        log.forcedLog(f"initialized the dmm connection and assign channel {k}")
                    except:
                        log.errorLog(f"{color.bgred}failed to initialize the dmm {device}{color.end}")
    

class siglent_sdm3055_usb_single(function):
    
    '''
    Siglent SDM3055
    - USB interface
    '''
    
    def __init__(self, resource_name=None):
        
        log.initLogger(log.info)
        
        self.rm = visa.ResourceManager()
        self.mode = None
        self.rang = None
        self.vparm = None
        self.cparm = None
        self.sampling = None
        self.nplc = None
        
        if resource_name is not None:
            try:
                self.device = self.rm.open_resource(resource_name, write_termination="\n", read_termination="\n")
                # self.device = usbtmc.Instrument(resource_name)

                current_range = ["200uA", "2mA", "20mA", "200mA", "2A", "10A", "auto"]
                voltage_range = ["200mV", "2V", "20V", "200V", "1000V", "auto", "hiz"]

                self.create_property("voltage", voltage_range)
                self.create_property("current", current_range)
                
                self.device.timeout = 5000 # 5seconds
                self.sampling = 5
                self.nplc = 1
                
                self.set_nplc = self.nplc
                self.set_sampling = self.sampling
            except:
                log.errorLog(f"{color.bgred}failed to initialize the dmm{color.end}")
        else:
            log.errorLog(f"{color.bgred}[sdm3055] resource address is required{color.end}")
        
    
    def read(self, command):
        
        try:
            ret = self.device.query(command)
        except:
            log.infoLog(f"[dmm] read error, retry reading")
            ret = self.device.query(command)
        return ret
    
    
    def send(self, command):
        self.device.write(command)


class agilent_34401a:
    
    def __init__(self, resource_name=None):

        try:
            self.rm = serial.Serial(port=resource_name, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, xonxoff=False, timeout=0)
            self.send("*CLS")
            self.send("SYSTem:REMote")
            self.clear_buffer
        except:
            log.errorLog(f"failed to initialize the agilent 34401a")
    
    
    def read(self, command):
        
        try:
            self.send(command)
        except:
            self.clear_buffer
            log.infoLog(f"[34401a] transfer error, retry sending")
            self.send(command)
            
        res = None
        cnt = 0
        for _ in range(10):
            delay(0.25)
            temp = self.rm.readlines()
            if len(temp) == 0:
                cnt += 1
                if cnt == 4:
                    break
            else:
                res = temp
                return res[0].decode()
            
        return 0
    
    
    def send(self, command):
        
        msg = (command + "\n").encode()
        self.rm.write(msg)
    
    
    @property
    def clear_buffer(self):
        
        self.send("*CLS")
        # log.infoLog(f"dmm connection : {self.read('*IDN?')}")
        self.send("SYSTem:REMote")
        
        for _ in range(4):
            self.rm.readlines()
    
    
    @property
    def voltage(self):
        
        ret = self.read("MEAS:VOLT:DC?")
        if ret == None:
            delay(0.5)
            self.clear_buffer
            delay(0.5)
            ret = self.read("MEAS:VOLT:DC?")

        try:
            numeric = "".join(char for char in ret if char.isdigit() or char in ['.', 'e', 'E', '+', '-'])
        except:
            self.clear_buffer
            delay(0.5)
            ret = self.read("MEAS:VOLT:DC?")
            numeric = "".join(char for char in ret if char.isdigit() or char in ['.', 'e', 'E', '+', '-'])
        return float(numeric)
    
    
    '''
    @property
    def current(self):
        
        ret = self.read("MEAS:CURR:DC?")
        numeric = "".join(char for char in ret if char.isdigit() or char in ['.', 'e', 'E', '+', '-'])
        return float(numeric)
    '''
    

class function_keithley:
    
    def get_average(self, list_data):
        
        string_list = list_data.split(",")
        float_list = [float(num.strip()) for num in string_list]
        average = sum(float_list) / len(float_list)
        
        return average
    
    
    @property
    def set_sampling(self):
        
        ret = self.read("CURR:AVER:COUNT?")
        log.forcedLog(f"sampling count : {ret}")
        
    
    @set_sampling.setter
    def set_sampling(self, cfg):
        
        self.sampling = cfg
        
        if self.mode =="current":
            self.send(f"CURR:AVER:COUNT {cfg}")
            self.send("CURR:AVER ON")
        else:
            self.send(f"VOLT:AVER:COUNT {cfg}")
            self.send("VOLT:AVER ON")
    
    
    @property
    def set_nplc(self):
        
        # 0.005 ~ 15
        
        i_nplc = self.read("CURR:DC:NPLC?")
        v_nplc = self.read("VOLT:DC:NPLC?")
        log.forcedLog(f"volt:nplc={v_nplc}")
        log.forcedLog(f"curr:nplc={i_nplc}")
    
    
    @set_nplc.setter
    def set_nplc(self, cfg):
        
        self.nplc = cfg
        self.send(f"CURR:DC:NPLC {self.nplc}")
        self.send(f"VOLT:DC:NPLC {self.nplc}") # option 1, 10, 100, 0.5
    
    
    def current(self, cfg):
        
        self.mode = "current"
        self.vparm = None
        
        if cfg == "auto":
            
            if (self.mode != "current") or (self.rang != "auto") or (self.cparm != "auto"):
                
                self.send(':FUNCtion "CURRent"')
                
                self.rang = "auto"
                self.cparm = "auto"
                self.send(":SENSe:CURRent:RANGe:AUTO ON")
                
                self.set_nplc = self.nplc
                self.set_sampling = self.sampling
                
        else:
            
            if (self.mode != "current") or (self.rang != "fixed" or (self.cparm != cfg)):
                
                self.send(':FUNCtion "CURRent"')
                
                self.rang = "fixed"
                self.cparm = cfg
                self.send(f":SENSe:CURRent:RANGe {cfg}")      
                
                self.set_nplc = self.nplc
                self.set_sampling = self.sampling  
                
        # ret = self.read("FETC?")
        ret = self.read("READ?")
        # average_ret = self.get_average(list_data=ret)
        # return average_ret
        return float(ret)
    
    
    def voltage(self, cfg):
        
        self.mode = "voltage"
        self.cparm = None
        
        if cfg == "auto":
            
            self.send(':FUNCtion "VOLTage"')
            
            if (self.rang != "auto") or (self.vparm != None):
                self.rang  = "auto"
                self.vparm = None
                self.send(":SENSe:VOLTage:RANGe:AUTO ON")
                
                self.set_nplc = self.nplc
                self.set_sampling = self.sampling
                self.send(":SENS:VOLT:INP AUTO")
                
        elif cfg == "hiz":
            
            self.send(':FUNCtion "VOLTage"')
            
            if (self.rang != "hiz") or (self.vparm != "hiz"):
                self.rang = "hiz"
                self.vparm = "hiz"
                self.send(":SENSe:VOLTage:RANGe:AUTO ON")
                
                self.set_nplc = self.nplc
                self.set_sampling = self.sampling
                self.send(":SENS:VOLT:INP AUTO")
        else:
            
            self.send(':FUNCtion "VOLTage"')
            
            if (self.rang != "fixed") or (self.vparm != cfg):
                self.rang = "fixed"
                self.vparm = cfg
                self.send(f":SENSe:VOLTage:RANGe {cfg}")
                
                self.set_nplc = self.nplc
                self.set_sampling = self.sampling
                self.send(":SENS:VOLT:INP AUTO")
                
        # ret = self.read("FETC?")
        ret = self.read("READ?")
        # average_ret = self.get_average(list_data=ret)
        # return average_ret
        return float(ret)
    
    
    @property
    def resistance(self):
        
        self.send(':SENS:FUNC "RES"')
        
        if self.mode != "resistance":
            
            self.send(":SENS:RES:NPLC DEF")
            
            self.mode  = "resistance"
            self.rang  = None
            self.vparm = None
            self.cparm = None
            
        ret = self.read("READ?")
        return float(ret)
    

    @property
    def frequency(self):
        
        self.send(':FUNCtion "FREQ"')
        
        if self.mode != "frequency":
            self.mode = "frequency"
            self.rang = None
            self.set_nplc = 5
            self.set_sampling = 10
        
        ret = self.read("READ?")
        return float(ret)
    
    
    @property
    def temperature(self):
        
        self.send(':FUNCtion "TEMP"')
        ret = self.read("READ?")
        return float(ret)
    
    
    def create_property(self, prefix, config_list):

        for cfg in config_list:
            suffix_cfg = cfg.replace("-", "_")
            setattr(self.__class__, f"{prefix}_{suffix_cfg}", property(lambda self, cfg=cfg: getattr(self, prefix)(cfg)))




class keithley_dm6500(function_keithley):

    def __init__(self, resource_name=None, rm=None):
        
        log.initLogger(log.info)
        
        if rm == None:
            self.rm = visa.ResourceManager()
        else:
            self.rm = rm
        
        self.mode = "voltage"
        self.rang = "fixed"
        self.vparm = 10
        self.cparm = None
        self.nplc = 1
        self.sampling = 10
        self.connection = False

        if resource_name is not None:
            
            try:
                self.device = self.rm.open_resource(resource_name, write_termination="\n", read_termination="\n")
                self.connection = True
                log.forcedLog(f"initialized the dm6500 connection")
                
            except:
                log.errorLog(f"{color.bgred}failed to initialize the dm6500{color.end}")
                
        else:
            with open(equipment_dir/"devices.yaml") as yaml_dev:
                dmm_id = yaml.safe_load(yaml_dev)
                
            usb_id = dmm_id["digital_multimeter"]["keithley_dmm6500"]
            self.device = self.rm.open_resource(usb_id, write_termination="\n", read_termination="\n")
            log.forcedLog(f"initialized the dm6500 connection")
            
            self.connection = True
        
        if self.connection:
            
            current_range = ["10E-6", "100E-6", "1E-3", "10E-3", "100E-3", "1", "3"]
            voltage_range = ["1E-1", "1", "10", "100", "1000", "auto", "hiz"]

            self.create_property("voltage", voltage_range)
            self.create_property("current", current_range)
            
            self.device.timeout = 5000 # 5seconds
            self.set_nplc = self.nplc
            self.set_sampling = self.sampling
        
    
    def read(self, command):
        
        try:
            ret = self.device.query(command)
        except:
            log.infoLog(f"[dmm] read error, retry reading")
            ret = self.device.query(command)
        return ret
    
    
    def send(self, command):
        self.device.write(command)



class function_rohde:
    
    def get_average(self, list_data):
        
        string_list = list_data.split(",")
        float_list = [float(num.strip()) for num in string_list]
        average = sum(float_list) / len(float_list)
        
        return average
    
    
    def current(self, cfg):
        
        self.mode = "current"
        self.vparm = None
        
        if cfg == "auto":
            
            self.send("TRIG:COUN 10")
            
            if (self.mode != "current") or (self.rang != "auto") or (self.cparm != "auto"):
                
                self.send("CONF:CURR:DC")
                delay(3)
                
                self.rang = "auto"
                self.cparm = "auto"
                
        else:
            
            self.send("TRIG:COUN 10")
            
            if (self.mode != "current") or (self.rang != "fixed" or (self.cparm != cfg)):
                
                self.send(f"CONF:CURR:DC {cfg}")
                
                self.rang = "fixed"
                self.cparm = cfg
        
        # ret = self.read("READ?")
        self.send("TRIG:MODE AUTO")
        self.send("INIT")
        ret = self.read("FETC?")
        return float(ret)
    
    
    def voltage(self, cfg):
        
        self.mode = "voltage"
        self.cparm = None
        
        if cfg == "auto":
            
            if (self.rang != "auto") or (self.vparm != None):
                self.rang  = "auto"
                self.vparm = None
                
                self.send("CONF:VOLT:DC")
                delay(3)
                
        else:
            
            if (self.rang != "fixed") or (self.vparm != cfg):
                self.rang = "fixed"
                self.vparm = cfg
                
                self.send(f"CONF:VOLT:DC {cfg}")
                delay(3)
                
        ret = self.read("READ?")
        return float(ret)
    
    
    @property
    def resistance(self):
        
        if self.mode != "resistance":
            
            self.send("CONF:RES AUTO")
            delay(3)
            
            self.mode  = "resistance"
            self.rang  = None
            self.vparm = None
            self.cparm = None
            
        ret = self.read("READ?")
        return float(ret)
    

    @property
    def frequency(self):
        
        if self.mode != "frequency":
            
            self.send("CONF:FREQ:VOLT")
            delay(3)
            
            self.mode = "frequency"
            self.rang = None
            self.set_nplc = 5
            self.set_sampling = 10
        
        ret = self.read("READ?")
        return float(ret)
    
    
    def create_property(self, prefix, config_list):

        for cfg in config_list:
            suffix_cfg = cfg.replace("-", "_")
            setattr(self.__class__, f"{prefix}_{suffix_cfg}", property(lambda self, cfg=cfg: getattr(self, prefix)(cfg)))



class rohde_hmc8012(function_rohde):
    
    def __init__(self, resource_name=None, rm=None):
        
        log.initLogger(log.info)
        
        if rm == None:
            self.rm = visa.ResourceManager()
        else:
            self.rm = rm
        
        self.mode = "voltage"
        self.rang = "fixed"
        self.vparm = 10
        self.cparm = None
        self.connection = False

        if resource_name is not None:
            
            try:
                self.device = self.rm.open_resource(resource_name, write_termination="\n", read_termination="\n")
                self.connection = True
                log.forcedLog(f"initialized hmc 8012 connection")
                
            except:
                log.errorLog(f"{color.bgred}failed to initialize hmc 8012{color.end}")
                
        else:
            with open(equipment_dir/"devices.yaml") as yaml_dev:
                dmm_id = yaml.safe_load(yaml_dev)
            usb_id = dmm_id["digital_multimeter"]["rohde_hmc8012"]
            
            try:
                self.device = self.rm.open_resource(usb_id, write_termination="\n", read_termination="\n")
                log.forcedLog(f"initialized the hmc 8012 connection")
                self.connection = True
            except:
                log.errorLog(f"{color.bgred}failed to initialize hmc 8012{color.end}")
            
            if self.connection:
            
                current_range = ["20mA", "200mA", "2A", "10A"]
                voltage_range = ["400mV", "4V", "40V", "400V", "1000V"]

                self.create_property("voltage", voltage_range)
                self.create_property("current", current_range)
                
                self.device.timeout = 5000 # 5seconds
    
    
    def read(self, command):
        
        try:
            ret = self.device.query(command)
        except:
            log.infoLog(f"[dmm] read error, retry reading")
            ret = self.device.query(command)
        return ret
    
    
    def send(self, command):
        self.device.write(command)



class dmm(keithley_dm6500, rohde_hmc8012):
    
    def __init__(self):
    
        log.initLogger(log.info)
        
        with open(equipment_dir/"devices.yaml") as yaml_dev:
            dmm_list = yaml.safe_load(yaml_dev)
        
        dmm6500 = dmm_list["digital_multimeter"]["keithley_dmm6500"]
        hmc8012 = dmm_list["digital_multimeter"]["rohde_hmc8012"]
        
        self.rm = visa.ResourceManager()
        
        try:
            super().__dict__["ch1"] = keithley_dm6500(dmm6500, self.rm)
        except:
            log.errorLog(f"{color.bgred}failed to initialize dmm 6500 to ch1{color.end}")
        
        try:
            super().__dict__["ch2"] = rohde_hmc8012(hmc8012, self.rm)
        except:
            log.errorLog(f"{color.bgred}failed to initialize dmm hmc8012 to ch2{color.end}")
        


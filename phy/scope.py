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
waveform_dir = pathlib.Path(phy_dir).parent/"log/waveform"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)
if not waveform_dir.exists():
    waveform_dir.mkdir(parents=True, exist_ok=True)


from interface.cui_logger import logger as log
from interface.cui_colors import color
from time import sleep
from datetime import datetime

# import vxi11
import pyvisa as visa
import cv2 as cv
import yaml


class constant:
    
    RUN    = 1
    STOP   = 0
    BW20M  = "TWENTY"
    BW250M = "TWOFIFTY"
    BWFULL = "FULL"
    
    RECORD_1K   = 1000
    RECORD_10K  = 10_000
    RECORD_100K = 100_000
    RECORD_1M   = 1_000_000
    RECORD_5M   = 5_000_000
    RECORD_10M  = 10_000_000
    
    
class channel_function:
    
    def __init__(self, handler, channel):
        
        self._protocol = handler
        self.channel   = channel
        
        
    def send(self, command):

        self._protocol.write(command)
        sleep(0.3)
        
        
    def query(self, command):
        
        self._protocol.write(command)
        sleep(0.3)
        try:
            ret = self._protocol.read()
        except:
            log.infoLog(f"[dpo4104b] read error, retry reading")
            ret = self._protocol.read()

        return ret
    
    
    @property
    def enable(self):
        self.send(f"SELECT:CH{self.channel} ON")
    
    
    @property
    def disable(self):
        self.send(f"SELECT:CH{self.channel} OFF")
    
    
    @property
    def vertical_grid(self):

        ret = self.query(f"CH{self.channel}:POSition?")
        return ret


    @vertical_grid.setter
    def vertical_grid(self, grid):

        self.send(f"CH{self.channel}:POSition {grid}")
    
    
    @property
    def vertical_scale(self):

        ret= self.query(f"CH{self.channel}:SCALE?")
        return ret
    
    
    @vertical_scale.setter
    def vertical_scale(self, voltage):

        self.send(f"CH{self.channel}:SCALE {voltage}")

    @property
    def vertical_scale_grid(self):
        
        print(f"require the scale and grid factors")
        
    
    @vertical_scale_grid.setter
    def vertical_scale_grid(self, *args):
        
        for tup in args:
            len_args = len(args)
            if len_args == 1:
                scale = tup[0]
                grid  = tup[1]
            else:
                log.forcedLog(f"configuration error, require the scale and grid factors (e.g. self.vertical_scale_grid = 2, -2")
        
        self.vertical_scale = scale
        self.vertical_grid  = grid
        
        
    @property
    def vertical_offset(self):

        ret = self.query(f"CH{self.channel}:OFFS?")
        return ret

    
    @vertical_offset.setter
    def vertical_offset(self, offset):

        self.send(f"CH{self.channel}:OFFS {offset}")
    
    
    @property
    def trigger_rise(self):

        ret = self.query(f"TRIGGER:A:LEVel?")
        return ret
    

    @trigger_rise.setter
    def trigger_rise(self, voltage):
        
        self.send(f"TRIGGER:A:EDGE:SOURCE CH{self.channel}")
        self.send(f"TRIGGER:A:EDGE:SLOPE RISE")
        self.send(f"TRIGGER:A:LEVel {voltage}")
    

    @property
    def trigger_fall(self):

        ret = self.query(f"TRIGGER:A:LEVel?")
        return ret
    

    @trigger_fall.setter
    def trigger_fall(self, voltage):
        
        self.send(f"TRIGGER:A:EDGE:SOURCE CH{self.channel}")
        self.send(f"TRIGGER:A:EDGE:SLOPE FALL")
        self.send(f"TRIGGER:A:LEVel {voltage}")
    
    
    @property
    def label(self):

        ret = self.query(f"CH{self.channel}:LABEL?").replace('"','')
        return ret
        
    
    @label.setter
    def label(self, string):

        # self.send(f"SETUP{self.channel}:LABEL {string}")
        self.send(f"CH{self.channel}:LABEL '{string}'")
        log.infoLog(f"labeling to channel {self.channel} : {string}")

    
    @property
    def label_off(self):
        
        # self.send(f"SETUP{self.channel}:LABEL ''")
        self.send(f"CH{self.channel}:LABEL ''")
    

    @property
    def label_on(self):
        
        self.send(f"SELECT:CH{self.channel} ON")
    

    @property
    def bw_full(self):
        self.send(f"CH{self.channel}:BANDWIDTH {constant.BWFULL}")
    
    
    @property
    def bw_20MHz(self):
        self.send(f"CH{self.channel}:BANDWIDTH {constant.BW20M}")
    
    
    @property
    def bw_250MHz(self):
        self.send(f"CH{self.channel}:BANDWIDTH {constant.BW250M}")
    
    
    
class common_function:
    
    @property
    def label_on_batch(self):
        pass


    @label_on_batch.setter
    def label_on_batch(self, *args):
        
        for tup in args:
            len_args = len(args)
            for n in range(1, len_args+1):
                self.send(f"SELECT:CH{tup[n]} ON")
        
    
    @property
    def label_off_batch(self):
        pass


    @label_off_batch.setter
    def label_off_batch(self, *args):
        
        for n in args[0]:
            self.send(f"CH{n}:LABEL ''")
                
    
    @property
    def stop(self):
        self.send("ACQUIRE:STATE STOP")
        
    
    @property
    def forced_trigger(self):
        self.send("FPANEL:PRESS FORCetrig")
    
    
    @property
    def run(self):
        
        state = int(self.query("ACQuire:STATE?")[-2:-1])
        if state == 0:
            self.send("FPANEL:PRESS RUNSTOP")
        # self.send("ACQUIRE:STATE RUN")
    
    
    @property
    def single(self):
        
        self.send("ACQUIRE:STATE OFF")
        self.send("ACQUIRE:STOPAFTER SEQUENCE")
        self.send("ACQUIRE:STATE ON")

    
    @property
    def normal(self):
        self.send("TRIG:A:MOD NORMAL")
    
    
    @property
    def roll(self):
        self.send("TRIG:A:MOD AUTO")
        
        
    @property
    def init_default(self):
        
        for ch in [1, 2, 3, 4]:
            position = ch-1
            self.send(f"CH{ch}:POSition -{position}")
            self.send(f"CH{ch}:SCALE 1")
            self.send(f"SELECT:CH{ch} ON")
            self.send(f"CH{ch}:LABEL ''")
        
        self.horizontal_position = 0
        self.horizontal_scale = 1e-3
        self.roll
        self.run
    
    
    @property
    def disable_channel(self):
        pass


    @disable_channel.setter
    def disable_channel(self, *args):
        
        for tup in args:
            for i in tup:
                self.send(f"SELECT:CH{i} OFF")
    
    
    @property
    def enable_channel(self):
        pass


    @enable_channel.setter
    def enable_channel(self, *args):
        
        for tup in args:
            for i in tup:
                self.send(f"SELECT:CH{i} ON")
    

    @property
    def get_meas1(self):

        ret = self.query(f"MEASU:MEAS1:VAL?")
        return float(ret)
    

    @property
    def get_meas2(self):

        ret = self.query(f"MEASU:MEAS2:VAL?")
        return float(ret)
    
    @property
    def get_meas3(self):

        ret = self.query(f"MEASU:MEAS3:VAL?")
        return float(ret)
    
    @property
    def get_meas4(self):

        ret = self.query(f"MEASU:MEAS4:VAL?")
        return float(ret)
    

    @property
    def horizontal_center(self):
        self.horizontal_position = 0
    
    
    @property
    def horizontal_position(self):

        ret = self.query(f"HORizontal:DELay:TIMe?")
        return ret
    

    @horizontal_position.setter
    def horizontal_position(self, delay):
        
        self.send(f"HORizontal:DELay:MODe ON")
        self.send(f"HORizontal:DELay:TIMe {delay}")
        # log.infoLog(f"set horizontal position to {delay}")
    

    @property
    def horizontal_scale_grid(self):
        
        print(f"require the scale and grid factors")
        
    
    @horizontal_scale_grid.setter
    def horizontal_scale_grid(self, *args):
        
        for tup in args:
            len_args = len(args)
            if len_args == 1:
                scale = tup[0]
                grid  = tup[1]
            else:
                log.forcedLog(f"configuration error, require the scale and grid factors (e.g. self.horizontal_scale_grid = 2, -2")
        
        self.horizontal_scale = scale
        self.horizontal_grid  = grid
        
        
    @property
    def horizontal_grid(self):

        ret = self.send(f"HORizontal:DELay:TIMe?")
        return ret


    @horizontal_grid.setter
    def horizontal_grid(self, grid):
        
        # based on the center line, then plus or minus
        single_grid = float(self.query("HOR:SCA?"))
        self.send(f"HORizontal:DELay:MODe ON")
        self.send(f"HORizontal:DELay:TIMe {single_grid*(-grid)}")

    
    @property
    def horizontal_scale(self):

        ret = self.query(f"HORizontal:SCAle")
        return ret


    @horizontal_scale.setter
    def horizontal_scale(self, scale):
        
        self.send(f"HORizontal:DELay:MODe ON")
        self.send(f"HORizontal:SCAle {scale}")
        # log.infoLog(f"set horizontal scale to {scale}")
    

    def create_property(self, prefix, config_list):

        for cfg in config_list:
            setattr(self.__class__, f"{prefix}_{cfg}", property(lambda self, cfg=cfg: getattr(self, prefix)(cfg)))
    
    
    def record_length(self, level):
        
        if   level == "1K"  : self.send(f"HORIZONTAL:RECORDLENGTH {constant.RECORD_1K}")
        elif level == "10K" : self.send(f"HORIZONTAL:RECORDLENGTH {constant.RECORD_10K}")
        elif level == "100K": self.send(f"HORIZONTAL:RECORDLENGTH {constant.RECORD_100K}")
        elif level == "1M"  : self.send(f"HORIZONTAL:RECORDLENGTH {constant.RECORD_1M}")
        elif level == "5M"  : self.send(f"HORIZONTAL:RECORDLENGTH {constant.RECORD_5M}")
        elif level == "10M" : self.send(f"HORIZONTAL:RECORDLENGTH {constant.RECORD_10M}")
        # log.infoLog(f"Horizontal record length is set to {self.query('HORizontal:RECOrdlength?')}")
    
    
    @property
    def save_waveform(self):
        log.infoLog(f"filename is required")
    

    @save_waveform.setter
    def save_waveform(self, file):
        
        self.send("SAVe:IMAGe:FILEFormat PNG")
        self.send("SAVe:IMAGe:INKSaver OFF")
        self.send("HARDCopy STARt")
        imgData = self.dev.read_raw()
        
        if file is None:
            dt = datetime.now()
            self.filename = dt.strftime("%Y%m%d_%H%M%S.png")

        if file.endswith(".png"):
            self.filename = file
        else:
            self.filename = file + ".png"
        
        file_path = waveform_dir/self.filename
        imgFile = open(file_path, "wb")
        imgFile.write(imgData)
        imgFile.close()

        # raw_image = cv.imread("./log/" + self.filename)
        png_raw = cv.imread(file_path)
        inverted_image = cv.bitwise_not(png_raw)
        
        cv.imwrite(waveform_dir/f"invert_{self.filename}", inverted_image)
        log.infoLog(f"save the waveform into the log directory with {self.filename}")


class tektronix_mdo34(channel_function, common_function):
    
    '''
    Tektronix
    - Model : MDO34
    - 4 channel
    - usb protocol
    '''

    def __init__(self, resource_name=None):
        
        log.initLogger(log.info)
        self.rm = visa.ResourceManager()
        
        if resource_name is not None:
            
            try:
                self.dev = self.rm.open_resource(resource_name)
                
                for ch in [1, 2, 3,4]:
                    super().__dict__[f"ch{ch}"] = channel_function(self.dev, ch)
                log.forcedLog(f"initialized the scope connection")
            except:
                log.errorLog(f"{color.bgred}failed to initialize tektronix dp series{color.end}")
                
        else:
            
            try:
                with open(equipment_dir/"devices.yaml") as yaml_dev:
                    digital_scope = yaml.safe_load(yaml_dev)
                
                ds_id = digital_scope["oscilloscope"]["tektronix_mdo34"]
                self.dev = self.rm.open_resource(ds_id)
                
                for ch in [1, 2, 3,4]:
                    super().__dict__[f"ch{ch}"] = channel_function(self.dev, ch)
                log.forcedLog(f"initialized the scope connection")
            
            except:
                log.errorLog(f"{color.bgred}failed to initialize tektronix dp series{color.end}")

        resolution = ["1K", "10K", "100K", "1M", "5M", "10M"]
        self.create_property("record_length", resolution)
        self.filename = None
    
    
    def send(self, command):
        self.dev.write(command)
        
        
    def query(self, command):
        
        self.send(command)
        sleep(0.4)
        try:
            ret = self.dev.read()
        except:
            log.infoLog(f"[dpo4104b] read error, retry reading")
            ret = self.dev.read()
        return ret
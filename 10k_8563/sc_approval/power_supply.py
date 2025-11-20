# ! /usr/bin/env python
# coding=utf-8

from time import sleep as delay
import pyvisa as visa



class visa_resource:

    def vias_scan():

        rm = visa.ResourceManager()
        ret = rm.list_resources()
        for n in range(len(ret)):
            print(f"[USB ID_{n}] {ret[n]}")



class itech_it_m3612_usb:
    
    def __init__(self, resource_name=None):
        
        self.rm = visa.ResourceManager()
        self.device = self.rm.open_resource(resource_name)
    

    def read(self, command):
        
        try:
            ret = self.device.query(command)
        except:
            ret = self.device.query(command)
        return ret
    
    
    def send(self, command):
        self.device.write(command)
    
    
    @property
    def enable(self):
        self.device.write("OUTP 1")
    

    @property
    def disable(self):
        self.device.write("OUTP 0")
    

    @property
    def iset(self):
        pass


    @iset.setter
    def iset(self, current):
        self.send(f"SOUR:CURR {current+0.1}")
        self.send(f"SOUR:CURR:LIM {current}")
    
    
    @property
    def vset(self):
        pass


    @vset.setter
    def vset(self, voltage):
        self.send(f"SOUR:VOLT {voltage}")
    
    
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
            print(f"configuration error, require voltage and current input (e.g. self.cfg_all = 5, 0.2)")
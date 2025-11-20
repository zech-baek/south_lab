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



class agilent_34410a_usb:
    
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
    def current(self):
        
        sample = list()
        for _ in range(20):
            temp = float(self.read("MEAS:CURR:DC? 10mA"))
            sample.append(temp)
        sample.sort()
        selected_samples = sample[4:15]
        ret = sum(selected_samples) / len(selected_samples)
        
        return ret
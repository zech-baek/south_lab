# ! /usr/bin/env python
# coding=utf-8

import os
import sys

from time import sleep as delay
import pyvisa as visa
import yaml, sys



class function:
    
    def __init__(self, protocol, channel):
        
        self._protocol = protocol
        self._channel  = channel
    
    
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
            pass
    
    
    @property
    def voltage(self):
        return  float(self._protocol.query(f"MEAS:VOLT? (@{self._channel})"))
    
    
    @property
    def current(self):
        return float(self._protocol.query(f"MEAS:CURR? (@{self._channel})"))


    @property
    def clear_protection(self):
        self._protocol.send(f"OUTP:PROT:CLE (@{self._channel})")
    

    @property
    def power_recycle(self):

        self.disable
        delay(2)
        self.enable
        delay(1)



class keysight_N6705:
    
    def __init__(self, resource_name):
        
        self.rm = visa.ResourceManager()
        self.device = self.rm.open_resource(resource_name)
        self.__dict__["ch1"] = function(self, 1)
        self.__dict__["ch2"] = function(self, 2)
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
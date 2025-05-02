from time import sleep
import RPi.GPIO as GPIO
import os, sys, yaml



class rpi_tspi(object):
    
    def __init__(self, sdt=35, sck=37):
        
        self.pulled_low  = sdt # GPIO pin 35
        self.pulled_half = sck # GPIO pin 37
        self.delay       = 0.001 # roughly 500Hz clock

        self.reset()
        GPIO.setwarnings(False) # disble warning message
        GPIO.setmode(GPIO.BOARD) # allocate the pin number to the parameter
        
        # set the pin to output by default LOw for TSPI initial state
        GPIO.setup(self.pulled_low , GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.pulled_half, GPIO.OUT, initial=GPIO.LOW)
        
        self.set_default

        # the register mapping
        # with open(f"./device/HL7528_reg.yaml") as y:
        #     regmap = yaml.safe_load(y)
    
    
    @property
    def d1(self):
        
        # data 1 (high), low to high
        GPIO.output(self.pulled_low, GPIO.HIGH)
        sleep(self.delay)
        GPIO.output(self.pulled_low, GPIO.LOW)
        sleep(self.delay)
    
    
    @property
    def d0(self):
        
        # data 0 (low), half to high
        GPIO.output(self.pulled_half, GPIO.HIGH)
        sleep(self.delay)
        GPIO.output(self.pulled_half, GPIO.LOW)
        sleep(self.delay)
    
    
    @property
    def set_default(self):
        
        GPIO.output(self.pulled_low,  GPIO.LOW)
        GPIO.output(self.pulled_half, GPIO.LOW)
    
    
    @property
    def read(self):
        
        # read signal is same as data high
        self.d1
    
    
    @property
    def write(self):
        
        # /write signal is same as data low
        self.d0
        
    
    @property
    def dummy_cycle(self):
        
        # extra 3 cycles are needed to for every write and middle of read transaction
        for _ in range(3):
            self.d0
        
    
    @property
    def exit_testMode(self):
        
        # need to write to exit from the test mode
        # 4h'3 = 8'h79 (0x3 = 0x79)
        self.write
        self.d0
        self.d0
        self.d1
        self.d1
        
        self.d0
        self.d1
        self.d1
        self.d1
        self.d1
        self.d0
        self.d0
        self.d1
        
        self.dummy_cycle


    def reset(self):
        
        print(f"- reset all GPIOs configuration")
        GPIO.cleanup()

    
    @property
    def regmap_status(self):
        
        pass
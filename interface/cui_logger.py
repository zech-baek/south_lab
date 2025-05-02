# purpose : configuration class for logging
# logging levle
#   - debug < info < warning < error < critical
#   - default : info


import logging
import datetime
import os
import re
import csv
import pyvisa as visa


# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib

try:
    # try to use __file__
    doc_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        doc_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        doc_dir = os.getcwd()

log_dir = pathlib.Path(doc_dir).parent/"log"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)

  
'''
function description
- write_log(text)
	* generate today_time_format.log file
	* write the text into the log file
	* all color patterns are removed
- output(text, title, style)
	* title : file name
	* style == "message" : remove all color pattern, then save into the log file
    * style == "csv"     : save the message into the csv file
- usage
	log.initLogger(hmi_logging.info)
	log.initLogger(hmi_logging.error)
- if hmi_logging.output is true, write_log will add the message into the log file
- output_set_file(title)
	* assigne the output file name
- output_file(message)
	* output the message into the .log file
- output_csv(message)
	* output the message into the .csv file
- output_blank()
- time_stamp(display, ret)
'''


def write_log(text):
    
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    
    now = datetime.datetime.now()
    formatted_date = now.strftime("%Y-%m-%d %Hh%Mm%S.%f")[:-3] + "s"
    
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
    res = ansi_pattern.sub('', text)
    
    with open(log_dir/f"{current_date}.log", "a") as log_file:
        log_file.write(f"{formatted_date} {res}"+"\n")


def output(text, title, style="message"):
    
    '''
    [case 1] style == "message" : remove all color pattern, then save into the log file
    [case 2] style == "csv"     : save the message into the csv file
    '''
    
    if style == "message":
        ansi_pattern = re.compile(r'\x1b\[[0-9;]*m') # remove color pattern
        res = ansi_pattern.sub('', text)
        with open(log_dir/f"{title}.log", "a") as log_file:
            log_file.write(f"{res}"+"\n")
    elif style == "csv":
        with open(log_dir/f"{title}.csv", "a", newline="") as f:
            write_handler = csv.writer(f)
            write_handler.writerow(text)
    else:
        pass
        

class ExcludePrefixFormatter(logging.Formatter):
    
    def format(self, record):
        if record.msg.startswith("INFO:root:"):
            return ""
        return super().format(record)
    
    
class logger:

    logger_configured = False  # Class variable to track if logger is configured
    handler = None
    output  = True
    debug   = logging.DEBUG
    info    = logging.INFO
    error   = logging.ERROR
    disable = logging.CRITICAL
    file    = None


    @classmethod
    def initLogger(cls, level):
        
        if not cls.logger_configured:
            cls.handler = logging.getLogger()
            cls.handler.setLevel(level)
            formatter = logging.Formatter("%(asctime)s (%(levelname)s) : %(message)s")
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            
            formatter = ExcludePrefixFormatter()
            stream_handler.setFormatter(formatter)
            
            cls.handler.addHandler(stream_handler)
            cls.logger_configured = True
        else:
            cls.handler.setLevel(level)
    
    
    @classmethod
    def debugLog(cls, message):

        if not cls.logger_configured:
            cls.initLogger(level=cls.info)

        logging.debug(message)
        if cls.output:
            write_log(message)


    @classmethod
    def infoLog(cls, message):

        if not cls.logger_configured:
            cls.initLogger(level=cls.info)

        logging.info(message)
        if cls.output:
            write_log(message)
    

    @classmethod
    def forcedLog(cls, message):
        
        if not cls.logger_configured:
            cls.initLogger(level=cls.info)
        
        previous_level = cls.get_level()
        cls.set_infoLevel()
        logging.info(message)
        if cls.output:
            write_log(message)
        cls.initLogger(level=previous_level)
            
            
    @classmethod
    def errorLog(cls, message):

        if not cls.logger_configured:
            cls.initLogger(level=cls.info)
        
        logging.error(message)
        if cls.output:
            write_log(message)
    
    
    @classmethod
    def output_set_filename(cls, title):
        cls.file = title
    
    
    @classmethod
    def output_filestream(cls, message):
        
        # output the message into file
        output(text=message, title=cls.file, style="message")


    @classmethod
    def output_csv(cls, message):
        
        # output the data list into file
        output(text=message, title=cls.file, style="csv")

    
    @classmethod
    def output_blank(cls):
        
        # add carriage return
        # output(text="\n", title=cls.file, style="message")
        output(text="\n", title=cls.file, style="csv")
        

    @classmethod
    def set_debugLevel(cls):
        cls.initLogger(level=cls.debug)


    @classmethod
    def set_infoLevel(cls):
        cls.initLogger(level=cls.info)
    

    @classmethod
    def set_errorLevel(cls):
        cls.initLogger(level=cls.error)
    
    
    @classmethod
    def disable_logging(cls):
        cls.initLogger(level=cls.disable)
    
    
    @classmethod
    def get_level(cls):
        return cls.handler.level


    @classmethod
    def time_stamp(cls, display=True, ret=False, excel=False):
        
        now   = datetime.datetime.now()
        if display:
            print("[" + now.strftime("%Y-%m-%d ") + now.strftime("%H:%M:%S" + "] "), end="")
        if ret:
            if excel:
                res = now.strftime("%Y%m%d_") + now.strftime("%H%M%S")
            else:
                res = now.strftime("%Y%m%d_") + now.strftime("%H%M%S")
            return res
    
    
    @classmethod
    def visa_scan(cls):
        
        rm = visa.ResourceManager()
        ret = list(rm.list_resources())
        for n in range(len(ret)):
            print(f"### device {n+1} : {ret[n]}")
            write_log(f"### device {n+1} : {ret[n]}")
            
        return ret
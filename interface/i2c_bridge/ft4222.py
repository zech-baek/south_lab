# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib

try:
    # try to use __file__
    bridge_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        bridge_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        bridge_dir = os.getcwd()

root_dir = pathlib.Path(bridge_dir).parent.parent/"log"
log_dir = pathlib.Path(bridge_dir).parent.parent/"log"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)


from interface.cui_logger import logger as log
from ctypes import *
import os, sys
import platform


current = os.path.dirname(os.path.realpath(__file__))
FTD2XX_DLL = WinDLL("ftd2xx.dll")


def log_wrapping(header, message, is_logging=True):
    
    if is_logging:
        log_wrapping(f"ftdi", f"[{header} {sys._getframe(2).f_code.co_name}] {message}")


class FT_DEVICE_LIST_INFO_NODE(Structure):
    _fields_ = [
        ("Flags", c_ulong),
        ("Type", c_ulong),
        ("ID", c_ulong),
        ("LocId", c_ulong),
        ("SerialNumber", (c_char * 16)),
        ("Description", (c_char * 64)),
        ("ftHandle", c_void_p),
    ]


FT_OPEN_BY_SERIAL_NUMBER	= 1
FT_OPEN_BY_DESCRIPTION		= 2
FT_OPEN_BY_LOCATION			= 4

FT_OK                                   = 0
FT_INVALID_HANDLE                       = 1
FT_DEVICE_NOT_FOUND                     = 2
FT_DEVICE_NOT_OPENED                    = 3
FT_IO_ERROR                             = 4
FT_INSUFFICIENT_RESOURCES               = 5
FT_INVALID_PARAMETER                    = 6
FT_INVALID_BAUD_RATE                    = 7
FT_DEVICE_NOT_OPENED_FOR_ERASE          = 8
FT_DEVICE_NOT_OPENED_FOR_WRITE          = 9
FT_FAILED_TO_WRITE_DEVICE               = 10
FT_EEPROM_READ_FAILED                   = 11
FT_EEPROM_WRITE_FAILED                  = 12
FT_EEPROM_ERASE_FAILED                  = 13
FT_EEPROM_NOT_PRESENT                   = 14
FT_EEPROM_NOT_PROGRAMMED                = 15
FT_INVALID_ARGS                         = 16
FT_NOT_SUPPORTED                        = 17
FT_OTHER_ERROR                          = 18
FT_DEVICE_LIST_NOT_READY                = 19

FT_CreateDeviceInfoList = FTD2XX_DLL['FT_CreateDeviceInfoList']
FT_CreateDeviceInfoList.argtypes = [POINTER(c_ulong)]
FT_CreateDeviceInfoList.restype = c_uint32

FT_GetDeviceInfoList = FTD2XX_DLL['FT_GetDeviceInfoList']
FT_GetDeviceInfoList.argtypes = [POINTER(FT_DEVICE_LIST_INFO_NODE), POINTER(c_ulong)]
FT_GetDeviceInfoList.restype = c_uint32

FT_GetDeviceInfoDetail = FTD2XX_DLL['FT_GetDeviceInfoDetail']
FT_GetDeviceInfoDetail.argtypes = [c_ulong, POINTER(c_ulong), POINTER(c_ulong), POINTER(c_ulong), POINTER(c_ulong), c_void_p, c_void_p, c_void_p]
FT_GetDeviceInfoDetail.restype = c_uint32

FT_Open = FTD2XX_DLL['FT_Open']
FT_Open.argtypes = [c_int, POINTER(c_void_p)]
FT_Open.restype = c_uint32

FT_OpenEx = FTD2XX_DLL['FT_OpenEx']
FT_OpenEx.argtypes = [c_void_p, c_ulong, POINTER(c_void_p)]
FT_OpenEx.restype = c_uint32

FT_Close = FTD2XX_DLL['FT_Close']
FT_Close.argtypes = [c_void_p]
FT_Close.restype = c_uint32


current = os.getcwd()

if platform.architecture()[0] == "64bit":
    FT4222_DLL = WinDLL(current + "/misc/dll/ft4222_x64.dll")
else:
    FT4222_DLL = WinDLL(current + "/misc/dll/ft4222_x32.dll")


# FT4222 Device Status
FT4222_OK                                   = 0
FT4222_INVALID_HANDLE                       = 1
FT4222_DEVICE_NOT_FOUND                     = 2
FT4222_DEVICE_NOT_OPENED                    = 3
FT4222_IO_ERROR                             = 4
FT4222_INSUFFICIENT_RESOURCES               = 5
FT4222_INVALID_PARAMETER                    = 6
FT4222_INVALID_BAUD_RATE                    = 7
FT4222_DEVICE_NOT_OPENED_FOR_ERASE          = 8
FT4222_DEVICE_NOT_OPENED_FOR_WRITE          = 9
FT4222_FAILED_TO_WRITE_DEVICE               = 10
FT4222_EEPROM_READ_FAILED                   = 11
FT4222_EEPROM_WRITE_FAILED                  = 12
FT4222_EEPROM_ERASE_FAILED                  = 13
FT4222_EEPROM_NOT_PRESENT                   = 14
FT4222_EEPROM_NOT_PROGRAMMED                = 15
FT4222_INVALID_ARGS                         = 16
FT4222_NOT_SUPPORTED                        = 17
FT4222_OTHER_ERROR                          = 18
FT4222_DEVICE_LIST_NOT_READY                = 19

FT4222_DEVICE_NOT_SUPPORTED                 = 1000
FT4222_CLK_NOT_SUPPORTED                    = 1001
FT4222_VENDER_CMD_NOT_SUPPORTED             = 1002
FT4222_IS_NOT_SPI_MODE                      = 1003
FT4222_IS_NOT_I2C_MODE                      = 1004
FT4222_IS_NOT_SPI_SINGLE_MODE               = 1005
FT4222_IS_NOT_SPI_MULTI_MODE                = 1006
FT4222_WRONG_I2C_ADDR                       = 1007
FT4222_INVAILD_FUNCTION                     = 1008
FT4222_INVALID_POINTER                      = 1009
FT4222_EXCEEDED_MAX_TRANSFER_SIZE           = 1010
FT4222_FAILED_TO_READ_DEVICE                = 1011
FT4222_I2C_NOT_SUPPORTED_IN_THIS_MODE       = 1012
FT4222_GPIO_NOT_SUPPORTED_IN_THIS_MODE      = 1013
FT4222_GPIO_EXCEEDED_MAX_PORTNUM            = 1014
FT4222_GPIO_WRITE_NOT_SUPPORTED             = 1015
FT4222_GPIO_PULLUP_INVALID_IN_INPUTMODE     = 1016
FT4222_GPIO_PULLDOWN_INVALID_IN_INPUTMODE   = 1017
FT4222_GPIO_OPENDRAIN_INVALID_IN_OUTPUTMODE = 1018
FT4222_INTERRUPT_NOT_SUPPORTED              = 1019
FT4222_GPIO_INPUT_NOT_SUPPORTED             = 1020
FT4222_EVENT_NOT_SUPPORTED                  = 1021
FT4222_FUN_NOT_SUPPORT                      = 1022

# I2C Master condition
NONE           = 128,
START          = 2,
Repeated_START = 3,
STOP           = 4,
START_AND_STOP = 6,

# Function Type
FT4222_I2C_MASTER    = 1
FT4222_I2C_SLAVE     = 2
FT4222_SPI_MASTER    = 3
FT4222_SPI_SLAVE     = 4


class FT4222_Version(Structure):
    _fields_ = [
        ("ChipVersion", c_ulong),
        ("DllVersion", c_ulong),
    ]

FT4222_GetVersion = FT4222_DLL['FT4222_GetVersion']
FT4222_GetVersion.argtypes = [c_void_p, POINTER(FT4222_Version)]
FT4222_GetVersion.restype = c_uint32

FT4222_I2CMaster_GetStatus = FT4222_DLL['FT4222_I2CMaster_GetStatus']
FT4222_I2CMaster_GetStatus.argtypes = [c_void_p, POINTER(c_ubyte)]
FT4222_I2CMaster_GetStatus.restype = c_uint32

FT4222_UnInitialize = FT4222_DLL['FT4222_UnInitialize']
FT4222_UnInitialize.argtypes = [c_void_p]
FT4222_UnInitialize.restype = c_uint32

FT4222_I2CMaster_Init = FT4222_DLL['FT4222_I2CMaster_Init']
FT4222_I2CMaster_Init.argtypes = [c_void_p, c_uint32]
FT4222_I2CMaster_Init.restype = c_uint32

FT4222_I2CMaster_ReadEx = FT4222_DLL['FT4222_I2CMaster_ReadEx']
FT4222_I2CMaster_ReadEx.argtypes = [c_void_p, c_ushort, c_ubyte, POINTER(c_ubyte), c_ushort, POINTER(c_ushort)]
FT4222_I2CMaster_ReadEx.restype = c_uint32

FT4222_I2CMaster_WriteEx = FT4222_DLL['FT4222_I2CMaster_WriteEx']
FT4222_I2CMaster_WriteEx.argtypes = [c_void_p, c_ushort, c_ubyte, POINTER(c_ubyte), c_ushort, POINTER(c_ushort)]
FT4222_I2CMaster_WriteEx.restype = c_uint32



class FTD2XX(object):
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self):
        cls = type(self)
        if hasattr(cls, "_init"):
            return

        self.numDev = c_ulong()
        cls._init = True
        

    def createDeviceInfoList(self):
        ftStatus = FT_CreateDeviceInfoList(byref(self.numDev))
        return -ftStatus


    def getDeviceInfoDetail(self):
        ret = self.createDeviceInfoList()
        if ret < 0:
            return ret
        
        if self.numDev.value <= 0:
            return -FT_DEVICE_NOT_FOUND
        
        self.node = (FT_DEVICE_LIST_INFO_NODE * self.numDev.value)()
        ftStatus = FT_GetDeviceInfoList(self.node, byref(self.numDev))

        return -ftStatus
    

    def open(self):

        ret = self.getDeviceInfoDetail()
        if ret < 0:
            return ret

        if self.isOpen():
            if self.node[0].Type == 3:
                return -FT4222_DEVICE_NOT_SUPPORTED

            log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] Dongle is already opened")
            return FT_OK

        ftHandle = c_void_p()
        ret = FT_OpenEx(self.node[0].LocId, FT_OPEN_BY_LOCATION, byref(ftHandle))
        if ret != FT_OK:
            self.numDev = c_ulong(0)
            return -ret

        self.node[0].ftHandle = ftHandle
        return ret


    def close(self):
        if hasattr(self, "node") is False:
            return -FT_DEVICE_NOT_OPENED

        if self.numDev.value <= 0:
            return -FT_DEVICE_NOT_FOUND
        
        ret = FT_Close(self.node[0].ftHandle)
        if ret != FT_OK:
            return -ret
        
        self.numDev = c_ulong(0)
        del self.node
        return ret
    
    
    def isOpen(self):
        if hasattr(self, "node") is False:
            return False
        
        if self.getDeviceInfoDetail() != 0:
            return False
        
        return self.node[0].Flags & 0x01 == 0x01



class ft4222(FTD2XX):
    
    def __new__(cls, *args, **kwargs):
        
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance
    
    
    def __init__(self):
        
        cls = type(self)
        if hasattr(cls, "_init"):
            return
        
        super().__init__()
        self.OpenDevice()
        cls._init = True
        self.logging  = False
        self.__skip_logging = True
        self.i2c_speed(3)


    def OpenDevice(self):

        ret = super().open()
        
        if ret != FT4222_OK:
            if ret == -FT4222_DEVICE_NOT_SUPPORTED:
                log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] open error, the device is already occupied", self.logging)
            else:
                log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] open error_connection issue", self.logging)
        
        ftStatus = FT4222_I2CMaster_Init(self.node[0].ftHandle, 1000)
        
        if ftStatus != FT4222_OK:
            log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] open error, the device is already occupied", self.logging)
    
    
    def i2c_speed(self, value):
        
        scl_speed = {
            0 : 60 ,
            1 : 100,
            2 : 200,
            3 : 400
        }
        
        ftStatus = FT4222_I2CMaster_Init(self.node[0].ftHandle, scl_speed[value])
        
        if ftStatus != FT4222_OK:
            log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] failed to set up the i2c speed", self.logging)
        else:
            log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] set the i2c clock to {scl_speed[value]}kbps", self.logging)
    
    
    def i2c_read(self, i2c_address, reg_addr):
        
        # require 7bit type address
        i2c_address_8bit = i2c_address << 1
        ret = self.read(i2c_address_8bit, reg_addr)
        return ret
    
    
    def i2c_write(self, i2c_address, reg_addr, reg_val):
        
        # require 7bit type address
        i2c_address_8bit = i2c_address << 1
        self.write(i2c_address_8bit, reg_addr, reg_val)
        if not self.__skip_logging:
            log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] write to {i2c_address_8bit:#04x} : {reg_addr:#04x}={reg_val:#04x}", self.logging)
    
    
    def smbus_scan(self):
        
        ret = []
        for i in range(0x7f):
            read_single_byte = self.i2c_read(i, 0)
            if read_single_byte != "read fail":
                ret.append(i)
            else:
                pass
        log_wrapping("ftdi", "smbus scan : {ret}", self.logging)
        return ret
    
        
    def read(self, slave, address):
        """ 
        Read registers\n
        Args :
            slave = slave address
            address = register address
        Return :
            0 or read data 
            
        """
        error_log = "read fail"
        
        if self.isOpen() is False:
            log_wrapping(f"ftdi", "[read]: Dongle is not opened, please check connection of the dongle", self.logging)
            return error_log

        wbuffer = c_ubyte(address)
        rbuffer = (c_ubyte * 1)()
        addr = c_ushort(slave >> 1)
        sizeTransferred = c_ushort()

        FT4222_I2CMaster_WriteEx(self.node[0].ftHandle, addr, 0x02, byref(wbuffer), 1, byref(sizeTransferred))
        ret = self.getStatus("[read]:")
        if ret is False:
            if self.__skip_logging != True:
                log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] failed to read the register", self.logging)
            FT4222_I2CMaster_ReadEx(self.node[0].ftHandle, addr , 0x04, rbuffer, 1, byref(sizeTransferred))
            return error_log
        
        FT4222_I2CMaster_ReadEx(self.node[0].ftHandle, addr , 0x03 | 0x04, rbuffer, 1, byref(sizeTransferred))
        ret = self.getStatus("[read]:")
        if ret is False:
            if self.__skip_logging != True:
                log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}]  failed to read the register", self.logging)
            return error_log
        
        return rbuffer[0]


    def write(self, slave, addr, data):
        """ 
        Write registers\n
        Args :
            slave = slave address
            addr = register address
            data = written data
        Return :
            True or False
        """
        error_log = "write fail"
        
        if self.isOpen() is False:
            log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] connection error, failed to write", self.logging)
            return error_log
        
        buffer = (c_ubyte * 2)()
        buffer[0] = addr
        buffer[1] = data
        sizeTransferred = c_ushort()
        slaveAddress = c_ushort(slave >> 1)

        FT4222_I2CMaster_WriteEx(self.node[0].ftHandle, slaveAddress, 0x02 | 0x04, buffer, 2, byref(sizeTransferred))
        ret = self.getStatus("[write]:")
        if ret is False:
            if self.__skip_logging != True:
                log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] failed to write the register", self.logging)
            return error_log

        return True
    
    
    def getVersion(self, pVersion: FT4222_Version):
        """ 
        Get the version of FT4222H and LibFT4222
        Args :
            pVersion = Pointer to a variable of type FT4222_Version where the value will be stored.
            Type FT4222_Version is defined as follow:
            struct FT4222_Version
            {
                DWORD chipVersion; // The version of FT4222H chip
                DWORD dllVersion;  // The version of LibFT4222
            };
            Revision A chips report chipVersion as 0x42220100.
            Revision B chips report chipVersion as 0x42220200.
            Revision C chips report chipVersion as 0x42220300.
            Revision D chips report chipVersion as 0x42220400.
        Return :
            ftStatus
            
        """
        if self.isOpen() is False:
            log_wrapping(f"ftdi", f"[ft4222 {sys._getframe(2).f_code.co_name}] connection error", self.logging)
            return 0

        ftStatus = FT4222_GetVersion(self.node[0].ftHandle, byref(pVersion))
        return -ftStatus
    
    
    def getStatus(self, prefix=""):
        """
        Read the status of the I2C master controller.
        """
        if self.isOpen() is False:
            return -1
        
        status = c_ubyte()
        ftStatus = FT4222_I2CMaster_GetStatus(self.node[0].ftHandle, byref(status))
        if ftStatus != FT4222_OK:
            return -1
        
        if self.__skip_logging != True:
            if status.value & 0x01 != 0:
                log_wrapping(f"ftdi", f"{prefix} controller busy: all other status bits invalid", self.logging)
            if status.value & 0x02 != 0:
                log_wrapping(f"ftdi", f"{prefix} error condition", self.logging)
            if status.value & 0x04 != 0:
                log_wrapping(f"ftdi", f"{prefix} slave address was not acknowledged during last operation", self.logging)
            if status.value & 0x08 != 0:
                log_wrapping(f"ftdi", f"{prefix} data not acknowledged during last operation", self.logging)
            if status.value & 0x10 != 0:
                log_wrapping(f"ftdi", f"{prefix} arbitration lost during last operation", self.logging)
            
            # if status.value & 0x20 != 0:
            #     print(f"{prefix} controller idle")
            # if status.value & 0x40 != 0:
            #     print(f"{prefix} bus busy")

        return status.value & 0x02 == 0
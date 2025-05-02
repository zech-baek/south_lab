from interface.cui_logger import logger as log


def property_setter(name):

    def getter(self):
        
        ret = getattr(self, f"_{name}")
        log.debugLog(f"property getter : {name} = {ret}")
        return ret
    

    def setter(self, value):

        setattr(self, f"_{name}", value)
        log.debugLog(f"property setter : {name} = {value}")
    
    return property(getter, setter)


class register_mapping(object):
    
    def __init__(self, parm):

        self._reg_split = parm[0]
        self._reg_name  = parm[1]
        self._reg_addr  = parm[2]
        self._reg_msb   = parm[3]
        self._reg_lsb   = parm[4]
        self._reg_bith  = parm[5]
        self._reg_bitl  = parm[6]
        self._reg_auth  = parm[7]
        self._reg_rw    = parm[8]
        
    split = property_setter("reg_split")
    name  = property_setter("reg_name")
    addr  = property_setter("reg_addr")
    msb   = property_setter("reg_msb")
    lsb   = property_setter("reg_lsb")
    bith  = property_setter("reg_bith")
    bitl  = property_setter("reg_bitl")
    auth  = property_setter("reg_auth")
    rw    = property_setter("reg_rw")
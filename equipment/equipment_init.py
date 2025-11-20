from phy.multimeter import keithley_dm6500
from phy.power_supply import rigol_dp821a, rigol_dp811a
from phy.power_analyzer import keysight_N6705
from phy.scope import tektronix_mdo34
from phy.battery_simulator import asd_906b
from phy.eloader import it8511a

# from phy.eloader import sdl1030x
# from phy.relay_16ch import relay_box

# %matplotlib tk
from interface.docs.output_chart import plot
from interface.cui_colors import color
from interface.i2c_bridge.tca9548a import tca9548
from interface.docs.output_excel import excel_frame, style
from interface.cui_logger import logger as log
from interface.timer import precise_timer

from concurrent.futures import ThreadPoolExecutor

timer = precise_timer()

def delay(parameter:float):
    timer.sleep(parameter*1000)

import numpy as np

chart = plot()

dm = keithley_dm6500("USB0::0x05E6::0x6500::04651237::INSTR")
# dm2 = keithley_dm6500("USB0::0x05E6::0x6500::04651251::INSTR")

ps811 = rigol_dp811a(resource_name="USB0::0x1AB1::0x0E11::DP8H245000515::INSTR")
ps821 = rigol_dp821a(resource_name="USB0::0x1AB1::0x0E11::DP8E261000023::INSTR")

# ps = keysight_N6705()
ds = tektronix_mdo34()
bs = asd_906b(port=4)
# bs_s = asd_906b(port=11)
ps = keysight_N6705(resource_name="USB0::0x0957::0x0F07::MY47000200::INSTR")
# sm = keithley_2470()
ld = it8511a("COM12")

# relay = relay_box(i2c_h=ic)
# tc = chamber(port=3)
# mux = tca9548(ic.i2c_h, 0x70)

# --------------------------------------------------
# list_voltage = list(np.arange(5, 8, 0.005))
# voltage  = [round(num, 3) for num in list_voltage]
# --------------------------------------------------
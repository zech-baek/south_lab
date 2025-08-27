from phy.multimeter import keithley_dm6500
from phy.power_supply import rigol_dp821a
from sc_approval.ch341 import ch341
from phy.relay_16ch import relay_box

from time import sleep as delay
import datetime
import csv

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5 import uic

import sys
import os
import yaml
import time


def resource_path(relative_path):
    # Works for both development and PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  # PyInstaller temp folder
    else:
        base_path = os.path.abspath(".")  # Dev mode
    return os.path.join(base_path, relative_path)


ui_file_path = resource_path("sc_approval/main.ui")
form_class = uic.loadUiType(ui_file_path)[0]

class WindowClass(QMainWindow, form_class) :

    def __init__(self, logging=False) :

        super().__init__()
        self.setupUi(self)
        # self.setFixedSize(self.size())
        # self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        self.btn_init.clicked.connect(self.init_equipment)
        self.btn_pre.clicked.connect(self.pre_test)
        self.btn_post.clicked.connect(self.post_test)

        self.log_pre.setFontPointSize(15)
        self.log_post.setFontPointSize(15)

        self.mode = None
        self.logging = logging

        yaml_path = os.getcwd() + "/equipment.yaml"

        with open(yaml_path) as yaml_id:
            id_list = yaml.safe_load(yaml_id)

        yaml_ps_id = id_list["ps"]
        yaml_dm_id = id_list["dm"]

        self.txt_ps_id.setText(yaml_ps_id)
        self.txt_dmm_id.setText(yaml_dm_id)

        self.log_path = os.getcwd() + "/output"

        if not os.path.isdir(self.log_path):
            os.makedirs(self.log_path)
        
        self.log_pre.append(f"output path : {self.log_path}\n")
        self.log_post.append(f"output path : {self.log_path}\n")
        # self.log_pre.append(os.getcwd())

        now  = datetime.datetime.now()
        self.date = "[" + now.strftime("%Y-%m-%d") + "]"

        self.count = 1
        self.init_flag = False
    

    def closeEvent(self, event):

        event.accept()
        QApplication.quit()


    def init_equipment(self):

        ps_id = self.txt_ps_id.text()
        dmm_id = self.txt_dmm_id.text()

        if self.logging:
            print(f"equipments id : ps={ps_id}, dmm={dmm_id}")

        try:
            self.dmm = keithley_dm6500(dmm_id)
            self.output_log(message=f"initialized dmm connection", terminal=False)
            self.init_flag = True
        except:
            self.output_log(message=f"failed to init dmm", terminal=False)
            self.init_flag = False

        try:
            self.ps821 = rigol_dp821a(ps_id)
            self.output_log(message=f"initialized p/s connection", terminal=False)
            self.init_flag = True
        except:
            self.output_log(message=f"failed to init p/s", terminal=False)
            self.init_flag = False
        
        try:
            self.i2c = ch341(logging=False)
            self.output_log(message=f"initialized i2c connection", terminal=False)
            self.init_flag = True
        except:
            self.output_log(message=f"failed to init i2c", terminal=False)
            self.init_flag = False
        
        try:
            self.relay = relay_box(i2c_h=self.i2c, i2c_a=0x27, logging=False)
            self.output_log(message=f"initialized relay connection\n", terminal=False)
            self.relay.init_channels
            self.relay.logging = False
            self.init_flag = True
        except:
            self.output_log(message=f"failed to init relay", terminal=False)
            self.init_flag = False
        
        if self.init_flag:
            self.btn_init.setText(f"Init Done")
            QApplication.processEvents()
        else:
            self.btn_init.setText(f"Init Fail")
            QApplication.processEvents()
    

    def pre_test(self):

        self.mode = "pre_test"
        tray_no = None
        count = None

        if self.init_flag:
            try:
                tray_no = int(self.txt_no1.text())
            except:
                self.output_log(message=f"empty tray number in pre_test", terminal=True)

            if isinstance(tray_no, int):
                if self.chk_loop.isChecked():
                    try:
                        count = int(self.txt_loop.text())
                    except:
                        self.output_log(message=f"empty loop number in pre_test", terminal=True)
                else:
                    count = self.count

                if isinstance(count, int):

                    laptime_start = time.time()

                    for n in range(count):
                        self.output_log(message=f"enter to pre-test : mode={self.mode}, tray no.={tray_no} (count={n+1}/{count})", terminal=False)
                        self.run_test(tray_no=tray_no)
                        self.output_log(message=f"exit from pre-test mode", terminal=False)

                        lap_time = round(time.time() - laptime_start, 3)
                        self.output_log(message=f"total lap time : {lap_time}sec\n", terminal=False)
        else:
            self.output_log(message=f"devices are not connected", terminal=True)

        self.mode = None


    def post_test(self):

        self.mode = "post_test"
        tray_no = None
        count = None

        if self.init_flag:
            try:
                tray_no = int(self.txt_no2.text())
            except:
                self.output_log(message=f"empty tray number in post_test", terminal=True)

            if isinstance(tray_no, int):

                if self.chk_loop.isChecked():
                    try:
                        count = int(self.txt_loop.text())
                    except:
                        self.output_log(message=f"empty loop number in pre_test", terminal=True)
                else:
                    count = self.count

                if isinstance(count, int):

                    laptime_start = time.time()

                    for n in range(count):
                        self.output_log(message=f"enter to post-test : mode={self.mode}, tray no.={tray_no} (count={n+1}/{count})", terminal=False)
                        self.run_test(tray_no=tray_no)
                        self.output_log(message=f"exit from post-test mode", terminal=False)

                        lap_time = round(time.time() - laptime_start, 3)
                        self.output_log(message=f"total lap time : {lap_time}sec\n", terminal=False)
        else:
            self.output_log(message=f"devices are not connected", terminal=True)
        
        self.mode = None


    def output_csv(self, output, filename=None):
    
        # output should be the list type
            
        with open(f"{self.log_path}\{filename}.csv", "a", newline="") as f:
            write_handler = csv.writer(f)
            write_handler.writerow(output)
    

    def output_log(self, message=None, terminal=True, logging=True):
        
        if terminal:
            if self.mode =="pre_test":
                self.log_pre.append(message)
            else:
                self.log_post.append(message)
        
        if logging:
            trimmed_msg = message.replace("[", "").replace("]", "")

            with open(f"{self.log_path}\{self.date}_message.log", "a") as log_out:
                date_format = datetime.datetime.now().strftime("%Y-%m-%d %Hh%Mm%S.%f")[:-3] + "s"
                wrapping_message = f"[{date_format}] {trimmed_msg}"
                log_out.write(wrapping_message + "\n")
    

    def run_test(self, tray_no):

        v_vext = 20
        v_vout = 4.5

        filename = f"{self.date} Tray #{tray_no} - {self.mode}"

        #--------------------------------------------------------------------------------
        # need to assign the equipment
        #--------------------------------------------------------------------------------
        self.ps = self.ps821.ch1
        self.dm = self.dmm
        #--------------------------------------------------------------------------------

        self.dm.current_1
        self.relay.init_channels
        self.output_log(message=f"init relay channels", terminal=False)

        self.ps.disable
        self.output_log(message=f"disable power supply", terminal=False)
        delay(1)

        self.relay.ch5.enable # start signal

        #--------------------------------------------------------------------------------
        #  IQ_VEXT
        #--------------------------------------------------------------------------------
        self.relay.ch3.enable
        self.output_log(message=f"enable relay ch3 for vext path", terminal=False)

        self.ps.cfg_all = v_vext, 0.05 # vext
        self.ps.enable
        self.output_log(message=f"turn-on vext to {v_vext}V", terminal=False)
        delay(1)

        ret_00h = self.i2c.i2c_read(110, 0)
        self.output_log(message=f"[I2C Check] 0x00={ret_00h:#04x}", terminal=True)
        QApplication.processEvents()

        iq_vext = round(self.dm.current_10E_3 * 1e+6, 3)
        self.output_log(message=f"[IQ_VEXT] {iq_vext}uA", terminal=True)
        QApplication.processEvents()

        self.ps.cfg_all = 0.1, 0.02
        self.ps.disable
        self.output_log(message=f"turn-off vext", terminal=False)
        delay(0.5)

        self.relay.ch3.disable
        self.output_log(message=f"disable relay ch3 for vext path", terminal=False)
        #--------------------------------------------------------------------------------

        #--------------------------------------------------------------------------------
        #  IQ_VOUT
        #--------------------------------------------------------------------------------
        self.relay.ch1.enable
        self.output_log(message=f"enable relay ch1 for vout path", terminal=False)

        self.ps.cfg_all = v_vout, 0.05 # vout
        self.ps.enable
        self.output_log(message=f"turn-on vout to {v_vout}V", terminal=False)
        delay(1)

        ret_00h = self.i2c.i2c_read(110, 0)
        self.output_log(message=f"[I2C Check] 0x00={ret_00h:#04x}", terminal=True)
        QApplication.processEvents()

        iq_vout = round(self.dm.current_10E_3 * 1e+6, 3)
        self.output_log(message=f"[IQ_VOUT] {iq_vout}uA", terminal=True)
        QApplication.processEvents()

        self.ps.cfg_all = 0.1, 0.02
        self.ps.disable
        self.output_log(message=f"turn-off vout", terminal=False)

        self.relay.ch1.disable
        self.output_log(message=f"disable relay ch1 for vout path", terminal=False)
        #--------------------------------------------------------------------------------

        self.output_csv(output=[tray_no, iq_vext, iq_vout], filename=filename)
        self.output_log(message=f"store the data into the {filename}.csv", terminal=False)

        self.output_log(message=f"----- Test done : Tray no. {tray_no} -----", terminal=True)
        self.output_log(message=f" ", terminal=True, logging=False)
        QApplication.processEvents()

        self.relay.ch5.disable


if __name__ == "__main__" :

    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()
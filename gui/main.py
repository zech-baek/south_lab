'''
# run on the root path
python -m gui.main
'''

# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib

try:
    # try to use __file__
    base_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        base_dir = os.getcwd()

root_dir    = pathlib.Path(base_dir).parent
log_dir     = pathlib.Path(base_dir).parent/"log"
project_dir = pathlib.Path(base_dir).parent/"project"
layout_dir  = pathlib.Path(base_dir)/"layout"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)


import dearpygui.dearpygui as dpg
from interface.cui_logger import logger as log

from gui.tabs import tab_1_i2c, tab_2_user, tab_3_regmap, tab_4
from gui.shared_space import shared_var

# shared_var.rw_interface is to be shared across multiple tabs
# shared_var.rw_interface can store in a mutable object like a dictionary or a dedicated class
# initialization is required
# rw_interface = None


# variables for sharing with the tabs
class dev_info:
    
    device    = "hl7133"
    revision  = "ae"
    emulator  = "cp2112" # default
    
    hidden    = False
    connect   = False
    debugging = True
    logging   = False
    height    = 600


# variables for main.py
class var:
    
    l_shift_sts  = False


def close_gui(sender, app_data):

    # assigned to key combination : left-shift + Q
    if dpg.is_key_down(dpg.mvKey_LShift):
        dpg.stop_dearpygui()  # gracefully stops the GUI loop while allowing cleanup


def switch_tab(sender, app_data, user_data):
    
    # dpg.is_key_down is being polled in a loop, it might introduce delays

    if var.l_shift_sts:
        for i, key in enumerate([dpg.mvKey_1, dpg.mvKey_2, dpg.mvKey_3]):
            if dpg.is_key_down(key):
                dpg.set_value("tabs", shared_var.list_tab[i])
                break  # exit the loop once a key is detected


def create_ui():
    
    shared_var.height = 800 if shared_var.debugging else 600
        
    with dpg.window(
        label=f"GUI v0.1",
        width=1200,
        height=shared_var.height,
        horizontal_scrollbar=False,
        no_resize=True,
        no_scrollbar=False,
        tag="main_panel"
        ):
        
        with dpg.tab_bar(tag="tabs"):
            
            shared_var.list_tab.append(tab_1_i2c.tab_i2c())
            shared_var.list_tab.append(tab_2_user.tab_user())
            shared_var.list_tab.append(tab_3_regmap.tab_regmap())
            # shared_var.list_tab.append(tab_4.tag_func())

            # shared_var.list_tab.extend([id_tab1, id_tab2, id_tab3])

            # for id in shared_var.list_tab:
            #     tab_config = dpg.get_item_configuration(id)
            #     log.forcedLog(f"registered the tab {tab_config['label']} with id {id}")
        
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_F2, callback=handler_function_key)
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_F3, callback=handler_function_key)
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_F5, callback=handler_function_key)
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_F6, callback=handler_function_key)
        
    if shared_var.debugging:
        with dpg.handler_registry():
            dpg.add_key_press_handler(dpg.mvKey_F9, callback=print_debugging)
        with dpg.handler_registry():
            dpg.add_key_press_handler(dpg.mvKey_F10, callback=print_debugging)
        with dpg.handler_registry():
            dpg.add_key_press_handler(dpg.mvKey_F11, callback=print_debugging)
            
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_F12, callback=handler_function_key)
    
    tab_1_i2c.handler_console(sender=None, app_data=shared_var.dict_layout, user_data=tab_1_i2c.var.id_console)
    
    # update tab 1 tag and id
    # first tab is selected tab
    # get_tab_id = dpg.get_value("tabs")
    # shared_var.selected_tab = get_tab_id


def handler_function_key():
    
    if dpg.is_key_down(dpg.mvKey_F2):
        tab_2_user.handler_update_register(sender="button_update_all", app_data=None, user_data=None)
        
    elif dpg.is_key_down(dpg.mvKey_F3):
        tab_3_regmap.handler_update_register(sender="update_all_button", app_data=None, user_data="update_all_button")
        
    elif dpg.is_key_down(dpg.mvKey_F5):
        
        # need to implement for compare the key hash with the shared_var.reset_key
        reset_key = "reset_from_shortcut"
        
        tab1_console_id = tab_1_i2c.var.id_console
        tab2_console_id = tab_2_user.var.id_console
        tab3_console_id = tab_3_regmap.var.id_console
        tab_1_i2c.handler_console(sender=None, app_data=reset_key, user_data=tab1_console_id)
        tab_2_user.handler_console(sender=None, app_data=reset_key, user_data=tab2_console_id)
        tab_3_regmap.handler_console(sender=None, app_data=reset_key, user_data=tab3_console_id)
        
    elif dpg.is_key_down(dpg.mvKey_F6):
        tab_1_i2c.handler_interface_connection(sender="btn_connect", app_data=None, user_data=None)
        
    elif dpg.is_key_down(dpg.mvKey_F12):
        dpg.stop_dearpygui()


def print_debugging(sender, app_data, user_data):

    print(f"[print debugging messages]")
    print(f"sender = {sender}, app_data = {app_data}, user_data = {user_data}")
    print(f"shared_var.rw_interface = {shared_var.rw_interface}")
    print(f"shared_var.device = {shared_var.device}")
    print(f"shared_var.revision = {shared_var.revision}")
    print(f"shared_var.emulator = {shared_var.emulator}")
    print(f"shared_var.connect = {shared_var.connect}")
    print(f"shared_var.dict_layout = {shared_var.dict_layout}")
    print(f"shared_var.dict_project = {shared_var.dict_project}")
    
    get_tab_id = dpg.get_value("tabs")
    print(f"shared_var.list_tab = {shared_var.list_tab}, current_tab = {get_tab_id}")
    
    if dpg.is_key_down(dpg.mvKey_F9):
        tab_1_i2c.print_debugging()
    elif dpg.is_key_down(dpg.mvKey_F10):
        tab_2_user.print_debugging()
    elif dpg.is_key_down(dpg.mvKey_F11):
        tab_3_regmap.print_debugging()
        # tab_4.print_debugging()


def change_window_title():
    
    # dpg.set_item_label("main_panel", new_title)
    if shared_var.connect:
        dpg.set_viewport_title(f"Main GUI (Connected : {shared_var.emulator.upper()})")
    else:
        dpg.set_viewport_title(f"Main GUI (Not connected)")
    
    dpg.configure_item("main_panel", label=f"{shared_var.device.upper()} GUI v0.1")


if __name__ == "__main__":
    
    shared_var.root_dir    = pathlib.Path(root_dir)
    shared_var.gui_dir     = pathlib.Path(base_dir)
    shared_var.log_dir     = pathlib.Path(log_dir)
    shared_var.project_dir = pathlib.Path(project_dir)
    shared_var.layout_dir  = pathlib.Path(layout_dir)
    
    # ---------------------------------------------
    # update project & revision
    # ---------------------------------------------
    for file in os.listdir(shared_var.layout_dir):
        if "xlsx" in file:
            file_split = file.split("_")
            shared_var.dict_layout[file_split[0]] = file_split[1]
            
    for project in os.listdir(shared_var.project_dir):
        item_path = os.path.join(project_dir, project)
        if os.path.isdir(item_path) and "__" not in project:
            shared_var.dict_project[project] = item_path
        
    # default setting
    shared_var.device = list(shared_var.dict_layout.keys())[0]
    shared_var.revision = shared_var.dict_layout[shared_var.device]
    # ---------------------------------------------
    
    dpg.create_context()

    # shortcut handler
    with dpg.handler_registry():
        dpg.add_key_press_handler(
            dpg.mvKey_Q,
            callback=close_gui
            )

        var.l_shift_sts = False
        
        # make simple to shorten the delay
        def ctrl_down(sender, app_data):
            if var.l_shift_sts == False:
                var.l_shift_sts = True
            else:
                pass
            
        def ctrl_up(sender, app_data):
            var.l_shift_sts = False

        dpg.add_key_down_handler(dpg.mvKey_LShift, callback=ctrl_down)
        dpg.add_key_release_handler(dpg.mvKey_LShift, callback=ctrl_up)
        dpg.add_key_press_handler(dpg.mvKey_LShift, callback=switch_tab, user_data=var.l_shift_sts)
        
    create_ui()
    
    dpg.create_viewport(
        title="Main GUI (Not connected)",
        width=1200+20,
        height=shared_var.height+45
        )
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

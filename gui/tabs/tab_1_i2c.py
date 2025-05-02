from interface.cui_logger import logger as log

import importlib, sys
import dearpygui.dearpygui as dpg

# to use the global variable "rw_interface"
# import gui.main as main
# from gui.main import dev_info

from gui.main import change_window_title
from gui.shared_space import shared_var
import gui.tabs.tab_2_user as tab_2
import gui.tabs.tab_3_regmap as tab_3

import hid
import os

# garbage collection
import gc


class var:
    
    tab1_tag = "id_tab_1"
    
    id_console = None
    
    '''
    --------------------------------------------------------
    [id_group format]
        var.id_group["radio_dongle"]   = id_dongles
        var.id_group["btn_connect"]    = id_btn_connect
        var.id_group["btn_disconnect"] = id_btn_disconnect

        var.id_group["btn_scan"]        = id_btn_scan
        var.id_group["btn_hid"]         = id_btn_hid
        var.id_group["btn_i2c_address"] = id_btn_i2c_address
        var.id_group["txt_i2c_address"] = id_txt_i2c_address

        var.id_group["txt_read_addr"]   = id_txt_read_addr
        var.id_group["btn_i2c_read"]    = id_btn_i2c_read
        var.id_group["txt_write_addr"]  = id_txt_write_addr
        var.id_group["txt_write_value"] = id_txt_write_value
        var.id_group["btn_i2c_write"]   = id_btn_i2c_write
    --------------------------------------------------------
    tag has same value with the var.id_group.keys()
    --------------------------------------------------------
    '''
    id_group   = dict()
    
    id_i2c_scan = None
    id_hid_scan  = None
    id_set_i2c  = None
    id_i2c_rw   = dict()
    id_connection_section = dict() # store the id data for radio_dongle, btn_connect and btn_disconnect
    
    list_i2c_scan = list()


def print_debugging():
    
    # print(f"[tab1] var.id_group = {var.id_group}")
    # print(f"[tab1] var.id_i2c_scan = {var.id_i2c_scan}")
    # print(f"[tab1] var.id_set_i2c = {var.id_set_i2c}")
    # print(f"[tab1] var.id_connection_section = {var.id_connection_section}")
    print(f"[tab1] var.list_i2c_scan = {var.list_i2c_scan}")
    

def handler_interface_connection(sender, app_data, user_data):
    
    if "radio_dongle" in sender:
        
        shared_var.emulator = app_data.lower() # store the the selected i2c emulator
        handler_console(sender, f"select the i2c emulator : {shared_var.emulator.upper()}", var.id_console)
    
    elif "btn_connect" in sender:
        
        reinitialize()
        
        if shared_var.connect:
            
            module_name = module.__name__
            if module_name in sys.modules:
                del sys.modules[module_name]
            del module
            gc.correct()

        module_path = f"project.{shared_var.device.lower()}"
        module = importlib.import_module(module_path)
        # module = importlib.import_module(module_path, package=project)
        
        if shared_var.connect:
            handler_console(sender, f"already connected to the emulator", var.id_console)
        
        else:
            
            hid_list = hid_scan()
            
            if any("CP2112" in item for item in hid_list):
                
                if "CP2112".upper() in shared_var.emulator or "CP2112".lower() in shared_var.emulator:
                    
                    # shared_var.emulator = "CP2112"
                    shared_var.rw_interface = module.project(
                        device   = shared_var.device,
                        revision = shared_var.revision,
                        emulator = shared_var.emulator.lower(),
                        logging  = shared_var.logging,
                        is_gui   = True
                        )
                    
                    shared_var.connect = True
                    change_window_title()
                    handler_console(sender, f"connected to {shared_var.emulator.upper()}", var.id_console)
                    
                    tab_2.create_contents()
                    tab_3.create_contents()
                    
                    default_i2c_address = shared_var.rw_interface.get_i2c_address()
                    dpg.set_value(var.id_group["txt_i2c_address"], f"{default_i2c_address:#04x}")
            
            else:
                handler_console(sender, f"CP2112 is NOT in the HID device list", var.id_console)
    
    elif "btn_disconnect" in sender:
        
        if shared_var.connect:
            
            reinitialize()
            tab_2.destroy_contents()
            tab_3.destroy_contents()
            
            # force garbage collection
            gc.collect()
            
        else:
            handler_console(None, f"emulator is NOT connected", var.id_console)
    
    elif "project_list" in sender:
        
        shared_var.device = app_data.split(" ")[0]
        shared_var.revision = app_data.split(" ")[1]
    
    '''
    elif "project_select" in sender:
        
        handler_console(None, f"create register tables for {shared_var.device.upper()} {shared_var.revision.upper()}", var.id_console)
        tab_2.create_contents()
    
    elif "project_deselect" in sender:
        
        reinitialize()
        handler_console(None, f"close register tables", var.id_console)
        tab_2.destroy_contents()
    '''


def reinitialize():
    
    if shared_var.connect:
        
        # explicitly delete object
        shared_var.rw_interface.close()
        del shared_var.rw_interface
        
        # reset variables     
        shared_var.rw_interface = None            
        shared_var.connect = False
        shared_var.emulator = "cp2112" # set default
        
        handler_console(None, f"disconnected I2C emulator, set default to cp2112", var.id_console)
    
    change_window_title()


def convert_int(value: str) -> int:
    
    try:
        converted_number = int(value, 0)  # auto-detects base (decimal, hex, binary, etc.)
        if converted_number < 0x100:
            return converted_number
        else:
            handler_console(None, f"invalid size : the number ({value}) must be smaller than 0x100 (256)", var.id_console)
            return None
    except:
        handler_console(None, f"invalid size : {value} has to be integer or hex", var.id_console)
        return None


# method for i2c_scan and manual read & write
def handler_rw(sender, app_data, user_data):
    
    if shared_var.connect is True:
        
        if "btn_scan" in sender:
            
            ret_address = shared_var.rw_interface.i2c_scan()
            hex_address = [f"{x:#04x}" for x in ret_address]  # convert all to hex strings
            
            if ret_address is not None:
                
                for address in ret_address:
                    handler_console(sender, f"i2c address response: {ret_address} ({hex_address})", var.id_console)
                    dpg.set_value(var.id_group["txt_i2c_address"], f"{ret_address[0]:#04x}")
                    var.list_i2c_scan.append(ret_address)
            
        elif "btn_i2c_address" in sender:
            
            i2c_addr_str = dpg.get_value(var.id_group["txt_i2c_address"])
            i2c_addr = convert_int(i2c_addr_str)
            
            if i2c_addr is not None:
                shared_var.rw_interface.update_i2c_address(i2c_addr)
                handler_console(sender, f"update I2C address to {i2c_addr:#04x} ({i2c_addr})", var.id_console)
            
        elif "btn_i2c_read" in sender:
            
            i2c_reg_str = dpg.get_value(var.id_group["txt_read_addr"])
            i2c_reg = convert_int(i2c_reg_str)
                
            if i2c_reg is not None:
                byte_read = shared_var.rw_interface.read_byte(i2c_reg)
                handler_console(sender, f"read byte {i2c_reg:#04x}={byte_read:#04x}", var.id_console)
                
        elif "btn_i2c_write" in sender:
            
            i2c_reg_str   = dpg.get_value(var.id_group["txt_write_addr"])
            i2c_value_str = dpg.get_value(var.id_group["txt_write_value"])
            i2c_reg   = convert_int(i2c_reg_str)
            i2c_value = convert_int(i2c_value_str)
            
            if i2c_reg is not None and i2c_value is not None:
                
                shared_var.rw_interface.write_byte(i2c_reg, i2c_value)
                handler_console(sender, f"send byte {i2c_reg:#04x}={i2c_value:#04x}", var.id_console)
        
    else:
        handler_console(None, f"emulator is NOT connected", var.id_console)


def handler_hid(sender, app_data, user_data):
    
    if "btn_hid" in sender:
        ret_hid = hid_scan()
        
        for i in ret_hid:
            handler_console(sender, f"{i}", var.id_console)


def hid_scan():
    
    hid_dev = list()
    for device in hid.enumerate():
        
        if device["manufacturer_string"] != "":
            vid = device["vendor_id"]
            pid = device["product_id"]
            item = device["manufacturer_string"] + " : " + device["product_string"] + f" (vid={vid:#06x}, pid={pid:#06x})"
            hid_dev.append(item)
            
    remove_duplicate = list(set(hid_dev))
    
    return remove_duplicate


def handler_console(sender, app_data, user_data):
    
    # user_data : console id
    # app_data : pass from caller
    
    current_text = dpg.get_value(user_data)
    
    if app_data == shared_var.reset_key:
        
        new_log = "clear console output"
        dpg.set_value(user_data, new_log)
    
    elif isinstance(app_data, dict):
        
        # console out for project & revision info
        n = 1
        for prject, revision in app_data.items():
            temp = f"\ndevice list # {n} : {prject.upper()}, {revision.upper()}"
            current_text += temp
            n += 1
        dpg.set_value(user_data, current_text)
        
    else:
    
        new_log = "\n" + f"{app_data}"
        dpg.set_value(user_data, current_text+new_log)
        
    # dpg.set_y_scroll("console_window", dpg.get_y_scroll_max("console_window")) # force vertical scrolling to bottom
    # dpg.focus_item(user_data)
    

def tab_i2c():
    
    with dpg.tab(label="Configuration", tag=var.tab1_tag):
        
        dpg.add_spacer(height=5)

        ##### parent group --> i2c emulator selection and util group
        with dpg.group(horizontal=True):

            ##### group A start --> i2c emulator connection
            with dpg.group():
                with dpg.child_window(width=200, height=200):

                    dpg.add_text(
                        default_value="I2C Emulator",
                        color=(255, 255, 0) # yellow
                        )
                    dpg.add_spacer(height=5)

                    id_dongles = dpg.add_radio_button(
                        items=["CP2112", "MCP2221", "FT200X"],
                        callback=handler_interface_connection,
                        tag="radio_dongle"
                        )
                    dpg.add_spacer(height=5)

                    id_btn_connect = dpg.add_button(
                        label="Connect (F6)",
                        width=150,
                        callback=handler_interface_connection,
                        tag="btn_connect"
                        )
                    id_btn_disconnect = dpg.add_button(
                        label="Disconnect",
                        width=150,
                        callback=handler_interface_connection,
                        tag="btn_disconnect"
                        )
                    
                    var.id_group["radio_dongle"]   = id_dongles
                    var.id_group["btn_connect"]    = id_btn_connect
                    var.id_group["btn_disconnect"] = id_btn_disconnect
                    
                    var.id_connection_section["radio_dongle"]   = id_dongles
                    var.id_connection_section["btn_connect"]    = id_btn_connect
                    var.id_connection_section["btn_disconnect"] = id_btn_disconnect
                    
            ##### group A finish

            ##### group B start --> i2c utility
            with dpg.group():
                with dpg.child_window(width=400, height=200):

                    dpg.add_text(
                        default_value="I2C Fuction",
                        color=(255, 255, 0)
                        )
                    dpg.add_spacer(height=5)

                    id_btn_scan = dpg.add_button(
                        label="I2C Bus scan",
                        width=150,
                        callback=handler_rw,
                        tag="btn_scan"
                        )
                    id_btn_hid = dpg.add_button(
                        label="HID device scan",
                        width=150,
                        callback=handler_hid,
                        tag="btn_hid"
                        )
                    dpg.add_spacer(height=5)
                    
                    with dpg.group(horizontal=True, horizontal_spacing=3):
                        id_btn_i2c_address = dpg.add_button(
                            label="Set I2C address",
                            width=150,
                            callback=handler_rw,
                            tag="btn_i2c_address"
                            )
                        id_txt_i2c_address = dpg.add_input_text(
                            default_value="0x00",
                            width=231,
                            callback=handler_rw,
                            tag="txt_i2c_address"
                            )
                    dpg.add_spacer(height=5)
                    
                    var.id_group["btn_scan"] = id_btn_scan
                    var.id_group["btn_hid"]  = id_btn_hid
                    var.id_group["btn_i2c_address"] = id_btn_i2c_address
                    var.id_group["txt_i2c_address"] = id_txt_i2c_address
                    
                    var.id_i2c_rw["i2c_address"] = id_txt_i2c_address
                    var.id_i2c_scan = id_btn_scan
                    var.id_hid_scan = id_btn_hid
                    var.id_set_i2c = id_btn_i2c_address
                    
                    ##### start A table --> manual read and writing
                    with dpg.table(
                        header_row=True,
                        resizable=False,
                        borders_innerH=False,
                        borders_innerV=True,
                        borders_outerH=True,
                        policy=dpg.mvTable_SizingFixedFit
                        ):
                        
                        # define columns with fixed widths
                        column_width = 100
                        
                        dpg.add_table_column(
                            label="Address",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Value",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label=" ",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )

                        # 1st row
                        with dpg.table_row():
                            id_txt_read_addr = dpg.add_input_text(
                                default_value="0x00",
                                width=column_width,
                                tag="txt_read_addr"
                                )
                            dpg.add_text("N/A")
                            id_btn_i2c_read = dpg.add_button(
                                label="R",
                                callback=handler_rw,
                                tag="btn_i2c_read"
                                )
                        
                        # 2nd row
                        with dpg.table_row():
                            id_txt_write_addr = dpg.add_input_text(
                                default_value="0x00",
                                width=column_width,
                                tag="txt_write_addr"
                                )
                            id_txt_write_value = dpg.add_input_text(
                                default_value="0x00",
                                width=column_width,
                                tag="txt_write_value"
                                )
                            id_btn_i2c_write = dpg.add_button(
                                label="W",
                                callback=handler_rw,
                                tag="btn_i2c_write"
                                )
                            
                        var.id_group["txt_read_addr"]   = id_txt_read_addr
                        var.id_group["btn_i2c_read"]    = id_btn_i2c_read
                        var.id_group["txt_write_addr"]  = id_txt_write_addr
                        var.id_group["txt_write_value"] = id_txt_write_value
                        var.id_group["btn_i2c_write"]   = id_btn_i2c_write
                        
                        var.id_i2c_rw["r_addr"]  = id_txt_read_addr
                        var.id_i2c_rw["r_click"] = id_btn_i2c_read
                        var.id_i2c_rw["w_addr"]  = id_txt_write_addr
                        var.id_i2c_rw["w_value"] = id_txt_write_value
                        var.id_i2c_rw["w_click"] = id_btn_i2c_write
                        
                    ##### table A finish
            ##### group B finish
        ##### parent group finish

        dpg.add_spacer(height=5)
        
        n_project = len(shared_var.dict_layout.keys())
        # 50 : header height for child_window
        # 20 * n_project : dynamically assign the hegith number
        
        # project selection
        with dpg.group():
            with dpg.child_window(width=600+8, height=50+25*n_project, tag="project_selection"):
                
                with dpg.group(horizontal=True, horizontal_spacing=10):
                     
                    dpg.add_text(
                        default_value="Scanned list",
                        color=(255, 255, 0) # yellow
                        )
                    
                    with dpg.theme() as color_table_update:
                        with dpg.theme_component(dpg.mvButton):
                            dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 30, 10, 150])  # default blue color (RGBA)
                            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 150, 30, 150])  # on hover
                            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 200, 150])  # even brighter when clicked
                    
                    '''
                    dpg.add_button(
                        label="Open Project",
                        user_data="project_select",
                        callback=handler_interface_connection,
                        tag=f"project_select"
                        )
                    
                    dpg.add_button(
                        label="Close Project",
                        user_data="project_deselect",
                        callback=handler_interface_connection,
                        tag=f"project_deselect"
                        )
                    '''
                
                dpg.add_spacer(height=5)
                
                item_list = list()
                for p, r in shared_var.dict_layout.items():
                    item_list.append(f"{p.upper()} {r.upper()}")
                
                dpg.add_radio_button(
                    items=item_list,
                    callback=handler_interface_connection,
                    tag="project_list"
                    )
                dpg.add_spacer(height=5)
                
        dpg.add_spacer(height=5)
        
        
        # console box group
        with dpg.group():
            with dpg.child_window(width=600+8, height=200, tag="console_window"):
                # add 8px due to the horizontal spacer between the childwindows 
                var.id_console = dpg.add_input_text(
                    multiline=True,
                    readonly=True,
                    width=600,
                    height=180,
                    default_value="[Output console] clear shortcut : F5"
                )
        
        handler_console(None, f"default the i2c emulator : {shared_var.emulator}", var.id_console)
        
        dpg.add_spacer(height=5)
        
        with dpg.group():
            with dpg.child_window(width=600+8, height=30):
                dpg.add_text("-"*82) # dummy
    
    # return the id of the tab
    return var.tab1_tag
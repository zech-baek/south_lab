import dearpygui.dearpygui as dpg

# import gui.main as main
# from gui.main import dev_info

from project.get_device_info import get_map
from gui.layout.layout_form import tab_form
from gui.shared_space import shared_var

import re

# garbage collection
import gc


'''------------------------------------------------------------------------------
structure
---------------------------------------------------------------------------------
with dpg.tab():
    dpg.add_button(label="update all")
    with dpg.group():
        for group in [group_a, group_b]:
            if group == group_a : table_item = table_item_a
            elif group == group_b : table_item = table_item_b
        with dpg.group():
            with dpg.child_window()
                for table_title, register_list in table_item.items():
                    dpg.add_text(defautl_value=table_title)
                    dpg.add_button(label="update table")
                with dpg.table():
                    dpg.add_table_column(lable="Register")
                    dpg.add_table_column(lable="Type")
                    dpg.add_table_column(lable="Length")
                    dpg.add_table_column(lable="Value")
                    for register in register_list:
                        with dpg.table_row():
                            dpg.add_text(register)
                            dpg.add_text(register["rw"])
                            dpg.add_text(register["length"])
                            # get the list_value_suffix
                            # divide list_value_1st_suffix, list_value_2nd_suffix
                            if "textbox":
                                with dpg.group():
                                    dpg.add_intput_text()
                                    dpg.add_button("r" or "r" with "w")
                            else:
                                if "dropdown":
                                    dpg.add_combo(items=list_value_suffix)
                                elif "selectable":
                                    for select_group in [list_value_1st_suffix, list_value_2nd_suffix]:
                                        with dpg.group():
                                            for select_item in select_group:
                                                dpg.add_selectable()
------------------------------------------------------------------------------'''



class var:
    
    tab2_tag = "id_tab_2"
    id_console = None # id for output console
    selected_item = None # global variable to track the selected item from dpg.add_selectable()
    
    '''------------------------
    [id_group_table format]
        156:
        - DAC
        - F_OS
        - F_PN
        210:
        - MODEL_ID
        - DEV_ID
    ------------------------'''
    id_group_table = dict()
    
    '''------------------------
    [id_group_register format]
        ARRC:
            id_item: 
                selectable_ARRC_0
                selectable_ARRC_1
            selected: null
            style: selectable
        ARRCM:
            id_item: dropdown_ARRCM
            style: dropdown
        BUSY:
            id_r: 147
            id_textbox: text_BUSY
            r_only: true
            style: textbox
        D:
            id_r: 125
            id_textbox: text_D
            id_w: 126
            r_only: false
            style: textbox
    ------------------------'''
    id_group_register = dict()
    tag_group = list() # purpose for dynamic create or destroy


def print_debugging():
    
    print(f"[tab2] selected_item = {var.selected_item}")
    # print(f"[tab2] id_group_table = {var.id_group_table}")
    # print(f"[tab2] id_group_register = {var.id_group_register}")
    print(f"[tab2] tag_group = {var.tag_group}")


def update_unit(reg_name, reg_property):
    
    selection_style = reg_property["style"]
    id_item = reg_property["id_item"]
    read_register_value = getattr(shared_var.rw_interface, reg_name)
    
    # handler_console(sender, f"{register} : sender={sender}, app_data={app_data}, user_data={user_data}, id_item={id_item}, reg_value={read_register_value}", var.id_console)
    
    try:
        
        if "textbox" in selection_style:
            
            dpg.set_value(id_item, f"{read_register_value:#04x}")
            
        elif "dropdown" in selection_style:
            
            selection_list = reg_property["lists"]
            dpg.set_value(id_item, selection_list[read_register_value])

        elif "selectable" in reg_property["style"]:
            
            target_selectable_id = reg_property["id_item"].get(read_register_value)
            
            # release all selectable options
            for temp in id_item.values():
                dpg.set_value(temp, False)
                
            # handler_console(None, f"[debug] {reg_property['id_item']}, {target_selectable_id}, reg={read_register_value}", var.id_console)
            
            # select the target item
            dpg.set_value(target_selectable_id, True)
            
            # sender : "button_update_all_tab2"
            # app_data : None
            # user_data : "update_all"
            # id_item : selectable_ARRC_1, selectable_PE_1, selectable_PD_1, selectable_IMAX_7, selectable_UMODE_1
        
        handler_console(None, f"read {reg_name}={read_register_value:#x}", var.id_console)
    
    except:
        
        handler_console(None, f"error, invalid {reg_name} property", var.id_console)


def handler_update_register(sender, app_data, user_data):
    
    # utilize id_group_register
    
    # handler_console(sender, f"[debug] enter to update handler : sender={sender}, app_data={app_data}, user_data={user_data}", var.id_console)
    
    if shared_var.connect is True:
        
        # read the register value from the device
        # update the corresponding item from the id
        if "button_update_all_tab2" in sender:
            
            handler_console(sender, f"start register update", var.id_console)
        
            for register, config in var.id_group_register.items():
                update_unit(reg_name=register, reg_property=config)
        
        elif "update_table" in sender: # format for the update table button : "update_table{n_table}"
            
            for id_table, register in var.id_group_table.items():
                
                if sender == id_table:
                    
                    for unit in register:
                        update_unit(reg_name=unit, reg_property=var.id_group_register[unit])
        
        elif "dropdown" in sender:
            
            splitted_data = app_data.split(" ")[0]
            write_value = int(splitted_data, 0)  # automatically convert the int string of hex string to integer
            setattr(shared_var.rw_interface, user_data, write_value)
            
            id_item = var.id_group_register[user_data]["id_item"]
            selection_list = var.id_group_register[user_data]["lists"]
            dpg.set_value(id_item, selection_list[write_value])
            
            handler_console(sender, f"write {user_data}={write_value:#x}", var.id_console)
        
        # elif "read_" in sender or "write_" in sender:
        else:
            
            register = user_data
            id_textbox = var.id_group_register[register]["id_item"]
            
            if "read_" in sender:
                
                read_value = getattr(shared_var.rw_interface, register)
                dpg.set_value(id_textbox, f"{read_value:#x}")
                handler_console(None, f"read {register}={read_value:#x}", var.id_console)
            
            elif "write_" :
                
                write_value = int(dpg.get_value(id_textbox), 0)
                reg_map = shared_var.rw_interface.get_regmap()
                max_bits = max(value for key, value in reg_map[register].items() if "bit" in key) + 1
                value_limit = (2**max_bits) - 1
                
                if write_value > value_limit:
                    handler_console(None, f"{write_value:#x} exceed the limit {value_limit:#x} ({value_limit})", var.id_console)
                
                else:
                    setattr(shared_var.rw_interface, user_data, write_value)
                    handler_console(sender, f"write {register}={write_value:#x}", var.id_console)
                
            # handler_console(sender, f"[debug] handler : sender={sender}, app_data={app_data}, user_data={user_data}", var.id_console)
                
    else:
        handler_console(None, f"emulator is NOT connected", var.id_console)


def handler_selectable(sender, app_data, user_data):
    
    # important note ----------
    # tag substitutes sender
    # ----------------------
    
    # register name = user_data
    # sender format : f"selectable_{register name}_{value}
    # var.id_group_register[user_data]["id_item"] : all ids for selection option
    
    if shared_var.connect is True:
        
        write_value = int(sender.split("_")[-1])
        setattr(shared_var.rw_interface, user_data, write_value)
        
        # deselect all/previous item
        for temp in var.id_group_register[user_data]["id_item"].values():
            dpg.set_value(temp, False)
            
        # highlight the clicked item
        dpg.set_value(sender, True)
        
        # update the selected item
        var.selected_item = sender
        
        handler_console(sender, f"write {user_data}={write_value:#x}", var.id_console)
    
    else:
        handler_console(None, f"emulator is NOT connected", var.id_console)


def handler_console(sender, app_data, user_data):
    
    # user_data : console id
    # app_data : pass from caller
    
    if app_data == shared_var.reset_key:
        
        new_log = "clear console output\n"
        dpg.set_value(user_data, new_log)
        
    else:
    
        current_text = dpg.get_value(user_data)
        new_log = "\n" + f"{app_data}"
        dpg.set_value(user_data, current_text+new_log)


def split_list(lst):

    mid = len(lst) // 2  # calculate quotient, find the middle index
    return lst[:mid], lst[mid:]


def update_tab_id():
    
    print(f"get tab id _ #2 : {shared_var.list_tab}")    
    get_tab_id = dpg.get_value("tabs")
    shared_var.list_tab["tab2"].update({"tab_id" : get_tab_id})
    print(f"get tab id _ #2 : {get_tab_id}, {shared_var.list_tab}")


def tab_user():
    
    with dpg.tab(label="User", tag=var.tab2_tag):
        # return the id of the tab
        return var.tab2_tag


def create_contents():
    
    # if the items alread exists, delete it before create
    for tag in var.tag_group:
        if dpg.does_item_exist(var.tag_group):
            dpg.delete_item(tag)
    
    #----------------------------------------
    excel_file = shared_var.gui_dir/f"layout/{shared_var.device}_{shared_var.revision}_layout.xlsx"
    
    reg_map = get_map(shared_var.device, shared_var.revision)
    layout = tab_form(file=excel_file, reg_map=reg_map)
    
    # total list items in the group
    group_a, group_b = layout.get_layout_table()
    
    # get the table title
    sub_group_a, sub_group_b = layout.get_sub_group()
    
    # get the dictionary : table title (key), register name (value)
    table_item_a, table_item_b = layout.get_table_item()
    
    layout.close()
    gc.collect()
    #----------------------------------------
    
    dpg.add_spacer(height=5, parent=var.tab2_tag, tag="spacer_tab2_1")
    var.tag_group.append("spacer_tab2_1")

    with dpg.theme() as color_all_update:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 30, 10, 150])  # default blue color (RGBA)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [100, 30, 30, 150])  # on hover
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 200, 150])  # even brighter when clicked
        
    id_all_update = dpg.add_button(
        parent=var.tab2_tag,
        label="Update all registers (F2)",
        width=280,
        user_data="update_all",
        tag=f"button_update_all_tab2",
        callback=handler_update_register
        )

    dpg.bind_item_theme(id_all_update, color_all_update)
    
    dpg.add_spacer(height=5, parent=var.tab2_tag, tag="spacer_tab2_2")
    var.tag_group.extend(["button_update_all_tab2", "spacer_tab2_2"])

    ##### parent group
    with dpg.group(
        parent=var.tab2_tag,
        horizontal=True,
        tag="group_tab2_1"):
        
        n_table = 0 # to give a number for the table id
        var.tag_group.append("group_tab2_1")
        
        # divide group a and b            
        for group in [group_a, group_b]:
            if group == group_a:
                table_item = table_item_a
            elif group == group_b:
                table_item = table_item_b
        
            ##### main group start
            with dpg.group():
                with dpg.child_window(
                    width=550,
                    autosize_x=False,
                    autosize_y=False,
                    horizontal_scrollbar=False
                    ):
                    
                    # define columns with fixed widths
                    column_width = 100
                    
                    #----------------------------------------
                    # table_title : str
                    # register_name : list
                    #----------------------------------------

                    for table_title, register_list in sorted(table_item.items()):
                        
                        # table title
                        with dpg.group(horizontal=True, horizontal_spacing=10):
                            
                            dpg.add_text(
                                default_value=table_title,
                                color=(255, 255, 0)
                                )
                            
                            with dpg.theme() as color_table_update:
                                with dpg.theme_component(dpg.mvButton):
                                    dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 30, 10, 150])  # default blue color (RGBA)
                                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 150, 30, 150])  # on hover
                                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 200, 150])  # even brighter when clicked
                                
                            id_table_update = dpg.add_button(
                                label="Update table",
                                user_data="update_table",
                                callback=handler_update_register,
                                tag=f"update_table_{n_table}"
                                )
                            
                            n_table += 1
                            dpg.bind_item_theme(id_table_update, color_table_update)
                            
                            # store the id : register list for update the table function
                            var.id_group_table[id_table_update] = register_list

                        # total length = 100 x 4 + 150
                        with dpg.table(
                            header_row=True,
                            resizable=False,
                            borders_innerH=True,
                            borders_innerV=True,
                            borders_outerH=True,
                            policy=dpg.mvTable_SizingFixedFit
                            ):
                            
                            #----------------------------------------
                            # table header
                            #----------------------------------------
                            dpg.add_table_column(
                                label="Register",
                                init_width_or_weight=column_width+20,
                                width_fixed=True
                                )
                            dpg.add_table_column(
                                label="Type",
                                init_width_or_weight=column_width-30,
                                width_fixed=True
                                )
                            dpg.add_table_column(
                                label="Length",
                                init_width_or_weight=column_width-50,
                                width_fixed=True
                                )
                            dpg.add_table_column(
                                label="Value",
                                init_width_or_weight=column_width+190,
                                width_fixed=True
                                )
                            #----------------------------------------
                            
                            #----------------------------------------
                            # row for the register
                            #----------------------------------------
                            for register in sorted(register_list):
                                
                                with dpg.table_row():
                                    
                                    # 3 items from first cell
                                    dpg.add_text(register)
                                    dpg.add_text(group[register]["rw"])
                                    dpg.add_text(group[register]["length"])
                                    
                                    # [case 1] read-only or rw
                                    #   - add_input_text()
                                    #   - if it's read-only, other selection option will be ignored
                                    # [case 2] rw & dropdown
                                    #   - drop-down with hex value or comment
                                    #   - var : list_value_suffix
                                    # [case 3] rw & selectable
                                    #   - hex value (with comment, optional)
                                    #   - list_value_1st_suffix, list_value_2nd_suffix
                                    
                                    #-----------------------------------------------------------------------------
                                    # variables for the value selection
                                    # two types of styles will be used for value display : list_value_suffix
                                    # 1. "int (hex)"
                                    # 2. "hex (description)"
                                    #-----------------------------------------------------------------------------
                                    # list_value : list of int
                                    # list_value_suffix : list of "int (hex)"
                                    # list_1st, list_2nd : divide list_value into 2 groups
                                    # list_value_1st_suffix, list_value_2nd_suffix : split list_value_suffix into 2 lists
                                    #-----------------------------------------------------------------------------
                                    
                                    register_rw = group[register]["rw"]
                                    length = group[register]["length"]
                                    length_style = len(group[register]["style"])
                                    list_value = [i for i in range(2**length)]
                                    
                                    list_value_suffix = list()
                                    
                                    if length_style == 0:
                                        list_value_suffix = [f"{item} (0x{i:x})" for i, item in enumerate(list_value)]
                                    else:
                                        for entry in group[register]["style"]:
                                            # extract the prefix (can be int or hex) and suffix (text)
                                            match = re.match(r'(\d+|0x[0-9A-Fa-f]+),\s*(.*)', entry)
                                            
                                            if match:
                                                prefix, suffix = match.groups()
                                                # convert prefix to integer and back to hex (ensuring uniform 0x format)
                                                hex_value = f"0x{int(prefix, 0):x}"  # int(prefix, 0) : auto-detects base
                                                list_value_suffix.append(f"{hex_value} ({suffix})")
                                                
                                    list_value_1st, list_value_2nd = split_list(list_value)
                                    list_value_1st_suffix, list_value_2nd_suffix = split_list(list_value_suffix)
                                    #-----------------------------------------------------------------------------
                                    
                                    # case 1 : input-text
                                    if group[register]["selection"] == "textbox" or register_rw == "R":
                                        
                                        is_readonly = False if "W" in register_rw else True
                                        
                                        with dpg.group(horizontal=True, horizontal_spacing=3):
                                            
                                            id_textbox = dpg.add_input_text(
                                                default_value="0x00",
                                                readonly=is_readonly,
                                                tag=f"text_{register}",
                                                width=216
                                                )
                                            id_r_button = dpg.add_button(
                                                label="R",
                                                user_data=register,
                                                callback=handler_update_register,
                                                tag=f"read_{register}"
                                                )
                                            
                                            var.id_group_register[register] = {
                                                "style"   : "textbox",
                                                "id_item" : id_textbox,
                                                "r_only"  : True,
                                                "id_r"    : id_r_button
                                            }
                                            
                                            if "W" in register_rw:
                                                id_w_button = dpg.add_button(
                                                    label="W",
                                                    user_data=register,
                                                    callback=handler_update_register,
                                                    tag=f"write_{register}"
                                                    )
                                                
                                                var.id_group_register[register].update(
                                                    {"id_w"   : id_w_button,
                                                        "r_only" : False
                                                        }
                                                    )
                                        
                                    else:
                                        # case 2 : drop-down
                                        if group[register]["selection"] == "dropdown":
                                            id_combo = dpg.add_combo(
                                                label=None,
                                                width=251,
                                                items=list_value_suffix,
                                                default_value=list_value_suffix[0],
                                                user_data=register,
                                                tag=f"dropdown_{register}",
                                                callback=handler_update_register
                                                )
                                            
                                            var.id_group_register[register] = {
                                                "style"   : "dropdown",
                                                "id_item" : id_combo,
                                                "lists"   : list_value_suffix
                                            }
                                        
                                        # case 3 : selectable
                                        elif group[register]["selection"] == "selectable":
                                            with dpg.group(horizontal=True, horizontal_spacing=5):
                                                
                                                id_set_temp = dict()
                                                
                                                for select_group in [list_value_1st_suffix, list_value_2nd_suffix]:
                                                    
                                                    with dpg.group():
                                                        
                                                        # allocate the list_value with suffix to the selectable item
                                                        # e.g.
                                                        #   register : ARRC
                                                        #   split_item : 0x0, 0x1
                                                        #   select_item : "0x0 (enable)", "0x1 (disable)" <-- enumerate the select_group from list_value_suffix
                                                        #   tag_item : 0, 1
                                                        #   id_select : selectable_ARRC_0, selectable_ARRC_1
                                                        for select_item in select_group:
                                                            
                                                            split_item = select_item.split()[0] # tag should be unique value
                                                            tag_item=int(split_item, 16) if split_item.startswith("0x") else int(split_item)
                                                            
                                                            id_select = dpg.add_selectable(
                                                                label=select_item,
                                                                user_data=register,
                                                                width=118,
                                                                tag=f"selectable_{register}_{tag_item}",
                                                                callback=handler_selectable
                                                                )
                                                            
                                                            id_set_temp.update({tag_item : id_select})
                                                            
                                                    var.id_group_register[register] = {
                                                        "style"    : "selectable",
                                                        "selected" : None
                                                    }
                                                    var.id_group_register[register].update({"id_item" : id_set_temp})
    
    dpg.add_spacer(height=5, parent=var.tab2_tag, tag="spacer_tab2_3")
                                                        
    # console box group
    with dpg.group(parent=var.tab2_tag):
        with dpg.child_window(
            width=550+550+8,
            height=200,
            autosize_x=False,
            autosize_y=False,
            horizontal_scrollbar=False,
            tag="group_tab2_2"
            ):
            # add 8px due to the horizontal spacer between the childwindows 
            var.id_console = dpg.add_input_text(
                multiline=True,
                readonly=True,
                width=550+550+22,
                height=180,
                default_value="[Output console] clear shortcut : F5"
            )
    
    dpg.add_spacer(height=5, parent=var.tab2_tag, tag="spacer_tab2_4")
    
    with dpg.group(parent=var.tab2_tag, tag="group_tab2_3"):
        with dpg.child_window(width=550+550+8, height=30):
            dpg.add_text("-"*153) # dummy
    
    var.tag_group.extend(["spacer_tab2_3", "group_tab2_2", "spacer_tab2_4", "group_tab2_3"])


def destroy_contents():
    
    for tag in var.tag_group:
        dpg.delete_item(tag)
        
    var.tab2_tag = "id_tab_2"
    var.id_console = None
    var.selected_item = None
    var.id_group_table = dict()
    var.id_group_register = dict()
    var.tag_group = list()
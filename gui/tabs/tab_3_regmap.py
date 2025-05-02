import dearpygui.dearpygui as dpg

from project.get_device_info import get_map, get_reg_table
from interface.cui_logger import logger as log

# to use the global variable "rw_interface"
# can access the variable "rw_interface" through "shared_var.rw_interface"
# import gui.main as main
# from gui.main import dev_info

from gui.shared_space import shared_var


'''
sorting the regmap
1. generate the dictionary
2. append the address to key
3. generate dummy list for [register, type, length] to all keys --> "reserved" for register name
4. update the list --> add suffix as the bit number if it's multibit register
5. apply the dictionary into the table
'''


class var:
    
    tab3_tag = "id_tab_3"
    
    cell_theme = dict()
    bit_table  = dict() # key=bit cell id, value=read value
    id_console = None
    id_update_table = dict() # key=address, value=[previous, current, [id for bit7~0]]
    tag_group = list()


def print_debugging():
    
    # print(f"[tab3] var.cell_theme =  {var.cell_theme}")
    # print(f"[tab3] var.bit_table = {var.bit_table}")
    # print(f"[tab3] var.id_update_table =  {var.id_update_table}")
    print(f"[tab3] var.tag_group =  {var.tag_group}")


# if there's NOT passing any user_data when registering the handler,
# then the callback should have only two parameters (sender, app_data)
def handler_color_change(sender, app_data, user_data):
    
    # Create themes for red and blue text
    with dpg.theme() as cyan_theme:
        with dpg.theme_component(dpg.mvSelectable):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (0x00, 0xff, 0xff))  # cyan text

    with dpg.theme() as silver_theme:
        with dpg.theme_component(dpg.mvSelectable):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (0x7b, 0x7d, 0x7d))  # silver text
    
    if user_data[0]: # clicked
        if "RW" in user_data[1]:
            # current_theme = var.cell_theme.get(sender, silver_theme) # find the value for sender, if not exist, return second parameter
            new_theme = cyan_theme if app_data is True else silver_theme
            var.cell_theme[sender] = new_theme
            dpg.bind_item_theme(sender, new_theme)
            if app_data is True:
                var.bit_table[sender] = True
            else:
                var.bit_table[sender] = False
            # handler_console(sender, f"sender={sender} app_data={app_data}", var.id_console)
        else:
            handler_console(sender, f"Type {user_data}, deny changes to the register data", var.id_console)
    
    # indirect function call
    # update both the selectable state (app_data) and the theme
    # dpg.set_value() does not work for dpg.add_selectable() because Selectable does not store its selection state in a way that set_value() can modify
    elif user_data[0] == False and "update" in user_data[1]:
        new_theme = cyan_theme if app_data is True else silver_theme
        var.cell_theme[sender] = new_theme
        dpg.bind_item_theme(sender, new_theme)
        # handler_console(sender, f"update the register : sender {sender}", var.id_console)


def handler_update_register(sender, app_data, user_data):
    
    '''
    1. read / update all : read byte -> cell color change based on read value -> previous/current value change
    2. write : get_value from var.id_update_table[address][2] -> write via i2c -> color change based on read value -> previous/current value change
    '''
    
    if shared_var.connect:
        
        # user_data of dpg.add_selectable : list
        # user_data of dpg.add_button for update all : str
        if isinstance(user_data, list) and "write" in user_data[0]:
            address = user_data[1]
            list_id_bits = var.id_update_table[address][2] # list_id_bits
            
            byte_data = 0
            
            # for bit in range(8):
            #     bit_shift = 7-bit
                # get_bit = dpg.get_value(var.id_update_table[address][2][bit]) << bit_shift
                # byte_data += get_bit
            
            for index in range(8):
                cell_id = list_id_bits[index]
                byte_data += var.bit_table[cell_id] << (7-index)
                # print(f"{byte_data}, id {list_id_bits}, shift {7-index}")
                
            shared_var.rw_interface.write_byte(address, byte_data)
            
            handler_console(sender, f"write byte {user_data[1]:#04x}={byte_data:#04x}", var.id_console)
            
        else:
            
            if sender == "update_all_button_tab3":
                handler_console(sender, f"start register update", var.id_console)
                loop_header = var.id_update_table
                
            elif isinstance(user_data, list) and user_data[0]=="read":
                loop_header = {user_data[1]:var.id_update_table[user_data[1]]} # format --> address : [previous id, current id, [bits id]]
                
            for address, previous_current in loop_header.items():
                
                returen_byte = shared_var.rw_interface.read_byte(address)
                old_value = dpg.get_value(previous_current[1]) # read current value to move to previous
                dpg.set_value(previous_current[0], old_value)
                dpg.set_value(previous_current[1], f"{returen_byte:#04x}")
                
                if old_value != f"{returen_byte:#04x}":
                    dpg.configure_item(previous_current[1], color=(0xff, 0xff, 0))
                else:
                    dpg.configure_item(previous_current[1], color=(0xff, 0xff, 0xff))
                
                for n_shift in range(7, -1, -1):
                    shifted_bit = (returen_byte>>n_shift) & 0x01
                    id_bit = previous_current[2][7-n_shift]
                    
                    # it looks shifted_bit doesn't mean the True of False
                    if shifted_bit == 1:
                        app_variable = True
                    else:
                        app_variable = False
                    
                    var.bit_table[id_bit] = app_variable # store the boolean value, not acutual number
                    
                    handler_color_change(sender=id_bit, app_data=app_variable, user_data=[False, "update"]) # user_data=[clicked, updated method]
                
                handler_console(sender, f"read byte {address:#04x}={returen_byte:#04x}", var.id_console)
    
    else:
        handler_console(sender, f"canceled, emulator is NOT connected to the GUI", var.id_console)
            
    
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


def type_check(value):
    
    if value is None or value == "":
        
        # print(f"[error] None or empty value : {value}")
        return "type_error"
        
    else:
        try:
            converted_value = int(str(value), 0)
            return converted_value
        
        except ValueError:
            # print(f"[error] invalid value : {value}")
            return "type_error"


def update_tab_id():
    
    print(f"get tab id _ #3 : {shared_var.list_tab}")    
    get_tab_id = dpg.get_value("tabs")
    shared_var.list_tab["tab3"].update({"tab_id" : get_tab_id})
    print(f"get tab id _ #3 : {get_tab_id}, {shared_var.list_tab}")


def tab_regmap():
    
    with dpg.tab(label="Register map", tag=var.tab3_tag):
        # return the id of the tab
        return var.tab3_tag


def create_contents():
    
    '''
    - extract the regmap
    - separate the maps into the dictionary
    '''
    
    # if the items alread exists, delete it before create
    for tag in var.tag_group:
        if dpg.does_item_exist(var.tag_group):
            dpg.delete_item(tag)
    
    #--------------------------------------------------
    regmap = get_map(shared_var.device, shared_var.revision)
    regmap_user, regmap_test, regmap_efuse = {}, {}, {}

    for key, value in regmap.items():
        permissions = value["permission"]
        if "User" in permissions:
            regmap_user[key] = value
        if "Test" in permissions:
            regmap_test[key] = value
        if "eFuse" in permissions:
            regmap_efuse[key] = value
            
    perm_group = list({value["permission"] for value in regmap.values()}) # make set to remove duplicated value
    reg_table = get_reg_table(shared_var.device, shared_var.revision)
    #--------------------------------------------------

    dpg.add_spacer(height=5, parent=var.tab3_tag, tag="spacer_tab3_1")
    var.tag_group.append("spacer_tab3_1")
    
    dpg.add_button(
        parent=var.tab3_tag,
        label="Update all registers (F3)",
        width=280,
        user_data="update_all_button_tab3",
        callback=handler_update_register,
        tag="update_all_button_tab3"
        )
    
    dpg.add_spacer(height=5, parent=var.tab3_tag, tag="spacer_tab3_2")

    dpg.add_text(f"Register map for {shared_var.device}_{shared_var.revision}", parent=var.tab3_tag, tag="taxt_tab3_1")
    
    var.tag_group.extend(["update_all_button_tab3", "spacer_tab3_2", "taxt_tab3_1"])
    
    with dpg.table(
        parent=var.tab3_tag,
        header_row=True,
        resizable=False,
        borders_outerH=True,
        borders_innerH=False,
        borders_innerV=True,
        width=1200-50,
        tag="table_tab3_1"
        ):

        # total 5+8 columns
        list_column = [
            "Address",
            "Register",
            "Type",
            "Previous",
            "Current"
        ]
        
        var.tag_group.append("table_tab3_1")
        
        # ------------ header section -------------
        for cell_name in list_column:
            dpg.add_table_column(label=cell_name)
            
        for cell_no in range(7, -1, -1):
            dpg.add_table_column(label=f"bit{cell_no}")
        
        dpg.add_table_column(label=f" ") # for the read and write blink button
        # -----------------------------------------
        
        # --------- table rows with cells ---------
        for key, value in reg_table.items():
            
            permission = value[13]
            
            if shared_var.hidden == True and permission != "User":
                pass
            
            else:
                with dpg.table_row():
                    
                    if "User" in permission:
                        tuple_color = (0xff, 0xff, 0xff)
                    elif "Test" in permission:
                        tuple_color = (0x7f, 0xb3, 0xd5)
                    else:
                        tuple_color = (0xf3, 0x9c, 0x12)
                    
                    converted_value = type_check(value[0])
                    
                    if converted_value != "type_error":
                                
                        dpg.add_text(
                            f"{converted_value:#04x}",
                            color=tuple_color
                            )
                        
                        # assign the value[0~12] for each table
                        
                        for n in range(1, 3):
                            dpg.add_text(
                                value[n],
                                color=tuple_color
                                )
                            
                        # previous value
                        converted_previous_value = type_check(value[3])
                        id_previous = dpg.add_text(
                                f"{converted_previous_value:#04x}",
                                color=tuple_color
                                )
                        
                        # current read value
                        converted_new_value = type_check(value[3])
                        id_current = dpg.add_text(
                                f"{converted_new_value:#04x}",
                                color=tuple_color
                                )
                        
                        with dpg.theme() as cyan_theme:
                            with dpg.theme_component(dpg.mvSelectable):
                                dpg.add_theme_color(dpg.mvThemeCol_Text, (0x00, 0xff, 0xff))  # cyan text
                                
                        with dpg.theme() as silver_theme:
                            with dpg.theme_component(dpg.mvSelectable):
                                dpg.add_theme_color(dpg.mvThemeCol_Text, (0x7b, 0x7d, 0x7d))  # silver text
            
                        # bit7 ~ 0
                        list_id_bits = list()
                        for m in range(5, 13):
                            cell_text = value[m]
                            cell_id = dpg.add_selectable(
                                label=cell_text,
                                user_data=[True, value[2], value[0], 12-m], # [clicked, type, address, bit position]
                                callback=handler_color_change
                            )
                            
                            dpg.bind_item_theme(cell_id, silver_theme)
                            var.cell_theme[cell_id] = silver_theme
                            list_id_bits.append(cell_id)
                            
                        var.id_update_table[value[0]] = [id_previous, id_current, list_id_bits]
                            
                        with dpg.group(horizontal=True, horizontal_spacing=3):
                            dpg.add_button(
                                label="R",
                                user_data=["read", value[0]],
                                callback=handler_update_register
                                )
                            if "W" in value[2]:
                                dpg.add_button(
                                    label="W",
                                    user_data=["write", value[0]],
                                    callback=handler_update_register
                                    )
                    
    dpg.add_spacer(height=5, parent=var.tab3_tag, tag="spacer_tab3_3")
    
    # console box group
    with dpg.group(parent=var.tab3_tag, tag="group_tab3_1"):
        with dpg.child_window(
            width=550+550+50,
            height=200,
            autosize_x=False,
            autosize_y=False,
            horizontal_scrollbar=False
            ):
            # add 8px due to the horizontal spacer between the childwindows 
            var.id_console = dpg.add_input_text(
                multiline=True,
                readonly=True,
                width=550+550+22,
                height=180,
                default_value="[Output console] clear shortcut : F5"
            )
    
    dpg.add_spacer(height=5, parent=var.tab3_tag, tag="spacer_tab3_4")
    
    with dpg.group(parent=var.tab3_tag, tag="group_tab3_2"):
        with dpg.child_window(width=550+550+50, height=30):
            dpg.add_text("-"*159) # dummy
    
    var.tag_group.extend(["spacer_tab3_3", "group_tab3_1", "spacer_tab3_4", "group_tab3_2"])


def destroy_contents():
    
    for tag in var.tag_group:
        dpg.delete_item(tag)
        
    var.tab3_tag = "id_tab_3"
    var.cell_theme = dict()
    var.bit_table  = dict()
    var.id_console = None
    var.id_update_table = dict()
    var.tag_group = list()
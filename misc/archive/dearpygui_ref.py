####################################################################################
'''
1. conditional format : existance of objects
2. basic method for callback function
3. basic button, input box and table
'''
####################################################################################

from project.hm1300 import *
from phy.relay_16ch import relay_box
from interface.cui_logger import logger as log
from interface.cui_colors import color_rgb
import dearpygui.dearpygui as dpg

# ensure the object "ic" is defined
if "ic" not in locals() and "ic" not in globals():
    ic = project(device="hm1300", revision="aa", emulator="cp2112", logging=True)
    relay = relay_box(i2c_h=ic)


# create the context and viewport
dpg.create_context()
dpg.create_viewport(title="Tutorial", width=800, height=600)


# shared variables
id_button = None
id_function = None


# def handler_text_input(sender, app_data, user_data):
    
#     global id_button
#     input_value = app_data.strip() # get the input value
#     if input_value.isdigit(): # check if it's valid number
#         new_label = f"Channel_{input_value}"
#         dpg.set_item_label(id_button, new_label) # update the button label
#         sender_label = dpg.get_item_label(sender)
#         log.forcedLog(f"update the button label : {new_label} from {sender_label}")
#     else:
#         log.forcedLog(f"invalid type of input : {new_label}")


def handler_delay(sender, app_data, user_data):
    
    global id_button
    input_value = app_data.strip() # get the input value
    if input_value.isdigit(): # check if it's valid number
        relay.set_delay = input_value
        log.forcedLog(f"change the delay : {input_value}")
    else:
        log.forcedLog(f"invalid type of input : {input_value}")


def handler_button(sender, app_data, user_data):
    
    label = dpg.get_item_label(sender) # get the button label
    if label.startswith(f"Channel_"):
        number = label.split("_")[1]
        log.forcedLog(f"button clicked : {number}")


def handler_function(sender, app_data, user_data):
    
    global id_function
    function = dpg.get_item_label(sender)
    channel  = dpg.get_item_label(id_button)
    number = channel.split("_")[1]
    if "on" in function:
        relay.set_channel(int(number), 1)
        dpg.set_item_label(id_function, f"toggle_off")
    else:
        relay.set_channel(int(number), 0)
        dpg.set_item_label(id_function, f"toggle_on")


with dpg.window(
    label="Main Window", 
    width=780, 
    height=500):
    
    dpg.add_text(f"GUI Template V0.10")
    dpg.add_text(f"")
    
    input_label = "set relay delay"
    id_input = dpg.add_input_text(
        label=input_label,
        callback=handler_delay
    )
    dpg.add_text(f"")
    
    # assign the id to global id variable
    id_button = dpg.add_button(
        label=f"Channel_{1}",
        callback=handler_button
    )
    dpg.add_text(f"")
    
    id_function = dpg.add_button(
        label=f"toggle_on",
        callback=handler_function
    )
    dpg.add_text(f"")
    
    with dpg.table(
        header_row=True,
        resizable=False,
        borders_outerH=True,
        borders_innerH=False,
        borders_innerV=True):

        '''
        header_row     : adds a header row at the top of the table
        resizable      : allow resizing of the columns
        borders_outerH : top and bottom border line
        borders_innerH : horizontal border lines between rows
        borders_innerV : vertical border between columns
        '''

        # table columns for header
        # table can have single header
        
        for col in reversed(range(8)):
            dpg.add_table_column(label=f"Bit{col}")
        
        # table rows with cells
        for row in range(5):

            with dpg.table_row():
                dpg.add_text(f"{row:#04x}")
                
                for col in reversed(range(8)):
                    dpg.add_text(
                        default_value=f"{row:02x}h_Bit{col}",
                        indent=5,
                        bullet=False,
                        color=color_rgb.light_sky
                        )


# render part
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()






####################################################################################
'''
1. instance id and distinguish
2. register table
3. console box
'''
####################################################################################


from interface.cui_logger import logger as log
from interface.cui_colors import color_rgb
import dearpygui.dearpygui as dpg

# create the context and viewport
dpg.create_context()
dpg.create_viewport(title="Tutorial", width=1000, height=800)


# shared variables
id_input   = list()
id_button  = list()
id_console = list()


def handler_input(sender, app_data, user_data):
    
    global id_input, id_console
    input_value = app_data.strip() # get the input value after revmove blank
    if input_value.isdigit(): # check if it's valid number
        log.forcedLog(f"(ID {id_input}) valid input : {input_value}")
    else:
        log.forcedLog(f"(ID {id_input}) invalid input : {input_value}")
    handler_log(f"{{from input handler}}", input_value, id_console)


def handler_button(sender, app_data, user_data):
    
    global id_button, id_console
    label = dpg.get_item_label(sender) # get the button label
    if label.startswith(f"Number_"):
        number = label.split("_")[1]
        log.forcedLog(f"(ID {id_button}) button clicked : {number}")
        handler_log(f"{{from button handler}}", f"button {number}", id_console)


def handler_log(sender, app_data, user_data):

    # sender : can be set by the caller
    # app_data : log value
    # user_data : id_console value

    global id_console
    current_text = dpg.get_value(user_data)
    new_log = f"\n{app_data}"  # Append new log
    dpg.set_value(user_data, current_text + new_log)
    log.forcedLog(f"(ID {id_console}) console output : {sender}, {app_data} {user_data}")


with dpg.window(
    label="Main Window", 
    width=800, 
    height=700):
    
    dpg.add_text(f"GUI Template V0.10")
    
    input_label = "Label test"
    id_input = dpg.add_input_text(
        label=input_label,
        callback=handler_input
    )
    dpg.add_text(f"")
    
    # assign the id to global id variable
    total_button = 4
    for n in range(1, total_button+1):
        id_assign = dpg.add_button(
            label=f"Number_{n}",
            callback=handler_button
        )
        id_button.append(id_assign)
    
    with dpg.table(
        header_row=True,
        resizable=False,
        borders_outerH=True,
        borders_innerH=False,
        borders_innerV=True):

        '''
        header_row     : adds a header row at the top of the table
        resizable      : allow resizing of the columns
        borders_outerH : top and bottom border line
        borders_innerH : horizontal border lines between rows
        borders_innerV : vertical border between columns
        '''

        # table columns for header
        # table can have single header
        
        for col in reversed(range(8)):
            dpg.add_table_column(label=f"Bit{col}")
        
        # table rows with cells
        # add_text does not support the callback function
        for row in range(5):

            with dpg.table_row():
                dpg.add_text(f"{row:#04x}")
                
                for col in reversed(range(8)):
                    dpg.add_text(
                        default_value=f"{row:02x}h bit{col}",
                        indent=5,
                        bullet=False,
                        color=color_rgb.red
                        )
    
    dpg.add_text(f"")
    
    console_label = "Log"
    id_console = dpg.add_input_text(
        multiline=True,
        readonly=True,
        width=500,
        height=200,
        default_value="Console box",
        label=input_label
    )


# render part
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()







####################################################################################
'''
1. register table
2. color change for cell
'''
####################################################################################

from interface.cui_logger import logger as log
from interface.cui_colors import color_rgb
import dearpygui.dearpygui as dpg

# create the context and viewport
dpg.create_context()
dpg.create_viewport(title="Tutorial", width=1000, height=800)

# Store cell IDs for tracking
cell_map = {}
cell_themes = {}
cell_conf = dict()

# Create themes for red and blue text
with dpg.theme() as red_theme:
    with dpg.theme_component(dpg.mvSelectable):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0))  # Red text

with dpg.theme() as blue_theme:
    with dpg.theme_component(dpg.mvSelectable):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 255))  # Blue text


# handler for change color
def change_cell_color(sender, app_data, user_data):
    current_theme = cell_themes.get(sender, red_theme)  # Default to red
    new_theme = blue_theme if current_theme == red_theme else red_theme
    dpg.bind_item_theme(sender, new_theme)
    cell_themes[sender] = new_theme
    log.forcedLog(f"(sneder {sender}) cell {user_data} clicked, color changed from {current_theme} to {new_theme}")

with dpg.window(
    label="Main Window", 
    width=800, 
    height=700):
    
    dpg.add_text(f"GUI Template V0.10")
    
    with dpg.table(
        header_row=True,
        resizable=False,
        borders_outerH=True,
        borders_innerH=False,
        borders_innerV=True):

        dpg.add_table_column(label="address")
        for col in reversed(range(8)):
            dpg.add_table_column(label=f"bit{col}")
        
        # table rows with cells
        for row in range(2):

            with dpg.table_row():
                dpg.add_text(f"{row:#04x}")
                
                for col in reversed(range(8)):
                    cell_text = f"{row:02x}h bit{col}"
                    cell_id = dpg.add_selectable(
                        label=cell_text,
                        user_data=cell_text,
                        callback=change_cell_color
                    )

                    # Apply default red theme
                    dpg.bind_item_theme(cell_id, red_theme)
                    cell_themes[cell_id] = red_theme
                    
                    cell_conf[cell_id] = dpg.get_item_configuration(cell_id)
                    
                    cell_map[cell_id] = [row, col]


# render part
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()




####################################################################################
'''
1. get the configuration from id
'''
####################################################################################

import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(label="Tutorial"):
    b0 = dpg.add_button(label="button 0")
    b1 = dpg.add_button(tag=100, label="Button 1")
    dpg.add_button(tag="Btn2", label="Button 2")

dpg.set_item_label(item=b0, label="new label")
print(b0)
print(b1)
print(dpg.get_item_label("Btn2"))

conf = dpg.get_item_configuration(b0)

dpg.create_viewport(title='Custom Title', width=600, height=200)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()



####################################################################################
'''
1. gather the infomation for the api
'''
####################################################################################

from interface.cui_logger import logger as log
from interface.cui_colors import color_rgb
import dearpygui.dearpygui as dpg
import yaml

# create the context and viewport
dpg.create_context()
dpg.create_viewport(title="Tutorial", width=1000, height=800)


def handler_button(sender, app_data, user_data):
    log.forcedLog(f"button handler : sender={sender}, app_data={app_data}, user_data={user_data}")


def handler_common(sender, app_data, user_data):
    log.forcedLog(f"common handler : sender={sender}, app_data={app_data}, user_data={user_data}")

yaml_dict = dict()

with dpg.window(
    label="Main Window", 
    width=800, 
    height=700):
    
    id_text = dpg.add_text(f"GUI Template V0.10")
    yaml_dict["add_text"] = dpg.get_item_configuration(id_text)

    id_button = dpg.add_button(
        label="button",
        callback=handler_button
    )
    yaml_dict["add_button"] = dpg.get_item_configuration(id_button)

    id_textbox = dpg.add_input_text(
        label="Log output",
        multiline=True,
        readonly=True,
        width=500,
        height=200,
        default_value="Text box"
    )
    yaml_dict["add_input_text"] = dpg.get_item_configuration(id_textbox)
    
    with dpg.table(
        header_row=True,
        resizable=False,
        borders_outerH=True,
        borders_innerH=False,
        borders_innerV=True):

        id_column = dpg.add_table_column(label="address")
        yaml_dict["address"] = dpg.get_item_configuration(id_column)

        for col in reversed(range(8)):
            id_column = dpg.add_table_column(label=f"bit{col}")
            yaml_dict[f"bit{col}"] = dpg.get_item_configuration(id_column)
        
        # table rows with cells
        for row in range(2):

            with dpg.table_row():
                id_row = dpg.add_text(f"{row:#04x}")
                yaml_dict[f"row{row:#04x}"] = dpg.get_item_configuration(id_row)
                
                for col in reversed(range(8)):
                    cell_text = f"{row:02x}h_bit{col}"
                    cell_id = dpg.add_selectable(
                        label=cell_text,
                        user_data=f"user_data_bit{col}",
                        callback=handler_common
                    )
                    yaml_dict[cell_text] = dpg.get_item_configuration(cell_id)

file = open(f"dearpygui_property.yaml", "w")
yaml.dump(yaml_dict, file, default_flow_style=False)
file.close()

# render part
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()



####################################################################################
'''
1. change the configure_item for the element
'''
####################################################################################

import dearpygui.dearpygui as dpg

# Create the context and viewport
dpg.create_context()
dpg.create_viewport(title="Radio Button Example", width=600, height=400)

# Color mapping for choices
color_map = {
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255)
}

# Callback function
def radio_callback(sender, app_data, user_data):
    """Changes text color based on selected radio button."""
    dpg.configure_item(user_data, color=color_map[app_data])  # Change text color
    print(f"Sender: {sender}, Selected: {app_data}, Changing color of {user_data}")

# Create GUI
with dpg.window(label="Main Window", width=400, height=300):
    
    text_id = dpg.add_text("Change my color!")  # Target text widget
    dpg.configure_item(
        text_id,
        color=(0, 255, 0),
        label="label test",
        show_label=True,
        indent=10
        )
    
    id = dpg.add_radio_button(
        items=["Red", "Green", "Blue"],
        callback=radio_callback,
        user_data=text_id  # Pass text widget ID to change its color
    )

print(dpg.get_item_configuration(id))

# Run GUI
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()


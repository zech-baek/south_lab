from gui.shared_space import shared_var
import dearpygui.dearpygui as dpg


def print_debugging():
    
    print(f"[tab4] pass")


def tag_func():
    
    tab_tag = "temp"
    
    with dpg.tab(label="temp map", tag=tab_tag):

        dpg.add_spacer(height=5)
        
        dpg.add_button(
            label="temp",
            width=280,
            user_data="temp_button",
            )
    
    # return the id of the tab
    return tab_tag
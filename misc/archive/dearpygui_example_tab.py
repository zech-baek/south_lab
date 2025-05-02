import dearpygui.dearpygui as dpg

# Create the context and viewport
dpg.create_context()
dpg.create_viewport(title="Radio Button Example", width=600, height=400)

with dpg.window(label="Main Window", width=400, height=300):

    with dpg.tab_bar():
        with dpg.tab(label="General Settings"):
            dpg.add_checkbox(label="Enable Auto Mode")
        
        with dpg.tab(label="Advanced"):
            dpg.add_slider_float(label="Gain")



dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
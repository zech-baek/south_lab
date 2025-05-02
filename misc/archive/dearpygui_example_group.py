import dearpygui.dearpygui as dpg

# Create context
dpg.create_context()
dpg.create_viewport(title="2x2 Grid Example", width=600, height=400)

with dpg.window(label="Main Window", width=600, height=400):

    # Top row
    with dpg.group(horizontal=True, width=200):  # Groups items in a horizontal row
        with dpg.group():
            dpg.add_text("Group 1: Controls")
            dpg.add_button(label="Button A")
            dpg.add_slider_float(label="Slider A")
        
        # dpg.add_spacing(count=10)  # Adds spacing between groups

        with dpg.group(width=200):
            dpg.add_text("Group 2: Settings")
            dpg.add_checkbox(label="Enable Feature X")
            dpg.add_input_text(label="Input A")

    dpg.add_spacing(count=20)  # Adds vertical spacing between top and bottom rows

    # Bottom row
    with dpg.group(horizontal=True, width=200):
        with dpg.group():
            dpg.add_text("Group 3: Options")
            dpg.add_radio_button(items=["Option 1", "Option 2"])

        # dpg.add_spacing(count=10)  

        with dpg.group(width=200):
            dpg.add_text("Group 4: Actions")
            dpg.add_button(label="Run")
            dpg.add_button(label="Stop")

# Setup & Start
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

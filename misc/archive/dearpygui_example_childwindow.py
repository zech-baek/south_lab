import dearpygui.dearpygui as dpg

# Create context and viewport
dpg.create_context()
dpg.create_viewport(title="2x2 Child Window Grid", width=700, height=400)

with dpg.window(label="Main Window", width=650, height=300):

    # Top row (Panel A & Panel B)
    with dpg.group(horizontal=True):
        with dpg.child_window(width=300, height=120):
            dpg.add_text("Panel #A")
            dpg.add_slider_float(label="Brightness")
            dpg.add_slider_float(label="Contrast")

        dpg.add_spacing(count=10)  # Space between columns

        with dpg.child_window(width=300, height=120):
            dpg.add_text("Panel #B")
            dpg.add_slider_float(label="Brightness")
            dpg.add_slider_float(label="Contrast")

    dpg.add_spacing(count=10)  # Space between rows

    # Bottom row (Panel C & Panel D)
    with dpg.group(horizontal=True):
        with dpg.child_window(width=300, height=120):
            dpg.add_text("Panel #C")
            dpg.add_slider_float(label="Brightness")
            dpg.add_slider_float(label="Contrast")

        dpg.add_spacing(count=10)

        with dpg.child_window(width=300, height=120):
            dpg.add_text("Panel #D")
            dpg.add_slider_float(label="Brightness")
            dpg.add_slider_float(label="Contrast")

# Setup & Start
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

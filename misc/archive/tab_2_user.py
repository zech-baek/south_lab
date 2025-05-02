import dearpygui.dearpygui as dpg
from gui.layout.user import group_a, group_b


def handler_update_register(sender, app_data, user_data):
    pass


def tab_user():

    tab_tag = "id_tab_2"
    
    #----------------------------------------
    # define group a & b
    # get the properties from the group class
    #----------------------------------------
    
    table_no = 0
    table_title = list()
    
    # key : order of register row
    row_index = list(group_a.table_prop.keys())
    
    
    #----------------------------------------
    
    with dpg.tab(label="User", tag=tab_tag):

        dpg.add_spacer(height=5)

        dpg.add_button(
            label="Update all registers in current tab",
            width=280,
            user_data="update_all_button",
            callback=handler_update_register
            )
        
        dpg.add_spacer(height=5)

        ##### parent group --> register control
        with dpg.group(
            horizontal=True):
            
            ##### group A start --> IC_info, Status
            with dpg.group():
                with dpg.child_window(
                    width=550,
                    height=300,
                    autosize_x=False,
                    autosize_y=False,
                    horizontal_scrollbar=False
                    ):

                    id_txt_regcontrol_title = dpg.add_text(
                        default_value="Register Info & Status",
                        color=(255, 255, 0)
                        )
                    
                    dpg.add_spacer(height=5)

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
                            label="Register",
                            init_width_or_weight=column_width+50,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Type",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Length",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Value",
                            init_width_or_weight=column_width+100,
                            width_fixed=True
                            )
                        
                        with dpg.table_row():
                            dpg.add_text("VENDOR_ID")
                            dpg.add_text("R")
                            dpg.add_text("4")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=True,
                                width=300
                                )
                        
                        with dpg.table_row():
                            dpg.add_text("MODEL_ID")
                            dpg.add_text("R")
                            dpg.add_text("4")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=True,
                                width=300
                                )
                        
                        with dpg.table_row():
                            dpg.add_text("DEV_ID")
                            dpg.add_text("R")
                            dpg.add_text("4")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=True,
                                width=300
                                )
                    
                    dpg.add_spacer(height=5)

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
                            label="Register",
                            init_width_or_weight=column_width+50,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Type",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Length",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Value",
                            init_width_or_weight=column_width+100,
                            width_fixed=True
                            )
                        
                        with dpg.table_row():
                            dpg.add_text("BUSY")
                            dpg.add_text("R")
                            dpg.add_text("1")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=True,
                                width=300
                                )
            
            ##### group B start --> Control, Position
            with dpg.group():
                with dpg.child_window(
                    width=550,
                    height=300,
                    autosize_x=False,
                    autosize_y=False,
                    horizontal_scrollbar=False
                    ):

                    id_txt_regcontrol_title = dpg.add_text(
                        default_value="Register Control",
                        color=(255, 255, 0)
                        )
                    
                    dpg.add_spacer(height=5)

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
                            label="Register",
                            init_width_or_weight=column_width+50,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Type",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Length",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Value",
                            init_width_or_weight=column_width+100,
                            width_fixed=True
                            )
                        
                        with dpg.table_row():
                            dpg.add_text("ARRC")
                            dpg.add_text("RW")
                            dpg.add_text("1")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=False,
                                width=300
                                )
                        
                        with dpg.table_row():
                            dpg.add_text("PD")
                            dpg.add_text("RW")
                            dpg.add_text("1")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=False,
                                width=300
                                )
                        
                        with dpg.table_row():
                            dpg.add_text("ARRCM")
                            dpg.add_text("RW")
                            dpg.add_text("3")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=False,
                                width=300
                                )
                        
                        with dpg.table_row():
                            dpg.add_text("SCAL")
                            dpg.add_text("RW")
                            dpg.add_text("2")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=False,
                                width=300
                                )
                        
                        with dpg.table_row():
                            dpg.add_text("ARRCT")
                            dpg.add_text("RW")
                            dpg.add_text("6")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=False,
                                width=300
                                )

                        with dpg.table_row():
                            dpg.add_text("UMODE")
                            dpg.add_text("RW")
                            dpg.add_text("1")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=False,
                                width=300
                                )
                        
                        with dpg.table_row():
                            dpg.add_text("UMC")
                            dpg.add_text("RW")
                            dpg.add_text("1")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=False,
                                width=300
                                )
                    
                    dpg.add_spacer(height=5)

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
                            label="Register",
                            init_width_or_weight=column_width+50,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Type",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Length",
                            init_width_or_weight=column_width,
                            width_fixed=True
                            )
                        dpg.add_table_column(
                            label="Value",
                            init_width_or_weight=column_width+100,
                            width_fixed=True
                            )
                        
                        with dpg.table_row():
                            dpg.add_text("D")
                            dpg.add_text("RW")
                            dpg.add_text("11")
                            dpg.add_input_text(
                                default_value="0x00",
                                readonly=False,
                                width=300
                                )
        ##### parent group finish
        
        dpg.add_spacer(height=5)

        ##### group C start --> IMAX
        with dpg.group():

            with dpg.child_window(
                width=550+550+8,
                height=170,
                autosize_x=False,
                autosize_y=False,
                horizontal_scrollbar=False
                ):

                dpg.add_text(
                    default_value="IMAX Control",
                    color=(255, 255, 0)
                    )
                
                dpg.add_spacer(height=5)

                silver = (160, 160, 160)
                black = (0, 0, 0)

                with dpg.theme() as checkbox_silver:
                    with dpg.theme_component(dpg.mvCheckbox):
                        dpg.add_theme_color(dpg.mvThemeCol_Text, silver, category=dpg.mvThemeCat_Core)
                with dpg.theme() as checkbox_black:
                    with dpg.theme_component(dpg.mvCheckbox):
                        dpg.add_theme_color(dpg.mvThemeCol_Text, silver, category=dpg.mvThemeCat_Core)

                with dpg.group(horizontal=True):
                    with dpg.group():
                        with dpg.child_window(width=200, border=False):
                            id_chkbox_100mA = dpg.add_checkbox(label="100mA", default_value=True)
                            id_chkbox_80mA  = dpg.add_checkbox(label="80mA", default_value=False)
                            id_chkbox_90mA  = dpg.add_checkbox(label="90mA", default_value=False)
                            id_chkbox_110mA = dpg.add_checkbox(label="110mA", default_value=False)
                    with dpg.group():
                        with dpg.child_window(width=200, border=False):
                            id_chkbox_120mA = dpg.add_checkbox(label="120mA", default_value=False)
                            id_chkbox_130mA = dpg.add_checkbox(label="130mA", default_value=False)
                            id_chkbox_140mA = dpg.add_checkbox(label="140mA", default_value=False)
                            id_chkbox_150mA = dpg.add_checkbox(label="150mA", default_value=False)
                    
                    dpg.bind_item_theme(id_chkbox_80mA, checkbox_silver)
                    dpg.bind_item_theme(id_chkbox_90mA, checkbox_silver)
                    dpg.bind_item_theme(id_chkbox_110mA, checkbox_silver)
                    dpg.bind_item_theme(id_chkbox_120mA, checkbox_silver)
                    dpg.bind_item_theme(id_chkbox_130mA, checkbox_silver)
                    dpg.bind_item_theme(id_chkbox_140mA, checkbox_silver)
                    dpg.bind_item_theme(id_chkbox_150mA, checkbox_silver)
        ##### group C finish

        dpg.add_spacer(height=5)

        # console box group
        with dpg.group():
            with dpg.child_window(
                width=550+550+8,
                height=200,
                autosize_x=False,
                autosize_y=False,
                horizontal_scrollbar=False
                ):
                # add 8px due to the horizontal spacer between the childwindows 
                id_input_console = dpg.add_input_text(
                    multiline=True,
                    readonly=True,
                    width=550+550-20,
                    height=180,
                    default_value="Output console"
                )
        
        dpg.add_spacer(height=5)
        
        with dpg.group():
            with dpg.child_window(width=550+550+8, height=30):
                dpg.add_text("-"*153) # dummy
                        
    return tab_tag
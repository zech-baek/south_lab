%matplotlib tk
from interface.docs.output_chart import plot
import numpy as np
import math
chart = plot()


# single pop-up
chart.set_title = "single pop-up window"
chart.set_single_plot
chart.set_xlabel = "label x-a"
chart.set_y_main_label = "label y-a"
chart.add_main_item = "item"
chart.add_main_item = "msb"
chart.add_main_item = "lsb"
chart.item.set_linewidth = 4
chart.msb.set_linewidth = 2
chart.lsb.set_linewidth = 1
chart.msb.set_line_dot
chart.lsb.set_line_dot
for i in range(100):
    chart.item.set_data = i, np.sin(math.pi*i/20)*i
    chart.msb.set_data = i, 10
    chart.lsb.set_data = i, -10
    chart.output
chart.save_plot = chart.set_title



# 1st pop-up
chart.set_title = "1st pop-up window"
chart.set_single_plot
chart.set_xlabel = "label x-a"
chart.set_y_main_label = "label y-a"
chart.add_main_item = "item_1"
chart.add_main_item = "item_2"
for i in range(30):
    x1 = np.sin(math.pi*i/10)*0.5
    x2 = np.sin(math.pi*i/5)*0.75
    chart.item_1.set_data = math.pi*i, x1
    chart.item_2.set_data = math.pi*i, x2
    chart.output
chart.save_plot = chart.set_title

# 2nd pop-up
chart.set_title = "2nd pop-up window"
chart.set_single_plot
chart.set_xlabel = "label x-b"
chart.set_y_main_label = "label y-b"
chart.add_main_item = "item_3"
chart.add_main_item = "item_4"
chart.add_main_item = "item_5"
chart.add_main_item = "item_6"
for i in range(30):
    x1 = np.sin(math.pi*i/10)*0.5
    x2 = np.sin(math.pi*i/5)*0.75
    chart.item_3.set_data = math.pi*i, x1
    chart.item_4.set_data = math.pi*i, x2
    chart.item_5.set_data = math.pi*i, x1*0.5
    chart.item_6.set_data = math.pi*i, x2*0.75
    chart.output
chart.save_plot = chart.set_title


chart.set_title = "dual axis"
chart.set_dual_plot
chart.set_xlabel = "label x label"
chart.set_y_main_label = "label y main"
chart.set_y_sub_label = "label y sub"
chart.add_main_item = "item_1"
chart.add_main_item = "item_2"
chart.add_main_item = "item_3"
chart.add_sub_item = "item_4"
chart.add_sub_item = "item_5"
chart.add_sub_item = "item_6"

for i in range(40):
    new_x = i * 0.1
    chart.item_1.set_data = new_x, np.sin(new_x*1)
    chart.item_2.set_data = new_x, np.sin(new_x*1.5)*1.2
    chart.item_3.set_data = new_x, np.sin(new_x*2)*0.75
    chart.item_4.set_data = new_x, np.sin(new_x*5)*1.6+1
    chart.item_5.set_data = new_x, np.sin(new_x*2)*0.6-1.5
    chart.item_6.set_data = new_x, np.sin(new_x*7)*0.2+2
    chart.output
chart.save_plot = chart.set_title


chart.set_title = "double axis 1"
chart.set_double_plot
chart.set_xlabel = "label x label"
chart.set_y_main_label = "label y main"
chart.set_y_sub_label = "label y sub"
chart.add_main_item = "item_1"
chart.add_main_item = "item_2"
chart.add_main_item = "item_3"
chart.add_sub_item = "item_4"
chart.add_sub_item = "item_5"
chart.add_sub_item = "item_6"

for i in range(50):
    new_x = i * 0.1
    chart.item_1.set_data = new_x, np.sin(new_x*1)
    chart.item_2.set_data = new_x, np.sin(new_x*1.5)*1.2
    chart.item_3.set_data = new_x, np.sin(new_x*2)*0.75
    chart.item_4.set_data = new_x, np.sin(new_x*5)*1.6+1
    chart.item_5.set_data = new_x, np.sin(new_x*2)*0.6-1.5
    chart.item_6.set_data = new_x, np.sin(new_x*7)*0.2+2
    chart.output
chart.save_plot = chart.set_title
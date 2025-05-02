# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib

try:
    # try to use __file__
    doc_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        doc_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        doc_dir = os.getcwd()

log_dir = pathlib.Path(doc_dir).parent.parent/"log"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)


from interface.cui_logger import logger as log
from matplotlib import pyplot as plt
from datetime import datetime


def output_log(function, message, logging):

    if logging:
        log.forcedLog(f"[{function} {message}]")
    

class style_preset:

    single_plot_style = {
        "figsize"   : (10, 5),
        "layout"    : "constrained",
        "facecolor" : "azure",
        "edgecolor" : "k"
    }


    dual_plot_style = {
        "figsize"   : (10, 7),
        "layout"    : "constrained",
        "facecolor" : "azure",
        "edgecolor" : "k"
    }


    title_style = {
        "fontsize"   : 16,
        "ha"         : "left",
        "fontweight" : "bold"
    }

    line_style = {
        "solid"   : "-",
        "dashed"  : "--",
        "dashdot" : "-.",
        "dotted"  : ":"
    }


class function:
    
    def __init__(self, handler, name, is_main, line_id):
        
        self.handler    = handler
        self.name       = name
        self.is_main    = is_main
        self.line_id    = line_id
        self.line_style = style_preset.line_style["solid"]
        self.is_grid    = True
        self.dotted     = False
        self.width      = 1

        for key, style in style_preset.line_style.items():
            setattr(self.__class__, f"set_line_{key}", property(lambda self, style=style: getattr(self, "set_line_style")(style)))
        
        self.set_line # initiaize the property for the line
    
    
    def set_line_style(self, style):
        self.line_style = style
    
    
    @property
    def set_line(self):
        
        if self.is_main:
            if self.line_id not in self.handler.main_items:
                output_log("set_line", f"main item : {self.name}", self.handler.logging)
                line, = self.handler.ax1.plot([], [], label=self.name)
                self.handler.main_items[self.line_id] = {"x":[], "y":[], "line":line}
        else:
            if self.line_id not in self.handler.sub_items:
                output_log("set_line", f"sub item : {self.name}", self.handler.logging)
                line, = self.handler.ax2.plot([], [], label=self.name)
                self.handler.sub_items[self.line_id] = {"x":[], "y":[], "line":line}
        
        # Ensure the main plot is drawn
        if not self.handler.is_main_drawing:
            output_log("set_line", f"drawing the items for main_axis", self.handler.logging)
            if self.handler.chart_title is not None:
                self.handler.fig.suptitle(t=self.handler.chart_title, **style_preset.title_style, x=0.05)
            if self.handler.x_label is not None:
                self.handler.ax1.set_xlabel(self.handler.x_label) # label for x-axis
            if self.handler.y_main_label is not None:
                self.handler.ax1.set_ylabel(self.handler.y_main_label) # label for y-axis
            self.handler.ax1.grid(True, which="both", linestyle="-", linewidth=0.5, color="black")
            self.handler.is_main_drawing = True
        
        # Ensure the sub plot is drawn
        if (not self.is_main) and (not self.handler.is_sub_drawing):
            output_log("set_line", f"drawing the items for sub_axis", self.handler.logging)
            if self.handler.y_sub_label is not None:
                self.handler.ax2.set_ylabel(self.handler.y_sub_label) # label for y-axis
            self.handler.is_sub_drawing = True
            if self.handler.is_double:
                self.handler.ax2.set_xlabel(self.handler.x_label) # label for x-axis
                self.handler.ax2.grid(True, which="both", linestyle="-", linewidth=0.5, color="black")
    
    
    @property
    def set_line_dot(self):
        self.dotted = True
    
    
    @property
    def set_line_solid(self):
        self.dotted = False
    
    
    @property
    def set_linewidth(self):
        output_log("set_linewidth", f"line width : {self.width}", self.handler.logging)
    
    
    @set_linewidth.setter
    def set_linewidth(self, value):
        self.width = value
    
    
    @property
    def set_data(self):
        pass
    
    
    @set_data.setter
    def set_data(self, *args):
        
        x_data = args[0][0]
        y_data = args[0][1]
        self.update_drawing(x_data, y_data)
    
    
    def update_drawing(self, x, y):
        
        if self.handler.fig:
            if self.is_main:
                if self.line_id in self.handler.main_items:
                    output_log("update_drawing", f"insert the coordinate for main plot", self.handler.logging)
                    self.handler.main_items[self.line_id]["x"].append(x)
                    self.handler.main_items[self.line_id]["y"].append(y)
                    line = self.handler.main_items[self.line_id]["line"]
                    line.set_xdata(self.handler.main_items[self.line_id]["x"])
                    line.set_ydata(self.handler.main_items[self.line_id]["y"])
                    if self.dotted:
                        line.set_linestyle("dotted")
                        line.set_linewidth(self.width)
                    else:
                        line.set_linestyle("solid")
                        line.set_linewidth(self.width)
                    self.handler.ax1.relim()  # recalculate the limit range
                    self.handler.ax1.autoscale_view(scalex=True, scaley=True)  # rescale the view
            else:
                if self.line_id in self.handler.sub_items:
                    output_log("update_drawing", f"insert the coordinate for sub plot", self.handler.logging)
                    self.handler.sub_items[self.line_id]["x"].append(x)
                    self.handler.sub_items[self.line_id]["y"].append(y)
                    line = self.handler.sub_items[self.line_id]["line"]
                    if self.dotted:
                        line.set_linestyle("dotted")
                        line.set_linewidth(self.width)
                    else:
                        line.set_linestyle("solid")
                        line.set_linewidth(self.width)
                    line.set_xdata(self.handler.sub_items[self.line_id]["x"])
                    line.set_ydata(self.handler.sub_items[self.line_id]["y"])
                    self.handler.ax2.relim()  # recalculate the limit range
                    
                    '''
                    - scaley has a bug when rescale on the pop-up window
                    - if scaley is True, the sub line is cleared
                    - therefore, the rescaling is implemented manually right before output the chart
                    '''

                    self.handler.ax2.autoscale_view(scalex=True, scaley=False)  # rescale the view
                    # self.handler.ax2.set_ylim(
                    #     min(self.handler.sub_items[self.line_id]["y"]),
                    #     max(self.handler.sub_items[self.line_id]["y"]))

        
        
class plot(function):
    
    def __init__(self):
        
        log.initLogger(log.info)
        self.logging      = False
        self.fig          = None
        self.ax1          = None
        self.ax2          = None
        self.line         = None
        self.chart_title  = None
        self.x_label      = None
        self.y_main_label = None
        self.y_sub_label  = None
        self.is_single    = None
        self.is_double    = False
        self.line_count   = 0
        self.main_items   = dict()
        self.sub_items    = dict()
        self.is_main_drawing = False
        self.is_sub_drawing  = False
        
        self.yaxis_lim ={
            "main_min" : None,
            "main_max" : None,
            "sub_min"  : None,
            "sub_max"  : None
        }
        
        plt.ion()
    
    
    @property
    def reset_chart(self):

        # reinitialize the figure
        # if the poped up window is none, exist_popup will be 0

        exist_popup = plt.fignum_exists(self.fig.number)
        if not exist_popup:
            if self.is_single:
                output_log("reset_chart", f"regenerate the single pop-up window, existing pop-up={exist_popup}", self.logging)
                self.fig, self.ax1 = plt.subplots(**style_preset.single_plot_style)
            elif not self.is_double:
                output_log("reset_chart", f"regenerate the dual pop-up window, existing pop-up={exist_popup}", self.logging)
                self.fig, self.ax1 = plt.subplots(**style_preset.dual_plot_style)
                self.ax2 = self.ax1.twinx()
            else:
                self.fig, (self.ax1, self.ax2) = plt.subplots(2, **style_preset.dual_plot_style)
        
        plt.show()
        self.main_items   = dict()
        self.sub_items    = dict()
        self.is_main_drawing = False
        self.is_sub_drawing  = False
        self.yaxis_lim ={
            "main_min" : None,
            "main_max" : None,
            "sub_min"  : None,
            "sub_max"  : None
        }
    
    
    @property
    def new_popup(self):
        
        if self.is_single:
            output_log("new_popup", f"regenerate the single pop-up window", self.logging)
            self.fig, self.ax1 = plt.subplots(**style_preset.single_plot_style)
        elif not self.is_double:
            output_log("new_popup", f"regenerate the dual pop-up window", self.logging)
            self.fig, self.ax1 = plt.subplots(**style_preset.dual_plot_style)
            self.ax2 = self.ax1.twinx()
        else:
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, **style_preset.dual_plot_style)
        
        
    @property
    def output(self):
        
        # update the limitation for main and sub y-axis
        self.calc_yaxis_lim
        offset_main = 0
        offset_sub = 0
        
        # all 10% margin
        # output warning : the case if the min and max set identical values
        if (float(self.yaxis_lim["main_min"]) - float(self.yaxis_lim["main_max"])) < 1e-5:
            offset_main = 1e-5
        self.ax1.set_ylim(float(self.yaxis_lim["main_min"])*1.1, float(self.yaxis_lim["main_max"])*1.1+offset_main)
        if not self.is_single:
            if (float(self.yaxis_lim["sub_min"]) - float(self.yaxis_lim["sub_max"])) < 1e-5: 
                offset_sub = 1e-5
            self.ax2.set_ylim(float(self.yaxis_lim["sub_min"])*1.1, float(self.yaxis_lim["sub_max"])*1.1+offset_sub)
        
        self.ax1.legend(loc="upper left")
        if not self.is_single:
            if self.is_double:
                self.ax2.legend(loc="upper left")
            else:
                self.ax2.legend(loc="upper right")

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    
    @property
    def set_main_ylimit(self):
        pass
    
    
    @set_main_ylimit.setter
    def set_main_ylimit(self, *args):
        
        minimum = args[0][0]
        maximum = args[0][1]
        self.ax1.set_ylim(minimum, maximum)
    
    
    @property
    def set_sub_ylimit(self):
        pass
    
    
    @set_sub_ylimit.setter
    def set_sub_ylimit(self, minimum, maximum):
        self.ax2.set_ylim(minimum, maximum)
    
    
    @property
    def calc_yaxis_lim(self):
        
        ret_main_min = []
        ret_main_max = []
        ret_sub_min = []
        ret_sub_max = []
        
        for value in self.main_items.values():
            output_log("calc_yaxis_lim", f"{value}", self.logging)
            ret_main_min.append(min(value["y"]))
            ret_main_max.append(max(value["y"]))
        self.yaxis_lim["main_min"] = min(ret_main_min)
        self.yaxis_lim["main_max"] = max(ret_main_max)
        
        if not self.is_single:
            for value in self.sub_items.values():
                ret_sub_min.append(min(value["y"]))
                ret_sub_max.append(max(value["y"]))
            self.yaxis_lim["sub_min"] = min(ret_sub_min)
            self.yaxis_lim["sub_max"] = max(ret_sub_max)
    
    
    @property
    def set_single_plot(self):
        
        # generate fig and main plot by default
        # generate sub plot if is_signle is False

        self.is_single = True
        output_log("set_single_plot", f"is_singe : {self.is_single}", self.logging)
        self.fig, self.ax1 = plt.subplots(**style_preset.single_plot_style)
        self.reset_chart
    
    
    @property
    def set_dual_plot(self):
        
        self.is_single = False
        output_log("set_dual_plot", f"is_singe : {self.is_single}", self.logging)
        self.fig, self.ax1 = plt.subplots(**style_preset.dual_plot_style)
        self.ax2 = self.ax1.twinx() # case for dual axis plot
        self.reset_chart
    

    @property
    def set_double_plot(self):
        
        self.is_single = False
        self.is_double = True
        output_log("set_double_plot", f"is_double : {self.is_double}", self.logging)
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, **style_preset.dual_plot_style)
        self.reset_chart
        
        
    @property
    def set_title(self):
        return self.chart_title
    
    
    @set_title.setter
    def set_title(self, data):
        
        output_log("set_title", f"{data}", self.logging)
        self.chart_title = data
    
    
    @property
    def set_xlabel(self):
        return self.x_label
    
    
    @set_xlabel.setter
    def set_xlabel(self, data):
        
        output_log("set_xlabel", f"{data}", self.logging)
        self.x_label = data
    
    
    @property
    def set_y_main_label(self):
        return self.y_main_label
    
    
    @set_y_main_label.setter
    def set_y_main_label(self, data):
        
        output_log("set_y_main_label", f"{data}", self.logging)
        self.y_main_label = data
    
    
    @property
    def set_y_sub_label(self):
        return self.y_sub_label
    
    
    @set_y_sub_label.setter
    def set_y_sub_label(self, data):
        
        output_log("set_y_sub_label", f"{data}", self.logging)
        self.y_sub_label = data
    
    
    @property
    def add_main_item(self):
        pass
    
    
    @add_main_item.setter
    def add_main_item(self, name):
        
        output_log("add_main_item", f"{name}", self.logging)
        main_item = function(handler=self, name=name, is_main=True, line_id=self.line_count)
        setattr(self, name, main_item)
        self.line_count += 1
    
    
    @property
    def add_sub_item(self):
        pass
    
    
    @add_sub_item.setter
    def add_sub_item(self, name):
        
        output_log("add_sub_item", f"{name}", self.logging)
        sub_item = function(handler=self, name=name, is_main=False, line_id=self.line_count)
        setattr(self, name, sub_item)
        self.line_count += 1
    
    
    @property
    def save_plot(self):
        pass
    
    
    @save_plot.setter
    def save_plot(self, filename):
        
        dt = datetime.now()
        dt_string = dt.strftime("%Y%m%d_%H%M%S_")

        if filename.endswith(".jpg"):
            filename = dt_string + filename
        else:
            filename = dt_string + filename + ".jpg"
        
        fig_out = log_dir/filename
        self.fig.savefig(fig_out, format='jpg')
        output_log("save_plot", f"export the chart : {fig_out}", self.logging)
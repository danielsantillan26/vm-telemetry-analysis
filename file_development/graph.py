import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Slider

from graphics.gfx_test import pane

matplotlib.use('TkAgg')
import pandas as pd


class GraphFigure:

    def __init__(self, data_name, title, y_num, color, x_label, y_label, pane):
        self.data = pd.read_csv(data_name)
        self.title = title
        self.y_num = y_num
        self.color = color
        self.x_label = x_label
        self.y_label = y_label


    def write_fig(self) -> Figure:
        fig = Figure(figsize=(5, 5), dpi = 100)
        ax = fig.add_subplot(111)
        ax.plot(self.data.iloc[:, 0], self.data.iloc[:, self.y_num], color = self.color, linewidth = 0.5)
        ax.set_title(self.title)
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        return fig
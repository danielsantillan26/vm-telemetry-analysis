import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from matplotlib.widgets import Slider
matplotlib.use('TkAgg')
import pandas as pd

Plot, Axis = plt.subplots()

plt.subplots_adjust(bottom=0.25)

data = pd.read_csv("../data/lap_traces.csv")      # Read .csv file
plt.plot(data[data.columns[0]], data[data.columns[7]], linestyle = '-', color = 'red', linewidth = 0.8)

slider_color = 'White'
axis_position = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor = slider_color)
slider_position = Slider(axis_position, 'Pos', 0.1, 90.0)

def update(val):
    pos = slider_position.val
    Axis.axis([pos, pos+10, -10, 10])
    Plot.canvas.draw_idle()

slider_position.on_changed(update)
plt.show()
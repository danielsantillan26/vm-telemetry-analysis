from tkinter import *
from tkinter import filedialog
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Slider
matplotlib.use('TkAgg')
import pandas as pd

root = Tk()

# Virginia Motorsports Telemetry Analysis Software
root.title("VMTAS")
root.iconbitmap('img/vmtas_icon.ico')
root.geometry('1200x800')
root.resizable(False, False)


# VARIABLES AND SETUP
file_to_read = None
Plot, Axis = plt.subplots()
plt.subplots_adjust(bottom=0.25)
plt.style.use('dark_background')


# FUNCTIONS

def mode_selection():
    """Determine the selected software mode and modify software options."""
    mode_choice = mode_choice_var.get()
    if mode_choice == 1:
        print("Live Run")
    elif mode_choice == 2:
        print("Previous Run Review")

def datapoint_selection():
    global file_to_read
    if (file_to_read):
        data = pd.read_csv(file_to_read)

        if (selected_speed.get() == 1):
            fig = Figure(figsize=(5, 4), dpi = 100)
            ax = fig.add_subplot(111)
            ax.plot(data.iloc[:, 0], data.iloc[:, 3], color = "#00afff", linestyle = "-", linewidth = 0.5)
            ax.set_title("Speed Plot")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Speed (mph)")
            canvas = FigureCanvasTkAgg(fig, master = pane_speed)
            canvas.draw()
            canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)
        else:
            for widget in pane_speed.winfo_children():
                widget.destroy()

        if (selected_radius.get() == 1):
            fig = Figure(figsize=(5,4), dpi = 100)
            ax = fig.add_subplot(111)
            ax.plot(data.iloc[:, 0], data.iloc[:, 4], color = "#ff5300", linestyle = "-", linewidth = 0.5)
            ax.set_title("Radius Plot")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Radius (ft)")
            canvas = FigureCanvasTkAgg(fig, master = pane_radius)
            canvas.draw()
            canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)
        else:
            for widget in pane_speed.winfo_children():
                widget.destroy()

        # TODO - Figure out how to do the G-G scatterplot from Chloe
        if (selected_g_lat.get() == 1):
            print(3)
        if (selected_g_lon.get() == 1):
            print(4)

        if (selected_accel_prs.get() == 1 or selected_brake_prs.get() == 1):
            fig = Figure(figsize=(5,4), dpi = 100)



        if (selected_yaw_vel.get() == 1):
            print(7)
        if (selected_yaw_acc.get() == 1):
            print(8)
        if (selected_slip_angle.get() == 1):
            print(9)
        if (selected_slip_ratio.get() == 1):
            print(10)
        if (selected_tire_fy.get() == 1):
            print(11)
        if (selected_roll_grad.get() == 1):
            print(12)
        if (selected_pitch_grad.get() == 1):
            print(13)


def open_file_dialog():
    global file_to_read
    file_path = filedialog.askopenfilename(initialdir = "/", title = "Select .csv to run",
                                           filetypes =(("csv files", "*.csv"),))
    if file_path:
        print(f"Selected File: {file_path}")
        file_to_read = file_path
    else:
        print("No file selected")



# GRAPHICS
# Starting with the options section... put all of this in a paned window
pane = PanedWindow(root, orient = "horizontal", sashrelief = "sunken", sashwidth = 4)
pane.pack(fill = "both", expand = True)

pane_options = Frame(pane, width = 300, height = 800, relief = "sunken")
pane_data = Frame(pane, width = 900, height = 800, relief = "sunken")
pane.add(pane_options, minsize = 260)
pane.add(pane_data, minsize = 500)

label_choose_mode = Label(pane_options, text = "Mode Selection", font = ("Segoe UI", 12), activeforeground = "black",
                          anchor = "w", justify = "left")
label_choose_mode.place(anchor = "nw", relx = 0.01, rely = 0.01, relheight = 0.04)



mode_choice_var = IntVar()
mode_choice_var.set(1)

radio_live = Radiobutton(pane_options, text ="Live Run", variable = mode_choice_var, value=1, padx = 0, pady = 0, bd = 0, anchor ="w", justify ="left")
radio_previous = Radiobutton(pane_options, text ="Previous Run Review", variable = mode_choice_var, value=2, padx = 0, pady = 0, bd = 0, anchor ="w", justify ="left")
radio_live.place(anchor ="nw", relx = 0.01, rely = 0.04, relheight = 0.05)
radio_previous.place(anchor ="nw", relx = 0.01, rely = 0.07, relheight = 0.05)

button_mode_choice = Button(pane_options, text ="Confirm", command = mode_selection, justify ="center", width = 20, height = 8)
button_mode_choice.place(anchor ="nw", relx = 0.01, rely = 0.11, relheight = 0.03)



label_choose_files = Label(pane_options, text="Choose Previous Run .csv", font = ("Segoe UI", 12), activeforeground = "black",
                           anchor = "w", justify = "left")
label_choose_files.place(anchor = "nw", relx = 0.01, rely = 0.16, relheight = 0.04)

button_choose_files = Button(pane_options, text = "Choose Files", command = open_file_dialog, justify = "center", width = 20, height = 8)
button_choose_files.place(anchor = "nw", relx = 0.01, rely = 0.20, relheight = 0.03)


label_select_datapoints = Label(pane_options, text="Select Visible Datapoints", font = ("Segoe UI", 12),
                                activeforeground = "black", anchor = "w", justify = "left")
label_select_datapoints.place(anchor = "nw", relx = 0.01, rely = 0.25, relheight = 0.04)

selected_speed = IntVar()
selected_radius = IntVar()
selected_g_lat = IntVar()
selected_g_lon = IntVar()
selected_accel_prs = IntVar()
selected_brake_prs = IntVar()
selected_yaw_vel = IntVar()
selected_yaw_acc = IntVar()
selected_slip_angle = IntVar()
selected_slip_ratio = IntVar()
selected_tire_fy = IntVar()
selected_roll_grad = IntVar()
selected_pitch_grad = IntVar()

check_speed = Checkbutton(pane_options, text = "Vehicle Speed", anchor = "w", justify = "left", variable = selected_speed)
check_radius = Checkbutton(pane_options, text = "Radius", anchor = "w", justify = "left", variable = selected_radius)
check_g_lat = Checkbutton(pane_options, text = "Lateral G-Force", anchor = "w", justify = "left", variable = selected_g_lat)
check_g_lon = Checkbutton(pane_options, text = "Longitudinal G-Force", anchor = "w", justify = "left", variable = selected_g_lon)
check_accel_prs = Checkbutton(pane_options, text = "Acceleration Pressure", anchor = "w", justify = "left", variable = selected_accel_prs)
check_brake_prs = Checkbutton(pane_options, text = "Brake Pressure", anchor = "w", justify = "left", variable = selected_brake_prs)
check_yaw_vel = Checkbutton(pane_options, text = "Yaw Velocity", anchor = "w", justify = "left", variable = selected_yaw_vel)
check_yaw_acc = Checkbutton(pane_options, text = "Yaw Acceleration", anchor = "w", justify = "left", variable = selected_yaw_acc)
check_slip_angle = Checkbutton(pane_options, text = "Slip Angle", anchor = "w", justify = "left", variable = selected_slip_angle)
check_slip_ratio = Checkbutton(pane_options, text = "Slip Ratio", anchor = "w", justify = "left", variable = selected_slip_ratio)
check_tire_fy = Checkbutton(pane_options, text = "Tire Fy", anchor = "w", justify = "left", variable = selected_tire_fy)
check_roll_grad = Checkbutton(pane_options, text = "Roll Gradient", anchor = "w", justify = "left", variable = selected_roll_grad)
check_pitch_grad = Checkbutton(pane_options, text = "Pitch Gradient", anchor = "w", justify = "left", variable = selected_pitch_grad)

check_speed.place(anchor = "nw", relx = 0.01, rely = 0.28, relheight = 0.05)
check_radius.place(anchor = "nw", relx = 0.01, rely = 0.315, relheight = 0.05)
check_g_lat.place(anchor = "nw", relx = 0.01, rely = 0.35, relheight = 0.05)
check_g_lon.place(anchor = "nw", relx = 0.01, rely = 0.385, relheight = 0.05)
check_accel_prs.place(anchor = "nw", relx = 0.01, rely = 0.42, relheight = 0.05)
check_brake_prs.place(anchor = "nw", relx = 0.01, rely = 0.455, relheight = 0.05)
check_yaw_vel.place(anchor = "nw", relx = 0.01, rely = 0.49, relheight = 0.05)
check_yaw_acc.place(anchor = "nw", relx = 0.01, rely = 0.525, relheight = 0.05)
check_slip_angle.place(anchor = "nw", relx = 0.01, rely = 0.56, relheight = 0.05)
check_slip_ratio.place(anchor = "nw", relx = 0.01, rely = 0.595, relheight = 0.05)
check_tire_fy.place(anchor = "nw", relx = 0.01, rely = 0.63, relheight = 0.05)
check_roll_grad.place(anchor = "nw", relx = 0.01, rely = 0.665, relheight = 0.05)
check_pitch_grad.place(anchor = "nw", relx = 0.01, rely = 0.7, relheight = 0.05)

button_visible_datapoints = Button(pane_options, text ="Confirm", command = datapoint_selection, justify ="center", width = 20, height = 8)
button_visible_datapoints.place(anchor ="nw", relx = 0.01, rely = 0.75, relheight = 0.03)


# Set up scrollbar and data frames
canvas_data = Canvas(pane_data)
scrollbar_data = Scrollbar(pane_data, orient = "vertical", command = canvas_data.yview)
canvas_data.configure(yscrollcommand = scrollbar_data.set)

scrollbar_data.pack(side = "right", fill = "y")
canvas_data.pack(side = "left", fill = "both", expand = True)

pane_scrollable = Frame(canvas_data)
pane_scrollable.bind(
    "<Configure>",
    lambda e: canvas_data.configure(scrollregion=canvas_data.bbox("all"))
)

canvas_data_window = canvas_data.create_window((0, 0), window=pane_scrollable, anchor="nw")

canvas_data.bind(
    "<Configure>",
    lambda e: canvas_data.itemconfig(canvas_data_window, width=e.width)
)


pane_speed = Frame(pane_scrollable, relief = "groove")
pane_radius = Frame(pane_scrollable, relief = "groove")
pane_g_lat = Frame(pane_scrollable, relief = "groove")
pane_g_lon = Frame(pane_scrollable, relief = "groove")
pane_accel_prs = Frame(pane_scrollable, relief = "groove")
pane_brake_prs = Frame(pane_scrollable, relief = "groove")
pane_yaw_vel = Frame(pane_scrollable, relief = "groove")
pane_yaw_acc = Frame(pane_scrollable, relief = "groove")
pane_slip_angle = Frame(pane_scrollable, relief = "groove")
pane_slip_ratio = Frame(pane_scrollable, relief = "groove")
pane_tire_fy = Frame(pane_scrollable, relief = "groove")
pane_roll_grad = Frame(pane_scrollable, relief = "groove")
pane_pitch_grad = Frame(pane_scrollable, relief = "groove")

pane_speed.pack(fill = "x", expand = True)
pane_radius.pack(fill = "x", expand = True)
pane_g_lat.pack(fill = "x", expand = True)
pane_g_lon.pack(fill = "x", expand = True)
pane_accel_prs.pack(fill = "x", expand = True)
pane_brake_prs.pack(fill = "x", expand = True)
pane_yaw_vel.pack(fill = "x", expand = True)
pane_yaw_acc.pack(fill = "x", expand = True)
pane_slip_angle.pack(fill = "x", expand = True)
pane_slip_ratio.pack(fill = "x", expand = True)
pane_tire_fy.pack(fill = "x", expand = True)
pane_roll_grad.pack(fill = "x", expand = True)
pane_pitch_grad.pack(fill = "x", expand = True)

pane.add(pane_options)
pane.add(pane_data)
root.update_idletasks()
pane.sash_place(0, 300, 0)
# Always the last line in your program.
root.mainloop()
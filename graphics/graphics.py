from tkinter import *
from tkinter import filedialog, messagebox
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')
import pandas as pd
from enum import IntEnum
import sys

# TODO: Consider getting rid of the mode altogether.
class Mode(IntEnum):
    NONE = 0
    PREVIOUS_RUN = 1
    LIVE_RUN = 2

class DatapointSelected(IntEnum):
    NOT_SELECTED = 0
    SELECTED = 1

root = Tk()

# Naming the window and defining a window size
root.title("VMTAS")
root.iconbitmap('../img/vmtas_icon.ico')
root.geometry('1200x800')

# List of active (visible) plots
active_plots = {}
# Filename from "previous" .csv file
file_prev = None
# Filename from "live" .csv file
file_live = None
# Data from "previous" .csv file
file_prev_data = None
# Data from "live" .csv file
file_live_data = None
# Variable defining the mode
mode = Mode.NONE
# Basic Plot Setup
Plot, Axis = plt.subplots()
plt.subplots_adjust(bottom=0.25)
plt.style.use('dark_background')
# Is the scrollbar "playing?"
is_scrollbar_playing = False

# Track Map Variables
fig_track_map = Figure(figsize=(5,4), dpi=100)
ax_track_map = fig_track_map.add_subplot(111)
ax_track_map_2 = ax_track_map.twinx()
canvas_track_map = FigureCanvasTkAgg(fig_track_map)
(track_dot_prev,) = ax_track_map.plot(
    [], [], color="#ff0000", marker="o", markersize=12, zorder=4
)
(track_dot_live,) = ax_track_map.plot(
    [], [], color="#11ff00", marker="o", markersize=12, zorder=4
)

# G-G Plot Variables
fig_g_lat = Figure(figsize=(5,4), dpi=100)
ax_g_lat = fig_g_lat.add_subplot(111)
canvas_g_lat = FigureCanvasTkAgg(fig_g_lat)
fig_g_lon = Figure(figsize=(5,4), dpi=100)
ax_g_lon = fig_g_lon.add_subplot(111)
canvas_g_lon = FigureCanvasTkAgg(fig_g_lon)
(g_point_prev, ) = ax_g_lat.plot(
    [], [], color="#ffff00", marker="o", markersize=10, zorder=2
)
(g_point_live, ) = ax_g_lon.plot(
    [], [], color="#ffff00", marker="o", markersize=10, zorder=2
)


# FUNCTIONS

# Mode Selection
def mode_selection():
    """Determine the selected software mode and modify software options."""
    global mode
    mode_choice = mode_choice_var.get()
    if mode_choice == Mode.LIVE_RUN:
        mode = Mode.LIVE_RUN
        print("Live Run")
    elif mode_choice == Mode.PREVIOUS_RUN:
        mode = Mode.PREVIOUS_RUN
        print("Previous Run Review")

# File functions
def open_prev_file_dialog():
    """File dialog for first file"""
    global file_prev
    global file_prev_data
    file_path = filedialog.askopenfilename(initialdir = "/", title = "Select .csv to run",
                                           filetypes =(("csv files", "*.csv"),))
    if file_path:
        print(f"Selected File (First Slot): {file_path}")
        file_prev = file_path
        file_prev_data = pd.read_csv(file_prev)
        label_choose_prev_file.config(text=f"Selected File: {file_path.rsplit('/', 1)[-1]}")
    else:
        print("No file selected")


def open_live_file_dialog():
    """File dialog for second file"""
    global file_live
    global file_live_data
    file_path = filedialog.askopenfilename(initialdir = "/", title = "Select .csv to run",
                                           filetypes =(("csv files", "*.csv"),))
    if file_path:
        print(f"Selected File (Second Slot): {file_path}")
        file_live = file_path
        file_live_data = pd.read_csv(file_live)
        label_choose_live_file.config(text=f"Selected File: {file_path.rsplit('/', 1)[-1]}")
    else:
        print("No file selected")

def reset_prev():
    global file_prev
    global file_prev_data
    file_prev = None
    file_prev_data = None
    clear_data()
    label_choose_prev_file.config(text="Choose Previous Run .csv")

def reset_live():
    global file_live
    global file_live_data
    file_live = None
    file_live_data = None
    clear_data()
    label_choose_live_file.config(text="Choose Live/Previous Run .csv")

def clear_data():
    pane_track_map.pack_forget()
    pane_speed.pack_forget()
    pane_radius.pack_forget()
    pane_g_lat.pack_forget()
    pane_g_lon.pack_forget()
    pane_steering_angle.pack_forget()
    pane_accel_prs.pack_forget()
    pane_brake_prs.pack_forget()
    pane_yaw_vel.pack_forget()
    pane_yaw_acc.pack_forget()
    pane_slip_angle.pack_forget()
    pane_slip_ratio.pack_forget()
    pane_tire_fy.pack_forget()
    pane_roll_grad.pack_forget()
    pane_pitch_grad.pack_forget()
    pane_beta.pack_forget()
    pane_battery_power.pack_forget()
    pane_power_draw.pack_forget()

    for w in pane_track_map.winfo_children():
        w.destroy()
    for w in pane_speed.winfo_children():
        w.destroy()
    for w in pane_radius.winfo_children():
        w.destroy()
    for w in pane_g_lat.winfo_children():
        w.destroy()
    for w in pane_g_lon.winfo_children():
        w.destroy()
    for w in pane_steering_angle.winfo_children():
        w.destroy()
    for w in pane_accel_prs.winfo_children():
        w.destroy()
    for w in pane_brake_prs.winfo_children():
        w.destroy()
    for w in pane_yaw_vel.winfo_children():
        w.destroy()
    for w in pane_yaw_acc.winfo_children():
        w.destroy()
    for w in pane_slip_angle.winfo_children():
        w.destroy()
    for w in pane_slip_ratio.winfo_children():
        w.destroy()
    for w in pane_tire_fy.winfo_children():
        w.destroy()
    for w in pane_roll_grad.winfo_children():
        w.destroy()
    for w in pane_pitch_grad.winfo_children():
        w.destroy()
    for w in pane_beta.winfo_children():
        w.destroy()
    for w in pane_battery_power.winfo_children():
        w.destroy()
    for w in pane_power_draw.winfo_children():
        w.destroy()

    print("Data Cleared")


# Functions for options scrollbar whenever moving
def options_on_mousewheel(event):
  if event.delta:
    canvas_options.yview_scroll(int(-1 * (event.delta / 120)), "units")
  elif event.num == 4:
    canvas_options.yview_scroll(-1, "units")
  elif event.num == 5:
    canvas_options.yview_scroll(1, "units")


def options_bind_mousewheel(event):
  canvas_options.bind_all("<MouseWheel>", options_on_mousewheel)
  canvas_options.bind_all("<Button-4>", options_on_mousewheel)
  canvas_options.bind_all("<Button-5>", options_on_mousewheel)


def options_unbind_mousewheel(event):
  canvas_options.unbind_all("<MouseWheel>")
  canvas_options.unbind_all("<Button-4>")
  canvas_options.unbind_all("<Button-5>")

# Functions for data scrollbar whenever moving
def data_on_mousewheel(event):
  if event.delta:
    canvas_data.yview_scroll(int(-1 * (event.delta / 120)), "units")
  elif event.num == 4:
    canvas_data.yview_scroll(-1, "units")
  elif event.num == 5:
    canvas_data.yview_scroll(1, "units")


def data_bind_mousewheel(event):
  canvas_data.bind_all("<MouseWheel>", data_on_mousewheel)
  canvas_data.bind_all("<Button-4>", data_on_mousewheel)
  canvas_data.bind_all("<Button-5>", data_on_mousewheel)


def data_unbind_mousewheel(event):
  canvas_data.unbind_all("<MouseWheel>")
  canvas_data.unbind_all("<Button-4>")
  canvas_data.unbind_all("<Button-5>")

# Data-Related Functions

# Rendering Data
def render_plots():
    global file_prev
    global file_live
    global active_plots
    global mode
    global file_prev_data
    global file_live_data
    global fig_track_map
    global ax_track_map
    global canvas_track_map
    global fig_g_lat
    global ax_g_lat
    global fig_g_lon
    global ax_g_lon
    global canvas_g_lon
    global canvas_g_lat
    active_plots.clear()

    if file_prev:
        clear_data()

        if selected_track_map.get() == DatapointSelected.SELECTED:
            # TODO: Just a note, this is NOT on active plots because this should NOT be scrolling.
            pane_track_map.pack(fill="x", expand=True)
            ax_track_map.plot(file_prev_data.iloc[:, 0], file_prev_data.iloc[:, 1], color="#ffffff", linewidth = 5.0, zorder=3)
            ax_track_map.set_title("Track Map")
            canvas_track_map = FigureCanvasTkAgg(fig_track_map, master=pane_track_map)
            canvas_track_map.draw()
            canvas_track_map.get_tk_widget().pack(side="top", fill="both", expand=True)

        if selected_speed.get() == DatapointSelected.SELECTED:
            render_basic_plot(pane_speed, "speed", "Speed Plot", 5, "Speed (mph)", "#00afff", "#0075ff")
        if selected_radius.get() == DatapointSelected.SELECTED:
            render_basic_plot(pane_radius, "radius", "Radius Plot", 6, "Radius (ft)", "#ff5300", "#9b3200")
        if selected_g_lat.get() == DatapointSelected.SELECTED:
            # TODO: Just a note, this is NOT on active plots because this should NOT be scrolling.
            pane_g_lat.pack(fill="x", expand=True)
            ax_g_lat.scatter(file_prev_data.iloc[:, 7], file_prev_data.iloc[:, 8], color="#180cb9", marker="o", s=10, zorder=0)
            ax_g_lat.set_title("G-G Plot (Prev)")
            ax_g_lat.set_xlabel("Lateral Acceleration (g)")
            ax_g_lat.set_ylabel("Longitudinal Acceleration (g)")
            canvas_g_lat = FigureCanvasTkAgg(fig_g_lat, master=pane_g_lat)
            canvas_g_lat.draw()
            canvas_g_lat.get_tk_widget().pack(side="top", fill="both", expand=True)

        if selected_g_lon.get() == DatapointSelected.SELECTED:
            if file_live:
                pane_g_lon.pack(fill="x", expand=True)
                ax_g_lon.scatter(file_live_data.iloc[:, 7], file_live_data.iloc[:, 8], color="#5d0bba", marker="o", s=10, zorder=0)
                ax_g_lon.set_title("G-G Plot (Live)")
                ax_g_lon.set_xlabel("Lateral Acceleration (g)")
                ax_g_lon.set_ylabel("Longitudinal Acceleration (g)")
                canvas_g_lon = FigureCanvasTkAgg(fig_g_lon, master=pane_g_lon)
                canvas_g_lon.draw()
                canvas_g_lon.get_tk_widget().pack(side="top", fill="both", expand=True)
        else:
            selected_g_lon.set(DatapointSelected.NOT_SELECTED)

        if selected_steering_angle.get() == DatapointSelected.SELECTED:
            render_basic_plot(pane_steering_angle, "steering angle", "Steering Angle Plot", 9, "Angle (degrees)", "#ffffff", "#878787")
        if selected_accel_prs.get() == DatapointSelected.SELECTED:
            print("Acceleration Pressure Selected")
        if selected_brake_prs.get() == DatapointSelected.SELECTED:
            print("Brake Pressure Selected")
        if selected_yaw_vel.get() == DatapointSelected.SELECTED:
            yaw_vel_prev_data = file_prev_data.iloc[:, 5] * 1.4667 / file_prev_data.iloc[:, 6]
            pane_yaw_vel.pack(fill="x", expand=True)
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(file_prev_data.iloc[:, 2], yaw_vel_prev_data, color="#610091", linewidth=0.5)
            ax.set_title("Yaw Velocity Plot")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Yaw Velocity (rad/s)")
            canvas = FigureCanvasTkAgg(fig, master=pane_yaw_vel)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
            active_plots["yaw velocity"] = {"canvas": canvas, "axis": ax, "line": ax.axvline(x=0, color="red", linestyle="-", linewidth=1)}

            if file_live:
                yaw_vel_live_data = file_live_data.iloc[:, 5] * 1.4667 / file_live_data.iloc[:, 6]
                ax_2 = ax.twinx()
                ax_2.plot(file_live_data.iloc[:, 2], yaw_vel_live_data, color="#ab00ff", linewidth = 0.5)

        if selected_yaw_acc.get() == DatapointSelected.SELECTED:
            print("Yaw Acceleration Selected")
        if selected_slip_angle.get() == DatapointSelected.SELECTED:
            pane_slip_angle.pack(fill="x", expand=True)
            fig_slip_angle = Figure(figsize=(5, 4), dpi=100)
            ax_front_slip_angle = fig_slip_angle.add_subplot(111)
            line_front_slip = ax_front_slip_angle.plot(file_prev_data.iloc[:, 2], file_prev_data.iloc[:, 10], color="#a3b700",
                                                       linewidth=0.5, label="Front Slip")
            ax_front_slip_angle.set_title("Slip Angle Plot")
            ax_front_slip_angle.set_xlabel("Time (s)")
            ax_front_slip_angle.set_ylabel("Slip Angle (degrees)")
            ax_rear_slip_angle = ax_front_slip_angle.twinx()
            line_rear_slip = ax_rear_slip_angle.plot(file_prev_data.iloc[:, 2], file_prev_data.iloc[:, 11], color="#ae0073",
                                                     linewidth=0.5, label="Rear Slip")

            lines_slip = line_front_slip + line_rear_slip
            labels_slip = [l.get_label() for l in lines_slip]
            ax_front_slip_angle.legend(lines_slip, labels_slip, loc="upper right")

            canvas_slip_angle = FigureCanvasTkAgg(fig_slip_angle, master=pane_slip_angle)
            canvas_slip_angle.draw()
            canvas_slip_angle.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

            active_plots["front slip angle"] = {"canvas": canvas_slip_angle, "axis": ax_front_slip_angle, "line": ax_front_slip_angle.axvline(x=0, color="red", linestyle="-", linewidth=1)}
            active_plots["rear slip angle"] = {"canvas": canvas_slip_angle, "axis": ax_rear_slip_angle}

            if (file_live):
                ax_front_slip_angle_2 = ax_front_slip_angle.twinx()
                ax_front_slip_angle_2.plot(file_live_data.iloc[:, 2], file_live_data.iloc[:, 10], color="#e3ff00", linewidth=0.5)
                ax_rear_slip_angle_2 = ax_front_slip_angle.twinx()
                ax_rear_slip_angle_2.plot(file_live_data.iloc[:, 2], file_live_data.iloc[:, 11], color="#ff00a9", linewidth=0.5)
        if selected_slip_ratio == DatapointSelected.SELECTED:
            print("Slip Ratio Selected")
        if selected_tire_fy == DatapointSelected.SELECTED:
            # TODO: Ask about the tyre model
            print("Tire Fy Selected")
        if selected_roll_grad.get() == DatapointSelected.SELECTED:
            print("Roll Grad Selected")
        if selected_pitch_grad.get() == DatapointSelected.SELECTED:
            print("Pitch Grad Selected")
        if selected_beta.get() == DatapointSelected.SELECTED:
            render_basic_plot(pane_beta, "beta", "Beta Plot", 12, "Beta Angle (degrees)", "#00ffd3", "#00ae90")
        if selected_battery_power.get() == DatapointSelected.SELECTED:
            render_basic_plot(pane_battery_power, "battery power", "Battery Power Plot", 13, "Battery Power (kW)", "#ff3d00", "#cd3000")
        if selected_power_draw.get() == DatapointSelected.SELECTED:
            render_basic_plot(pane_power_draw, "power draw", "Power Draw Plot", 15, "Power Draw (%)", "#ffff00", "#909000")
    else:
        messagebox.showwarning("Error", "Please select a .csv file. Choose a run under \"Choose Previous Run .csv.\"")


# Basic Render Function
def render_basic_plot(pane, name, title, ycol, ylabel, color_live, color_prev):
    global file_live
    global file_live_data
    global file_prev_data

    pane.pack(fill="x", expand=True)
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(file_prev_data.iloc[:, 2], file_prev_data.iloc[:, ycol], color=color_prev, linewidth=0.5)
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(ylabel)
    canvas = FigureCanvasTkAgg(fig, master=pane)
    canvas.draw()
    canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
    active_plots[name] = {"canvas": canvas, "axis": ax, "line": ax.axvline(x=0, color="red", linestyle="-", linewidth=1)}

    if (file_live):
        ax_2 = ax.twinx()
        ax_2.plot(file_live_data.iloc[:, 2], file_live_data.iloc[:, ycol], color=color_live, linewidth=0.5)


# Updating Graphics with Slider
def update_all_plots(val):
    offset = float(val)
    if offset >= 4: offset -= 4
    else: offset = 0
    window_size = 8.0

    for plot in active_plots.values():
        plot["axis"].set_xlim(offset, offset + window_size)
        plot["canvas"].draw_idle()
        if plot["line"]:
            plot["line"].set_xdata([float(val), float(val)])

    time_col_prev = file_prev_data.iloc[:, 2].to_numpy()
    time_col_prev = pd.to_numeric(file_prev_data.iloc[:, 2], errors="coerce").to_numpy(
        dtype=float
    )
    closest_prev_row = np.nanargmin(np.abs(time_col_prev - float(val)))

    time_col_live = file_live_data.iloc[:, 2].to_numpy() if file_live else None
    time_col_live = pd.to_numeric(file_live_data.iloc[:, 2], errors="coerce").to_numpy(
        dtype=float
    ) if file_live else None
    closest_live_row = np.nanargmin(np.abs(time_col_live - float(val))) if file_live else None

    if (selected_track_map.get() == DatapointSelected.SELECTED):
        prev_x = file_prev_data.iloc[closest_prev_row, 0]
        prev_y = file_prev_data.iloc[closest_prev_row, 1]
        track_dot_prev.set_data([prev_x], [prev_y])

        if (file_live):
            live_x = file_live_data.iloc[closest_live_row, 0]
            live_y = file_live_data.iloc[closest_live_row, 1]
            track_dot_live.set_data([live_x], [live_y])

        canvas_track_map.draw()

    if (selected_g_lat.get() == DatapointSelected.SELECTED):
        g_point_prev.set_data([file_prev_data.iloc[closest_prev_row, 7]], [file_prev_data.iloc[closest_prev_row, 8]])
        canvas_g_lat.draw()

    if (selected_g_lon.get() == DatapointSelected.SELECTED):
        g_point_live.set_data([file_live_data.iloc[closest_live_row, 7]], [file_live_data.iloc[closest_live_row, 8]])
        canvas_g_lon.draw()

def animate_slider():
    global is_scrollbar_playing

    current_val = slider.get()
    should_move = False
    if is_scrollbar_playing:
        if current_val < float(slider.cget("to")):
            should_move = True
        else:
            return
    else:
        return

    if should_move:
        slider.set(current_val + 0.25)
    root.after(250, animate_slider)

def play_pause_scrollbar():
    global is_scrollbar_playing
    is_scrollbar_playing = not is_scrollbar_playing

    if is_scrollbar_playing:
        button_slider_play_pause.config(text="Pause")
        animate_slider()
    else:
        button_slider_play_pause.config(text="Play")


# Closing
def on_closing():
    root.destroy()
    sys.exit()


# GRAPHICS

# Constructing main pane and subpanes
pane = PanedWindow(root, orient="horizontal", sashrelief="sunken", sashwidth=4)
pane.pack(fill="both", expand=True)

pane_options = Frame(pane, width=300, height=800, relief="sunken")
pane_data = Frame(pane, width=900, height=800, relief="sunken")
pane.add(pane_options, minsize=260)
pane.add(pane_data, minsize=500)

# Building the options section
canvas_options = Canvas(pane_options)
scrollbar_options = Scrollbar(pane_options, orient="vertical", command=canvas_options.yview)
canvas_options.configure(yscrollcommand=scrollbar_options.set)
scrollbar_options.pack(side="right", fill="y")
canvas_options.pack(side="left", fill="both", expand=True)

# Making options pane scrollable
pane_options_scrollable = Frame(canvas_options)
pane_options_scrollable.bind(
    "<Configure>",
    lambda e: canvas_options.configure(scrollregion=canvas_options.bbox("all"))
)
canvas_options_window = canvas_options.create_window((0, 0), window=pane_options_scrollable, anchor="nw")
canvas_options.bind(
    "<Configure>",
    lambda e: canvas_options.itemconfig(canvas_options_window, width=e.width)
)
canvas_options.bind("<Enter>", options_bind_mousewheel)
canvas_options.bind("<Leave>", options_unbind_mousewheel)

# Adding Labels/Selection
label_choose_mode = Label(pane_options_scrollable, text="Mode Selection", font=("Segoe UI", 12), activeforeground="black",
                          anchor="w", justify="left")
label_choose_mode.grid(row=0, column=0, padx=5, pady=5, sticky="w")


mode_choice_var = IntVar()
mode_choice_var.set(Mode.LIVE_RUN)
radio_live = Radiobutton(pane_options_scrollable, text="Live Run", variable = mode_choice_var, value=Mode.LIVE_RUN,
                         padx = 0, pady = 0, bd = 0, anchor ="w", justify ="left")
radio_previous = Radiobutton(pane_options_scrollable, text="Previous Run Review", variable = mode_choice_var,
                             value=Mode.PREVIOUS_RUN, padx = 0, pady = 0, bd = 0, anchor ="w", justify ="left")
radio_live.grid(row=1, column=0, padx=5, pady=3, sticky="w")
radio_previous.grid(row=2, column=0, padx=5, pady=3, sticky="w")
button_mode_choice = Button(pane_options_scrollable, text="Confirm", command=mode_selection, justify="center", width=7,
                            height=1)
button_mode_choice.grid(row=3, column=0, padx=4, pady=3, sticky="w")


label_choose_prev_file = Label(pane_options_scrollable, text="Choose Previous Run .csv", font=("Segoe UI", 12),
                               activeforeground = "black", anchor = "w", justify = "left")
label_choose_prev_file.grid(row=5, column=0, padx=5, pady=5, sticky="w")
button_choose_prev_file = Button(pane_options_scrollable, text="Choose File", command=open_prev_file_dialog,
                                 justify="center", width = 10, height = 1)
button_choose_prev_file.grid(row=6, column=0, padx=4, pady=3, sticky="w")
button_prev_reset = Button(pane_options_scrollable, text="Reset", command=reset_prev, justify="center", width=6,
                           height=1)
button_prev_reset.grid(row=6, column=0, padx=100, pady=3, sticky="w")

label_choose_live_file = Label(pane_options_scrollable, text="Choose Live/Previous Run .csv", font=("Segoe UI", 12),
                               activeforeground = "black", anchor="w", justify="left")
label_choose_live_file.grid(row=8, column=0, padx=5, pady=5, sticky="w")
button_choose_live_file = Button(pane_options_scrollable, text="Choose File", command=open_live_file_dialog,
                                 justify="center", width=10, height=1)
button_choose_live_file.grid(row=9, column=0, padx=4, pady=3, sticky="w")
button_live_reset = Button(pane_options_scrollable, text="Reset", command=reset_live, justify="center", width=6,
                           height=1)
button_live_reset.grid(row=9, column=0, padx=100, pady=3, sticky="w")

label_select_datapoints = Label(pane_options_scrollable, text="Select Visible Datapoints", font=("Segoe UI", 12),
                                activeforeground="black", anchor="w", justify="left")
label_select_datapoints.grid(row=11, column=0, padx=5, pady=5, sticky="w")


selected_track_map = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_speed = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_radius = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_g_lat = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_g_lon = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_steering_angle = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_accel_prs = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_brake_prs = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_yaw_vel = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_yaw_acc = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_slip_angle = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_slip_ratio = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_tire_fy = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_roll_grad = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_pitch_grad = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_beta = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_battery_power = IntVar(value=DatapointSelected.NOT_SELECTED)
selected_power_draw = IntVar(value=DatapointSelected.NOT_SELECTED)

check_track_map = Checkbutton(pane_options_scrollable, text="Track Map", anchor="w", justify="left", variable=selected_track_map)
check_speed = Checkbutton(pane_options_scrollable, text="Vehicle Speed", anchor="w", justify="left", variable=selected_speed)
check_radius = Checkbutton(pane_options_scrollable, text="Radius", anchor="w", justify="left", variable=selected_radius)
check_g_lat = Checkbutton(pane_options_scrollable, text="G-Force (File 1)", anchor="w", justify="left", variable=selected_g_lat)
check_g_lon = Checkbutton(pane_options_scrollable, text="G-Force (File 2)", anchor="w", justify="left", variable=selected_g_lon)
check_steering_angle = Checkbutton(pane_options_scrollable, text="Steering Angle", anchor="w", justify="left", variable=selected_steering_angle)
check_accel_prs = Checkbutton(pane_options_scrollable, text="Acceleration Pressure", anchor="w", justify="left", variable=selected_accel_prs)
check_brake_prs = Checkbutton(pane_options_scrollable, text="Brake Pressure", anchor="w", justify="left", variable=selected_brake_prs)
check_yaw_vel = Checkbutton(pane_options_scrollable, text="Yaw Velocity", anchor="w", justify="left", variable=selected_yaw_vel)
check_yaw_acc = Checkbutton(pane_options_scrollable, text="Yaw Acceleration", anchor="w", justify="left", variable=selected_yaw_acc)
check_slip_angle = Checkbutton(pane_options_scrollable, text="Slip Angle", anchor="w", justify="left", variable=selected_slip_angle)
check_slip_ratio = Checkbutton(pane_options_scrollable, text="Slip Ratio", anchor="w", justify="left", variable=selected_slip_ratio)
check_tire_fy = Checkbutton(pane_options_scrollable, text="Tire Fy", anchor="w", justify="left", variable=selected_tire_fy)
check_roll_grad = Checkbutton(pane_options_scrollable, text="Roll Gradient", anchor="w", justify="left", variable=selected_roll_grad)
check_pitch_grad = Checkbutton(pane_options_scrollable, text="Pitch Gradient", anchor="w", justify="left", variable=selected_pitch_grad)
check_beta = Checkbutton(pane_options_scrollable, text="Beta", anchor = "w", justify="left", variable=selected_beta)
check_battery_power = Checkbutton(pane_options_scrollable, text="Battery Power", anchor="w", justify="left", variable=selected_battery_power)
check_power_draw = Checkbutton(pane_options_scrollable, text="Power Draw", anchor="w", justify="left", variable=selected_power_draw)

check_track_map.grid(row=12, column=0, padx=4, pady=3, sticky="w")
check_speed.grid(row=13, column=0, padx=4, pady=3, sticky="w")
check_radius.grid(row=14, column=0, padx=4, pady=3, sticky="w")
check_g_lat.grid(row=15, column=0, padx=4, pady=3, sticky="w")
check_g_lon.grid(row=16, column=0, padx=4, pady=3, sticky="w")
check_steering_angle.grid(row=17, column=0, padx=4, pady=3, sticky="w")
check_accel_prs.grid(row=18, column=0, padx=4, pady=3, sticky="w")
check_brake_prs.grid(row=19, column=0, padx=4, pady=3, sticky="w")
check_yaw_vel.grid(row=20, column=0, padx=4, pady=3, sticky="w")
check_yaw_acc.grid(row=21, column=0, padx=4, pady=3, sticky="w")
check_slip_angle.grid(row=22, column=0, padx=4, pady=3, sticky="w")
check_slip_ratio.grid(row=23, column=0, padx=4, pady=3, sticky="w")
check_tire_fy.grid(row=24, column=0, padx=4, pady=3, sticky="w")
check_roll_grad.grid(row=25, column=0, padx=4, pady=3, sticky="w")
check_pitch_grad.grid(row=26, column=0, padx=4, pady=3, sticky="w")
check_beta.grid(row=27, column=0, padx=4, pady=3, sticky="w")
check_battery_power.grid(row=28, column=0, padx=4, pady=3, sticky="w")
check_power_draw.grid(row=29, column=0, padx=4, pady=3, sticky="w")

button_visible_datapoints = Button(pane_options_scrollable, text="Confirm", command=render_plots, justify ="center", width=8, height=1)
button_visible_datapoints.grid(row=30, column=0, padx=5, pady=5, sticky="w")



# Building the data section
canvas_data = Canvas(pane_data)
scrollbar_data = Scrollbar(pane_data, orient="vertical", command=canvas_data.yview)
canvas_data.configure(yscrollcommand=scrollbar_data.set)
scrollbar_data.pack(side="right", fill="y")
canvas_data.pack(side="left", fill="both", expand=True)

# Making data pane scrollable
pane_data_scrollable = Frame(canvas_data)
pane_data_scrollable.bind(
    "<Configure>",
    lambda e: canvas_data.configure(scrollregion=canvas_data.bbox("all"))
)
canvas_data_window = canvas_data.create_window((0,0), window=pane_data_scrollable, anchor="nw")
canvas_data.bind(
    "<Configure>",
    lambda e: canvas_data.itemconfig(canvas_data_window, width=e.width)
)
canvas_data.bind("<Enter>", data_bind_mousewheel)
canvas_data.bind("<Leave>", data_unbind_mousewheel)

pane_track_map = Frame(pane_data_scrollable, relief="groove")
pane_speed = Frame(pane_data_scrollable, relief="groove")
pane_radius = Frame(pane_data_scrollable, relief="groove")
pane_g_lat = Frame(pane_data_scrollable, relief="groove")
pane_g_lon = Frame(pane_data_scrollable, relief="groove")
pane_steering_angle = Frame(pane_data_scrollable, relief="groove")
pane_accel_prs = Frame(pane_data_scrollable, relief="groove")
pane_brake_prs = Frame(pane_data_scrollable, relief="groove")
pane_yaw_vel = Frame(pane_data_scrollable, relief="groove")
pane_yaw_acc = Frame(pane_data_scrollable, relief="groove")
pane_slip_angle = Frame(pane_data_scrollable, relief="groove")
pane_slip_ratio = Frame(pane_data_scrollable, relief="groove")
pane_tire_fy = Frame(pane_data_scrollable, relief="groove")
pane_roll_grad = Frame(pane_data_scrollable, relief="groove")
pane_pitch_grad = Frame(pane_data_scrollable, relief="groove")
pane_beta = Frame(pane_data_scrollable, relief="groove")
pane_battery_power = Frame(pane_data_scrollable, relief="groove")
pane_power_draw = Frame(pane_data_scrollable, relief="groove")

slider = Scale(canvas_data, from_=0, to=100, orient="horizontal", label="Scroll", command=update_all_plots, resolution=0.001)
slider.pack(fill = "x", anchor = "n")
button_slider_play_pause = Button(canvas_data, text="Play", justify="center", width=6, height=1, command=play_pause_scrollbar)
button_slider_play_pause.pack(fill="x", anchor="nw")

# Finalizing
root.update_idletasks()
pane.sash_place(0, 300, 0)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

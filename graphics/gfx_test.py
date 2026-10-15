from tkinter import *
from tkinter import filedialog, messagebox
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
root.iconbitmap('../img/vmtas_icon.ico')
root.geometry('1200x800')
root.resizable(False, False)
active_plots = {}


# VARIABLES AND SETUP
file_prev = None
file_live = None
mode = 0
Plot, Axis = plt.subplots()
plt.subplots_adjust(bottom=0.25)
plt.style.use('dark_background')


def mode_selection():
    """Determine the selected software mode and modify software options."""
    global mode
    mode_choice = mode_choice_var.get()
    if mode_choice == 1:
        mode = 1
        print("Live Run")
    elif mode_choice == 2:
        mode = 2
        print("Previous Run Review")

def render_plots():
    """Displays selected graphs based on selected file (if a file is selected)."""
    global file_prev
    global active_plots
    global mode
    active_plots.clear()

    if (file_prev):
        data = pd.read_csv(file_prev)
        data2 = None
        if (file_live):
            data2 = pd.read_csv(file_live)

        pane_speed.pack_forget()
        for w in pane_speed.winfo_children():
            w.destroy()
        if selected_speed.get() == 1:
            pane_speed.pack(fill="x", expand=True)
            fig_speed = Figure(figsize = (5, 4), dpi = 100)
            ax_speed = fig_speed.add_subplot(111)
            ax_speed.plot(data.iloc[:, 0], data.iloc[:, 3], color = "#00afff", linewidth = 0.5)
            ax_speed.set_title("Speed Plot")
            ax_speed.set_xlabel("Time (s)")
            ax_speed.set_ylabel("Speed (mph)")
            canvas_speed = FigureCanvasTkAgg(fig_speed, master = pane_speed)
            canvas_speed.draw()
            canvas_speed.get_tk_widget().pack(side = TOP, fill = BOTH, expand=True)

            active_plots["speed"] = {"canvas": canvas_speed, "axis": ax_speed}

            if (file_live):
                ax_speed_2 = ax_speed.twinx()
                ax_speed_2.plot(data2.iloc[:, 0], data2.iloc[:, 3], color = "#0075ff", linewidth = 0.5)


        pane_radius.pack_forget()
        for w in pane_radius.winfo_children():
            w.destroy()
        if selected_radius.get() == 1:
            pane_radius.pack(fill="x", expand=True)
            fig_radius = Figure(figsize = (5, 4), dpi = 100)
            ax_radius = fig_radius.add_subplot(111)
            ax_radius.plot(data.iloc[:, 0], data.iloc[:, 4], color = "#ff5300", linewidth = 0.5)
            ax_radius.set_title("Radius Plot")
            ax_radius.set_xlabel("Time (s)")
            ax_radius.set_ylabel("Radius (ft)")
            canvas_radius = FigureCanvasTkAgg(fig_radius, master = pane_radius)
            canvas_radius.draw()
            canvas_radius.get_tk_widget().pack(side = TOP, fill = BOTH, expand=True)

            active_plots["radius"] = {"canvas": canvas_radius, "axis": ax_radius}

        pane_steering_angle.pack_forget()
        for w in pane_steering_angle.winfo_children():
            w.destroy()
        if selected_steering_angle.get() == 1:
            pane_steering_angle.pack(fill="x", expand=True)
            fig_steering_angle = Figure(figsize = (5, 4), dpi = 100)
            ax_steering_angle = fig_steering_angle.add_subplot(111)
            ax_steering_angle.plot(data.iloc[:, 0], data.iloc[:, 7], color = "#ffffff", linewidth = 0.5)
            ax_steering_angle.set_title("Steering Angle Plot")
            ax_steering_angle.set_xlabel("Time (s)")
            ax_steering_angle.set_ylabel("Angle (degrees)")
            canvas_steering_angle = FigureCanvasTkAgg(fig_steering_angle, master = pane_steering_angle)
            canvas_steering_angle.draw()
            canvas_steering_angle.get_tk_widget().pack(side = TOP, fill = BOTH, expand=True)

            active_plots["steering angle"] = {"canvas": canvas_steering_angle, "axis": ax_steering_angle}

        pane_slip_angle.pack_forget()
        for w in pane_slip_angle.winfo_children():
            w.destroy()
        if selected_slip_angle.get() == 1:
            pane_slip_angle.pack(fill="x", expand=True)
            fig_slip_angle = Figure(figsize = (5, 4), dpi = 100)
            ax_front_slip_angle = fig_slip_angle.add_subplot(111)
            line_front_slip = ax_front_slip_angle.plot(data.iloc[:, 0], data.iloc[:, 8], color = "#e3ff00",
                                                    linewidth = 0.5, label = "Front Slip")
            ax_front_slip_angle.set_title("Slip Angle Plot")
            ax_front_slip_angle.set_xlabel("Time (s)")
            ax_front_slip_angle.set_ylabel("Slip Angle (degrees)")
            ax_rear_slip_angle = ax_front_slip_angle.twinx()
            line_rear_slip = ax_rear_slip_angle.plot(data.iloc[:, 0], data.iloc[:, 9], color = "#ff00a9",
                                                     linewidth = 0.5, label = "Rear Slip")

            lines_slip = line_front_slip + line_rear_slip
            labels_slip = [l.get_label() for l in lines_slip]
            ax_front_slip_angle.legend(lines_slip, labels_slip, loc = "upper right")

            canvas_slip_angle = FigureCanvasTkAgg(fig_slip_angle, master = pane_slip_angle)
            canvas_slip_angle.draw()
            canvas_slip_angle.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)

            active_plots["front slip angle"] = {"canvas": canvas_slip_angle, "axis": ax_front_slip_angle}
            active_plots["rear slip angle"] = {"canvas": canvas_slip_angle, "axis": ax_rear_slip_angle}

        pane_beta.pack_forget()
        for w in pane_beta.winfo_children():
            w.destroy()
        if selected_beta.get() == 1:
            pane_beta.pack(fill="x", expand=True)
            fig_beta = Figure(figsize = (5, 4), dpi = 100)
            ax_beta = fig_beta.add_subplot(111)
            ax_beta.plot(data.iloc[:, 0], data.iloc[:, 10], color = "#00ffd3", linewidth = 0.5)
            ax_beta.set_title("Beta Plot")
            ax_beta.set_xlabel("Time (s)")
            ax_beta.set_ylabel("Beta Angle (degrees)")
            canvas_beta = FigureCanvasTkAgg(fig_beta, master = pane_beta)
            canvas_beta.draw()
            canvas_beta.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)

            active_plots["beta"] = {"canvas": canvas_beta, "axis": ax_beta}

        pane_battery_power.pack_forget()
        for w in pane_battery_power.winfo_children():
            w.destroy()
        if selected_battery_power.get() == 1:
            pane_battery_power.pack(fill="x", expand=True)
            fig_battery_power = Figure(figsize = (5, 4), dpi = 100)
            ax_battery_power = fig_battery_power.add_subplot(111)
            ax_battery_power.plot(data.iloc[:, 0], data.iloc[:, 11], color = "#ff3d00", linewidth = 0.5)
            ax_battery_power.set_title("Battery Power Plot")
            ax_battery_power.set_xlabel("Time (s)")
            ax_battery_power.set_ylabel("Battery Power (kW)")
            canvas_battery_power = FigureCanvasTkAgg(fig_battery_power, master = pane_battery_power)
            canvas_battery_power.draw()
            canvas_battery_power.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)

            active_plots["battery power"] = {"canvas": canvas_battery_power, "axis": ax_battery_power}

        pane_power_draw.pack_forget()
        for w in pane_power_draw.winfo_children():
            w.destroy()
        if selected_power_draw.get() == 1:
            pane_power_draw.pack(fill="x", expand=True)
            fig_power_draw = Figure(figsize = (5, 4), dpi = 100)
            ax_power_draw = fig_power_draw.add_subplot(111)
            ax_power_draw.plot(data.iloc[:, 0], data.iloc[:, 13], color = "#ffff00", linewidth = 0.5)
            ax_power_draw.set_title("Power Draw Plot")
            ax_power_draw.set_xlabel("Time (s)")
            ax_power_draw.set_ylabel("Power Draw (%)")
            canvas_power_draw = FigureCanvasTkAgg(fig_power_draw, master = pane_power_draw)
            canvas_power_draw.draw()
            canvas_power_draw.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)

            active_plots["power draw"] = {"canvas": canvas_power_draw, "axis": ax_power_draw}



    else:
        messagebox.showwarning("Error", "Please select a .csv file")


def update_all_plots(val):
    for plot in active_plots.values():
        offset = float(val)
        window_size = 10.0

        plot["axis"].set_xlim(offset, offset + window_size)
        plot["canvas"].draw_idle()


def open_prev_file_dialog():
    global file_prev
    file_path = filedialog.askopenfilename(initialdir = "/", title = "Select .csv to run",
                                           filetypes =(("csv files", "*.csv"),))
    if file_path:
        print(f"Selected File: {file_path}")
        file_prev = file_path
    else:
        print("No file selected")

def open_live_file_dialog():
    global file_live
    file_path = filedialog.askopenfilename(initialdir = "/", title = "Select .csv to run",
                                           filetypes =(("csv files", "*.csv"),))
    if file_path:
        print(f"Selected File: {file_path}")
        file_live = file_path
    else:
        print("No file selected")

def reset_prev():
    global file_prev
    file_prev = None
    clear_data()

def reset_live():
    global file_live
    file_live = None
    clear_data()

def clear_data():
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

def _on_mousewheel(event):
  # Windows & macOS
  if event.delta:
    canvas_data.yview_scroll(int(-1 * (event.delta / 120)), "units")
  # Linux scroll up
  elif event.num == 4:
    canvas_data.yview_scroll(-1, "units")
  # Linux scroll down
  elif event.num == 5:
    canvas_data.yview_scroll(1, "units")


def _bind_mousewheel(event):
  canvas_data.bind_all("<MouseWheel>", _on_mousewheel)
  canvas_data.bind_all("<Button-4>", _on_mousewheel)
  canvas_data.bind_all("<Button-5>", _on_mousewheel)


def _unbind_mousewheel(event):
  canvas_data.unbind_all("<MouseWheel>")
  canvas_data.unbind_all("<Button-4>")
  canvas_data.unbind_all("<Button-5>")


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

button_choose_files = Button(pane_options, text = "Choose File", command = open_prev_file_dialog, justify = "center", width = 20, height = 8)
button_choose_files.place(anchor = "nw", relx = 0.01, rely = 0.20, relheight = 0.03)

button_prev_reset = Button(pane_options, text = "Reset", command = reset_prev, justify = "center", width = 20, height = 8)
button_prev_reset.place(anchor = "nw", relx = 0.55, rely = 0.20, relwidth = 0.25, relheight = 0.03)

label_choose_files_2 = Label(pane_options, text="Choose Live/Previous Run .csv", font = ("Segoe UI", 12), activeforeground = "black",
                             anchor = "w", justify = "left")
label_choose_files_2.place(anchor = "nw", relx = 0.01, rely = 0.25, relheight = 0.04)

button_choose_files_2 = Button(pane_options, text = "Choose File", command = open_live_file_dialog, justify = "center", width = 20, height = 8)
button_choose_files_2.place(anchor = "nw", relx = 0.01, rely = 0.29, relheight = 0.03)

button_live_reset = Button(pane_options, text = "Reset", command = reset_live, justify = "center", width = 20, height = 8)
button_live_reset.place(anchor = "nw", relx = 0.55, rely = 0.29, relwidth = 0.25, relheight = 0.03)


label_select_datapoints = Label(pane_options, text="Select Visible Datapoints", font = ("Segoe UI", 12),
                                activeforeground = "black", anchor = "w", justify = "left")
label_select_datapoints.place(anchor = "nw", relx = 0.01, rely = 0.32, relheight = 0.04)

selected_speed = IntVar()
selected_radius = IntVar()
selected_g_lat = IntVar()
selected_g_lon = IntVar()
selected_steering_angle = IntVar()
selected_accel_prs = IntVar()
selected_brake_prs = IntVar()
selected_yaw_vel = IntVar()
selected_yaw_acc = IntVar()
selected_slip_angle = IntVar()
selected_slip_ratio = IntVar()
selected_tire_fy = IntVar()
selected_roll_grad = IntVar()
selected_pitch_grad = IntVar()
selected_beta = IntVar()
selected_battery_power = IntVar()
selected_power_draw = IntVar()

check_speed = Checkbutton(pane_options, text = "Vehicle Speed", anchor = "w", justify = "left", variable = selected_speed)
check_radius = Checkbutton(pane_options, text = "Radius", anchor = "w", justify = "left", variable = selected_radius)
check_g_lat = Checkbutton(pane_options, text = "Lateral G-Force", anchor = "w", justify = "left", variable = selected_g_lat)
check_g_lon = Checkbutton(pane_options, text = "Longitudinal G-Force", anchor = "w", justify = "left", variable = selected_g_lon)
check_steering_angle = Checkbutton(pane_options, text = "Steering Angle", anchor = "w", justify = "left", variable = selected_steering_angle)
check_accel_prs = Checkbutton(pane_options, text = "Acceleration Pressure", anchor = "w", justify = "left", variable = selected_accel_prs)
check_brake_prs = Checkbutton(pane_options, text = "Brake Pressure", anchor = "w", justify = "left", variable = selected_brake_prs)
check_yaw_vel = Checkbutton(pane_options, text = "Yaw Velocity", anchor = "w", justify = "left", variable = selected_yaw_vel)
check_yaw_acc = Checkbutton(pane_options, text = "Yaw Acceleration", anchor = "w", justify = "left", variable = selected_yaw_acc)
check_slip_angle = Checkbutton(pane_options, text = "Slip Angle", anchor = "w", justify = "left", variable = selected_slip_angle)
check_slip_ratio = Checkbutton(pane_options, text = "Slip Ratio", anchor = "w", justify = "left", variable = selected_slip_ratio)
check_tire_fy = Checkbutton(pane_options, text = "Tire Fy", anchor = "w", justify = "left", variable = selected_tire_fy)
check_roll_grad = Checkbutton(pane_options, text = "Roll Gradient", anchor = "w", justify = "left", variable = selected_roll_grad)
check_pitch_grad = Checkbutton(pane_options, text = "Pitch Gradient", anchor = "w", justify = "left", variable = selected_pitch_grad)
check_beta = Checkbutton(pane_options, text = "Beta", anchor = "w", justify = "left", variable = selected_beta)
check_battery_power = Checkbutton(pane_options, text = "Battery Power", anchor = "w", justify = "left", variable = selected_battery_power)
check_power_draw = Checkbutton(pane_options, text = "Power Draw", anchor = "w", justify = "left", variable = selected_power_draw)

check_speed.place(anchor = "nw", relx = 0.01, rely = 0.35, relheight = 0.05)
check_radius.place(anchor = "nw", relx = 0.01, rely = 0.385, relheight = 0.05)
check_g_lat.place(anchor = "nw", relx = 0.01, rely = 0.42, relheight = 0.05)
check_g_lon.place(anchor = "nw", relx = 0.01, rely = 0.455, relheight = 0.05)
check_steering_angle.place(anchor = "nw", relx = 0.01, rely = 0.49, relheight = 0.05)
check_accel_prs.place(anchor = "nw", relx = 0.01, rely = 0.525, relheight = 0.05)
check_brake_prs.place(anchor = "nw", relx = 0.01, rely = 0.56, relheight = 0.05)
check_yaw_vel.place(anchor = "nw", relx = 0.01, rely = 0.595, relheight = 0.05)
check_yaw_acc.place(anchor = "nw", relx = 0.01, rely = 0.63, relheight = 0.05)
check_slip_angle.place(anchor = "nw", relx = 0.01, rely = 0.665, relheight = 0.05)
check_slip_ratio.place(anchor = "nw", relx = 0.01, rely = 0.70, relheight = 0.05)
check_tire_fy.place(anchor = "nw", relx = 0.01, rely = 0.735, relheight = 0.05)
check_roll_grad.place(anchor = "nw", relx = 0.01, rely = 0.77, relheight = 0.05)
check_pitch_grad.place(anchor = "nw", relx = 0.01, rely = 0.805, relheight = 0.05)
check_beta.place(anchor = "nw", relx = 0.01, rely = 0.84, relheight = 0.05)
check_battery_power.place(anchor = "nw", relx = 0.01, rely = 0.875, relheight = 0.05)
check_power_draw.place(anchor = "nw", relx = 0.01, rely = 0.910, relheight = 0.05)

button_visible_datapoints = Button(pane_options, text ="Confirm", command = render_plots, justify ="center", width = 20, height = 8)
button_visible_datapoints.place(anchor ="nw", relx = 0.01, rely = 0.96, relheight = 0.03)


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

canvas_data.bind("<Enter>", _bind_mousewheel)
canvas_data.bind("<Leave>", _unbind_mousewheel)

pane_speed = Frame(pane_scrollable, relief = "groove")
pane_radius = Frame(pane_scrollable, relief = "groove")
pane_g_lat = Frame(pane_scrollable, relief = "groove")
pane_g_lon = Frame(pane_scrollable, relief = "groove")
pane_steering_angle = Frame(pane_scrollable, relief = "groove")
pane_accel_prs = Frame(pane_scrollable, relief = "groove")
pane_brake_prs = Frame(pane_scrollable, relief = "groove")
pane_yaw_vel = Frame(pane_scrollable, relief = "groove")
pane_yaw_acc = Frame(pane_scrollable, relief = "groove")
pane_slip_angle = Frame(pane_scrollable, relief = "groove")
pane_slip_ratio = Frame(pane_scrollable, relief = "groove")
pane_tire_fy = Frame(pane_scrollable, relief = "groove")
pane_roll_grad = Frame(pane_scrollable, relief = "groove")
pane_pitch_grad = Frame(pane_scrollable, relief = "groove")
pane_beta = Frame(pane_scrollable, relief = "groove")
pane_battery_power = Frame(pane_scrollable, relief = "groove")
pane_power_draw = Frame(pane_scrollable, relief = "groove")

slider = Scale(canvas_data, from_=0, to=100, orient="horizontal", label="Scroll", command=update_all_plots)
slider.pack(fill="x", anchor="n", expand=True)

pane.add(pane_options)
pane.add(pane_data)
root.update_idletasks()
pane.sash_place(0, 300, 0)
# Always the last line in your program.
root.mainloop()

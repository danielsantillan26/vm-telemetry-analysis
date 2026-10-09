from tkinter import *

root = Tk()

# Virginia Motorsports Telemetry Analysis Software
root.title("VMTAS")
root.iconbitmap('../img/vmtas_icon.ico')
root.geometry('1200x800')
root.resizable(False, False)





# FUNCTIONS

def mode_selection():
    """Determine the selected software mode and modify software options."""
    mode_choice = mode_choice_var.get()
    if mode_choice == 1:
        print("Live Run")
    elif mode_choice == 2:
        print("Previous Run Review")

def datapoint_selection():
    print("Pressed")




# GRAPHICS
# Starting with the options section... put all of this in a paned window
label_choose_mode = Label(root, text = "Mode Selection", font = ("Segoe UI", 12), activeforeground = "black",
                          anchor = "w", justify = "left")
label_choose_mode.place(anchor = "nw", relx = 0.01, rely = 0.01, relwidth = 0.25, relheight = 0.04)



mode_choice_var = IntVar()
mode_choice_var.set(1)

radio_live = Radiobutton(root, text ="Live Run", variable = mode_choice_var, value=1, padx = 0, pady = 0, bd = 0, anchor ="w", justify ="left")
radio_previous = Radiobutton(root, text ="Previous Run Review", variable = mode_choice_var, value=2, padx = 0, pady = 0, bd = 0, anchor ="w", justify ="left")
radio_live.place(anchor ="nw", relx = 0.01, rely = 0.04, relwidth = 0.25, relheight = 0.05)
radio_previous.place(anchor ="nw", relx = 0.01, rely = 0.07, relwidth = 0.25, relheight = 0.05)

button_mode_choice = Button(root, text ="Confirm", command = mode_selection, justify ="center", width = 20, height = 8)
button_mode_choice.place(anchor ="nw", relx = 0.01, rely = 0.11, relheight = 0.03)



label_choose_files = Label(root, text="Choose Previous Run .csv", font = ("Segoe UI", 12), activeforeground = "black",
                           anchor = "w", justify = "left")
label_choose_files.place(anchor = "nw", relx = 0.01, rely = 0.16, relwidth = 0.25, relheight = 0.04)

# TODO: Add a place to pick files. For now, we are running off a pre-worked .csv set.



label_select_datapoints = Label(root, text="Select Visible Datapoints", font = ("Segoe UI", 12),
                                activeforeground = "black", anchor = "w", justify = "left")
label_select_datapoints.place(anchor = "nw", relx = 0.01, rely = 0.25, relwidth = 0.25, relheight = 0.04)

check_speed = Checkbutton(root, text = "Vehicle Speed", anchor = "w", justify = "left")
check_radius = Checkbutton(root, text = "Radius", anchor = "w", justify = "left")
check_g_lat = Checkbutton(root, text = "Lateral G-Force", anchor = "w", justify = "left")
check_g_lon = Checkbutton(root, text = "Longitudinal G-Force", anchor = "w", justify = "left")
check_accel_prs = Checkbutton(root, text = "Acceleration Pressure", anchor = "w", justify = "left")
check_brake_prs = Checkbutton(root, text = "Brake Pressure", anchor = "w", justify = "left")
check_yaw_vel = Checkbutton(root, text = "Yaw Velocity", anchor = "w", justify = "left")
check_yaw_acc = Checkbutton(root, text = "Yaw Acceleration", anchor = "w", justify = "left")
check_slip_angle = Checkbutton(root, text = "Slip Angle", anchor = "w", justify = "left")
check_slip_ratio = Checkbutton(root, text = "Slip Ratio", anchor = "w", justify = "left")
check_tire_fy = Checkbutton(root, text = "Tire Fy", anchor = "w", justify = "left")
check_roll_grad = Checkbutton(root, text = "Roll Gradient", anchor = "w", justify = "left")
check_pitch_grad = Checkbutton(root, text = "Pitch Gradient", anchor = "w", justify = "left")

check_speed.place(anchor = "nw", relx = 0.01, rely = 0.28, relwidth = 0.25, relheight = 0.05)
check_radius.place(anchor = "nw", relx = 0.01, rely = 0.31, relwidth = 0.25, relheight = 0.05)
check_g_lat.place(anchor = "nw", relx = 0.01, rely = 0.34, relwidth = 0.25, relheight = 0.05)
check_g_lon.place(anchor = "nw", relx = 0.01, rely = 0.37, relwidth = 0.25, relheight = 0.05)
check_accel_prs.place(anchor = "nw", relx = 0.01, rely = 0.40, relwidth = 0.25, relheight = 0.05)
check_brake_prs.place(anchor = "nw", relx = 0.01, rely = 0.43, relwidth = 0.25, relheight = 0.05)
check_yaw_vel.place(anchor = "nw", relx = 0.01, rely = 0.46, relwidth = 0.25, relheight = 0.05)
check_yaw_acc.place(anchor = "nw", relx = 0.01, rely = 0.49, relwidth = 0.25, relheight = 0.05)
check_slip_angle.place(anchor = "nw", relx = 0.01, rely = 0.52, relwidth = 0.25, relheight = 0.05)
check_slip_ratio.place(anchor = "nw", relx = 0.01, rely = 0.55, relwidth = 0.25, relheight = 0.05)
check_tire_fy.place(anchor = "nw", relx = 0.01, rely = 0.58, relwidth = 0.25, relheight = 0.05)
check_roll_grad.place(anchor = "nw", relx = 0.01, rely = 0.61, relwidth = 0.25, relheight = 0.05)
check_pitch_grad.place(anchor = "nw", relx = 0.01, rely = 0.64, relwidth = 0.25, relheight = 0.05)

button_visible_datapoints = Button(root, text ="Confirm", command = datapoint_selection, justify ="center", width = 20, height = 8)
button_visible_datapoints.place(anchor ="nw", relx = 0.01, rely = 0.69, relheight = 0.03)

# Always the last line in your program.
root.mainloop()
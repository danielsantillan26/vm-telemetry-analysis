from tkinter import *
from tkinter import messagebox
import subprocess, sys
import sqlite3
import hashlib
import socket

root = Tk()

root.title("VMTAS Login")
root.iconbitmap('../img/vmtas_icon.ico')
root.geometry('800x800')

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))

server.listen()

def on_closing():
    root.destroy()
    sys.exit()

def show_hide_login_pw():
    if entry_login_password.cget("show") == "*":
        entry_login_password.config(show="")
        button_login_show_hide.config(text="Hide Password")
    else:
        entry_login_password.config(show="*")
        button_login_show_hide.config(text="Show Password")

def show_hide_register_pw():
    if entry_register_password.cget("show") == "*":
        entry_register_password.config(show="")
        button_register_show_hide.config(text="Hide Password")
    else:
        entry_register_password.config(show="*")
        button_register_show_hide.config(text="Show Password")

def register():
    username = entry_register_username.get()
    password = entry_register_password.get()

    if not username or not password:
        messagebox.showwarning("Error", "Registration Failed: No username/password given.")
    else:
        conn = sqlite3.connect("../logins/userdata.db")
        cur = conn.cursor()

        password = hashlib.sha256(password.encode()).hexdigest()

        cur.execute("SELECT * FROM userdata WHERE username = ?", (username,))
        if cur.fetchall():
            messagebox.showwarning("Error", "Registration Failed: Username already exists")
        else:
            cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username, password))
            messagebox.showinfo("Success", "Registration Success: Log in to access VMTAS.")

        conn.commit()
        entry_register_username.delete(0, END)
        entry_register_password.delete(0, END)


def login():
    username = entry_login_username.get()
    password = hashlib.sha256(entry_login_password.get().encode()).hexdigest()

    conn = sqlite3.connect("../logins/userdata.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, password))

    if cur.fetchall():
        open_program()
    else:
        messagebox.showwarning("Error", "Login Invalid. Try again.")

def open_program():
    root.destroy()
    subprocess.run([sys.executable, "telemetry.py"])


label_login = Label(root, text="Login", font=("Segoe UI", 24), activeforeground="black", anchor="w", justify="left")
label_login.grid(row=0, column=0, padx=20, pady=5, sticky="w")
label_login_username = Label(root, text="Username", font=("Segoe UI", 15), activeforeground="black", anchor="w", justify="left")
label_login_username.grid(row=1, column=0, padx=20, pady=5, sticky="w")
entry_login_username = Entry(root, width=80, font=("Segoe UI", 12))
entry_login_username.grid(row=2, column=0, padx=20, pady=5, sticky="w")
label_login_password = Label(root, text="Password", font=("Segoe UI", 15), activeforeground="black", anchor="w", justify="left")
label_login_password.grid(row=3, column=0, padx=20, pady=5, sticky="w")
entry_login_password = Entry(root, width=80, font=("Segoe UI", 12), show="*")
entry_login_password.grid(row=4, column=0, padx=20, pady=5, sticky="w")
button_login = Button(root, text="Login", font=("Segoe UI", 13), command=login)
button_login.grid(row=6, column=0, padx=20, pady=5, sticky="w")
button_login_show_hide = Button(root, text="Show Password", font=("Segoe UI", 13), command=show_hide_login_pw)
button_login_show_hide.grid(row=5, column=0, padx=20, pady=5, sticky="w")
label_register = Label(root, text="Register", font=("Segoe UI", 24), activeforeground="black", anchor="w", justify="left")
label_register.grid(row=7, column=0, padx=20, pady=5, sticky="w")
label_register_username = Label(root, text="Username", font=("Segoe UI", 15), activeforeground="black", anchor="w", justify="left")
label_register_username.grid(row=8, column=0, padx=20, pady=5, sticky="w")
entry_register_username = Entry(root, width=80, font=("Segoe UI", 12))
entry_register_username.grid(row=9, column=0, padx=20, pady=5, sticky="w")
label_register_password = Label(root, text="Password", font=("Segoe UI", 15), activeforeground="black", anchor="w", justify="left")
label_register_password.grid(row=10, column=0, padx=20, pady=5, sticky="w")
entry_register_password = Entry(root, width=80, font=("Segoe UI", 12), show="*")
entry_register_password.grid(row=11, column=0, padx=20, pady=5, sticky="w")
button_register_show_hide = Button(root, text="Show Password", font=("Segoe UI", 13), command=show_hide_register_pw)
button_register_show_hide.grid(row=12, column=0,padx=20, pady=5, sticky="w")
button_register = Button(root, text="Register", font=("Segoe UI", 13), command=register)
button_register.grid(row=13, column=0, padx=20, pady=5, sticky="w")


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()



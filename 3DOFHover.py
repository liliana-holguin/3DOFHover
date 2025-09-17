# Full Combined GUI for 3DOF Hovercraft with Pixhawk Control
# Includes Motor Control, Real-Time Orientation Plotting, and Data Logging
# Author: Liliana Holguin
# Date: April 2025

import tkinter as tk  # Tkinter for GUI components
from tkinter import ttk  # ttk for Notebook tab interface
from matplotlib.figure import Figure  # For plotting graphs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Embedding matplotlib in Tkinter
from pymavlink import mavutil  # MAVLink communication
import threading  # For running background data reading
import time  # Time tracking for plots
import csv  # Writing to CSV files
import datetime  # Timestamp logging

# ---------------- MAVLink Connection ----------------
# Connect to Pixhawk via UDP (change to your own connection method if needed)
master = mavutil.mavlink_connection('udp:localhost:14550')
master.wait_heartbeat()  # Wait for the Pixhawk to respond

# ---------------- Tkinter Main Window ----------------
root = tk.Tk()  # Initialize the root window
root.title("3DOF Hovercraft Control GUI")  # Title of the window
root.geometry("1000x600")  # Set window size

# Create notebook (tabbed interface)
notebook = ttk.Notebook(root)  # Container for tabs
notebook.pack(fill='both', expand=True)  # Expand to fit window

# ---------------- Motor Control Tab ----------------
motor_tab = ttk.Frame(notebook)  # Create new tab
notebook.add(motor_tab, text="Motor Control")  # Add tab to notebook

# Function to send motor control commands to Pixhawk
# Takes values from entry fields and sends them via MAVLink
def send_motor_command():
    master.mav.manual_control_send(
        master.target_system,
        int(entry_x.get()),  # Forward/backward
        int(entry_y.get()),  # Left/right
        int(entry_z.get()),  # Up/down
        0,  # No rotation
        0   # No button flags
    )
    label_status.config(text="Command Sent!")  # Update status

# Entry fields for X, Y, Z motor directions
entry_x = tk.Entry(motor_tab)
entry_x.insert(0, "X Value")
entry_x.pack(pady=5)

entry_y = tk.Entry(motor_tab)
entry_y.insert(0, "Y Value")
entry_y.pack(pady=5)

entry_z = tk.Entry(motor_tab)
entry_z.insert(0, "Z Value")
entry_z.pack(pady=5)

# Button to trigger send_motor_command
btn_send = tk.Button(motor_tab, text="Send Command", command=send_motor_command)
btn_send.pack(pady=10)

# Label for status feedback
label_status = tk.Label(motor_tab, text="Enter motor values and click send")
label_status.pack()

# ---------------- Real-Time Graph Tab ----------------
graph_tab = ttk.Frame(notebook)  # Create new tab for graph
notebook.add(graph_tab, text="Orientation Graph")  # Add graph tab

# Create Matplotlib figure for orientation plotting
fig = Figure(figsize=(6,4), dpi=100)
plot = fig.add_subplot(111)
plot.set_title("Real-Time Roll, Pitch, Yaw")
plot.set_xlabel("Time (s)")
plot.set_ylabel("Degrees")

# Embed the figure in the Tkinter GUI
canvas = FigureCanvasTkAgg(fig, master=graph_tab)
canvas.get_tk_widget().pack()

# Initialize data lists to hold plot values
roll_data = []
pitch_data = []
yaw_data = []
time_data = []
start_time = time.time()  # Track time since GUI start

should_plot = True  # Used to toggle plotting

# Function to redraw the canvas periodically
def update_graph():
    if should_plot:
        canvas.draw()  # Redraw graph with new data
    root.after(1000, update_graph)  # Schedule next update in 1 second

# Background thread to receive and plot attitude messages from Pixhawk
# Converts radians to degrees and limits history to 50 points
def read_attitude():
    while True:
        msg = master.recv_match(type='ATTITUDE', blocking=True)
        if msg:
            current_time = time.time() - start_time
            roll_data.append(msg.roll * 57.3)  # Convert rad to deg
            pitch_data.append(msg.pitch * 57.3)
            yaw_data.append(msg.yaw * 57.3)
            time_data.append(current_time)

            # Trim list to last 50 data points
            if len(time_data) > 50:
                roll_data.pop(0)
                pitch_data.pop(0)
                yaw_data.pop(0)
                time_data.pop(0)

            # Clear and redraw the plot
            plot.clear()
            plot.plot(time_data, roll_data, label="Roll")
            plot.plot(time_data, pitch_data, label="Pitch")
            plot.plot(time_data, yaw_data, label="Yaw")
            plot.set_title("Real-Time Roll, Pitch, Yaw")
            plot.set_xlabel("Time (s)")
            plot.set_ylabel("Degrees")
            plot.legend()

# Start thread to read Pixhawk data continuously
threading.Thread(target=read_attitude, daemon=True).start()
# Start graph updates
root.after(1000, update_graph)

# ---------------- Data Logging Tab ----------------
log_tab = ttk.Frame(notebook)  # Create tab for logging
notebook.add(log_tab, text="Data Logging")  # Add to notebook

# Text entry for user label or note
entry_note = tk.Entry(log_tab)
entry_note.pack(pady=10)
entry_note.insert(0, "Enter Note or Label")

# Label to show log status
log_label = tk.Label(log_tab, text="Data will be logged to log.csv")
log_label.pack()

# Function to log most recent roll, pitch, yaw with timestamp and user note
def log_data():
    with open("log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.datetime.now(),  # Timestamp
            entry_note.get(),         # User note
            roll_data[-1] if roll_data else "",  # Last roll
            pitch_data[-1] if pitch_data else "",  # Last pitch
            yaw_data[-1] if yaw_data else ""  # Last yaw
        ])
    log_label.config(text="Logged Successfully")  # Confirm logging

# Button to trigger log_data
log_btn = tk.Button(log_tab, text="Log Last Orientation", command=log_data)
log_btn.pack(pady=10)

# ---------------- Run GUI ----------------
root.mainloop()  # Launch the Tkinter GUI

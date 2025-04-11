# GUI for 3DOF Hover Drone
# Attributes:
# control DC motors
# log/graph roll/pitch/yaw angles captured by pixhawk in real-time
# allows to upload logged data from Pixhawk to graph captured angles



###################### IMPORT LIBRARIES ######################
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymavlink import mavutil
import threading
import time
import csv
import datetime

###################### CONNECT TO MAVLink ######################
#master = mavutil.mavlink_connection('/dev/ttyACM0')
#master.wait_heartbeat()
#print("Pixhawk Connected")

###################### CREATE GUI FRAME ######################
root = tk.Tk()
root.title("3 DOF Hover GUI")
root.geometry("500x400")

# Create Tabs (Notebooks) for Real-Time Monitoring and Upload Data
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

tab1 = ttk.Frame(notebook) #creates tab1 frame
tab2 = ttk.Frame(notebook)

notebook.add(tab1, text="Real-Time Monitor") #label tab
notebook.add(tab2, text="Upload Pixhawk Flight Data") 

root.mainloop()

###################### 









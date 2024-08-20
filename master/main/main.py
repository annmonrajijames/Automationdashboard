import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import shutil
import sys

def open_folder():
    global folder_path
    folder_path = filedialog.askdirectory()
    if folder_path:
        path_label.config(text=folder_path)
        run_button.config(state='normal')  # Enable the run button

def copy_folder():
    destination_path = filedialog.askdirectory(title="Select Destination for Copy")
    if destination_path:
        destination_folder = os.path.join(destination_path, os.path.basename(folder_path))
        shutil.copytree(folder_path, destination_folder)
        save_output_label.config(text=destination_folder)
        return destination_folder
    else:
        return folder_path

def run_script():
    # Determine the base path: Use _MEIPASS for bundled app, and __file__ for development
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    
    if copy_var.get():
        new_path = destination_folder if 'destination_folder' in globals() else folder_path
    else:
        new_path = folder_path

    script = file_var.get()
    # Adjust the script path to consider the base path
    script_path = os.path.join(base_path, script)

    if script and new_path:
        # Run the script from the correct path
        subprocess.run(['python', script_path, new_path], check=True)

def handle_copy_check():
    if copy_var.get():
        global destination_folder
        destination_folder = copy_folder()  # Trigger folder selection upon checking

app = tk.Tk()
app.title("LECTRIX-Complete Analysis 2.0")
app.configure(bg="lightblue")  # Set the background color

# Global variable to store the folder path
folder_path = ""

# Label for the dropdown menu
label = tk.Label(app, text="Choose the Analysis", bg="lightblue", fg="black")
label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

# Dropdown for selecting the Python script
file_var = tk.StringVar(app)
file_var.set("Select a script")
scripts = {
    "Daily analysis LX70": "Bytebeam_LX70.py",
    "Daily analysis Enduro": "Bytebeam_NDuro.py",
    "Daily analysis LXS": "Bytebeam_LXS.py",
    "Daily analysis Influx LX70" : "Influx_LX70.py",
    "Daily analysis Influx Enduro" : "Influx_NDuro.py",
    "Daily analysis Influx LXS" : "Influx_LXS.py",
}
dropdown = tk.OptionMenu(app, file_var, *scripts.values())
dropdown.config(bg="lightblue", fg="black", width=20)
dropdown.grid(row=0, column=1, padx=10, pady=10, sticky='w')  # Align to the left (west)

# Set the default value to the first script
file_var.set(next(iter(scripts.values())))

# Label for displaying the folder path
path_label = tk.Label(app, text="Click Choose Folder- Input Folder's path will be shown here", bg="lightblue", fg="black", wraplength=100)
path_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

# Button to choose the folder
folder_button = tk.Button(app, text="Choose Folder", command=open_folder, bg="lightblue", fg="black")
folder_button.grid(row=1, column=1, padx=10, pady=10, sticky='nw')  # Align to the left (west)

# Label for the "Save output in preferred location" checkbox
save_output_label = tk.Label(app, text="Output folder path will be shown here", bg="lightblue", fg="black", wraplength=100)
save_output_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')

# Checkbox for copying the folder
copy_var = tk.BooleanVar()
copy_check = tk.Checkbutton(app, text="Save output in preferred location", variable=copy_var, bg="lightblue", fg="black", command=handle_copy_check)
copy_check.grid(row=2, column=1, padx=10, pady=5, sticky='w')  # Align to the left (west)

# Button to run the script (initially disabled)
run_button = tk.Button(app, text="Run", command=run_script, bg="lightblue", fg="black", state='disabled')
run_button.grid(row=3, columnspan=2, padx=10, pady=20)

app.mainloop()

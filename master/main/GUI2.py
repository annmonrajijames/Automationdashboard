import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import shutil

def open_folder():
    global folder_path
    folder_path = filedialog.askdirectory()
    if folder_path:
        path_label.config(text=folder_path)

def copy_folder(original_path):
    destination_path = filedialog.askdirectory(title="Select Destination for Copy")
    if destination_path:
        destination_folder = os.path.join(destination_path, os.path.basename(original_path))
        shutil.copytree(original_path, destination_folder)
        save_output_label.config(text=destination_folder)
        return destination_folder
    else:
        return original_path

def run_script():
    if copy_var.get():
        # If the user wants to copy the folder
        new_path = copy_folder(folder_path)
    else:
        new_path = folder_path
    
    script = file_var.get()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, script)
    if script and new_path:
        subprocess.run(['python', script_path, new_path], check=True)

app = tk.Tk()
app.title("Run Python Scripts")

# Global variable to store the folder path
folder_path = ""

# Label for the dropdown menu
label = tk.Label(app, text="Choose the Analysis")
label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

# Dropdown for selecting the Python script
file_var = tk.StringVar(app)
file_var.set("Select a script")
scripts = {
    "Test Script": "test.py",
    "Battery Analysis": "Battery_Analysis.py",
    "Error Causes": "Error_causes.py"
}
dropdown = tk.OptionMenu(app, file_var, *scripts.values())
dropdown.grid(row=0, column=1, padx=10, pady=10)

# Label for displaying the folder path
path_label = tk.Label(app, text="Choose to see input folder path")
path_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

# Button to choose the folder
folder_button = tk.Button(app, text="Choose Folder", command=open_folder)
folder_button.grid(row=1, column=1, padx=10, pady=10)

# Label for the "Save output in preferred location" checkbox
save_output_label = tk.Label(app, text="Run to see the output folder path")
save_output_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')

# Checkbox for copying the folder
copy_var = tk.BooleanVar()
copy_check = tk.Checkbutton(app, text="Save output in preferred location", variable=copy_var)
copy_check.grid(row=2, column=1, padx=10, pady=5)

# Button to run the script
run_button = tk.Button(app, text="Run", command=run_script)
run_button.grid(row=3, columnspan=2, padx=10, pady=20)

app.mainloop()

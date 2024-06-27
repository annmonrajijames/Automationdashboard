import tkinter as tk
from tkinter import filedialog
import subprocess
import os

def open_folder():
    global folder_path
    folder_path = filedialog.askdirectory()

def run_script():
    script = file_var.get()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, script)
    if script and folder_path:
        subprocess.run(['python', script_path, folder_path], check=True)

app = tk.Tk()
app.title("Run Python Scripts")

# Global variable to store the folder path
folder_path = ""

# Dropdown for selecting the Python script
file_var = tk.StringVar(app)
file_var.set("Select a script")
scripts = {
    "Test Script": "test.py",
    "Battery Analysis": "Battery_Analysis.py",
    "Error Causes": "Error_causes.py"
}
dropdown = tk.OptionMenu(app, file_var, *scripts.values())
dropdown.pack(pady=10)

# Button to choose the folder
folder_button = tk.Button(app, text="Choose Folder", command=open_folder)
folder_button.pack(pady=10)

# Button to run the script
run_button = tk.Button(app, text="Run", command=run_script)
run_button.pack(pady=20)

app.mainloop()

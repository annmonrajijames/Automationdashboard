import tkinter as tk
from tkinter.filedialog import askdirectory
import subprocess

def choose_folder():
    """ Opens a dialog to choose a folder and prints the selected path. """
    folder_path = askdirectory()
    if folder_path:
        print("Folder selected:", folder_path)
        return folder_path

def run_script(script_name):
    """ Runs a Python script based on the selected analysis type. """
    if script_name == "Date based - ANALYSIS":
        subprocess.run(["python", "CodeForAutomation24AndPowerParameters_excel.py"])
    elif script_name == "Battery based - ANALYSIS":
        subprocess.run(["python", "battery_analysis.py"])
    elif script_name == "Error Reasoning":
        subprocess.run(["python", "CellUnderVoltageWarning.py"])
    else:
        print("Invalid selection.")

def on_select(value):
    """ Handles selection changes in the dropdown. """
    print("Selected:", value)
    run_script(value)

root = tk.Tk()
root.title("Run Python file based on dropdown menu selection")
root.configure(bg="#7b7b7f")

# Frame for padding and organizing widgets
padded_frame = tk.Frame(root, padx=20, pady=15, borderwidth=2, bg="lightblue")
padded_frame.pack(fill="both", expand=True)

# Widgets for folder selection
tk.Label(padded_frame, text='Select the folder:', bg="lightblue").grid(row=0, column=0, pady=10)
tk.Button(padded_frame, text="Choose Folder", command=choose_folder).grid(row=0, column=1, pady=10)

# Dropdown menu for selecting analysis type
dropOptions = ["Date based - ANALYSIS", "Battery based - ANALYSIS", "Error Reasoning"]
selected_option = tk.StringVar(root)
selected_option.set(dropOptions[0])  # Default option
tk.Label(padded_frame, text='Select the analysis to be performed:', bg="lightblue").grid(row=1, column=0)
dropdown = tk.OptionMenu(padded_frame, selected_option, *dropOptions, command=on_select)
dropdown.grid(row=1, column=1)

root.mainloop()

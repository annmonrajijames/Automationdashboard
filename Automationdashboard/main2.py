import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import subprocess

def choose_folder():
    folder_path = askdirectory()
    if folder_path:
        print("Folder selected:", folder_path)
        return folder_path

def run_script(script_name):
    try:
        if script_name == "Date based - ANALYSIS":
            subprocess.run(["python", "date_analysis.py"], check=True)
        elif script_name == "Battery based - ANALYSIS":
            subprocess.run(["python", "battery_analysis.py"], check=True)
        elif script_name == "Error Reasoning":
            subprocess.run(["python", "CellUnderVoltageWarning.py"], check=True)
        messagebox.showinfo("Success", "Script executed successfully!")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Script execution failed!")

def on_select(value):
    print("Selected:", value)
    run_script(value)

root = tk.Tk()
root.title("Run Python file based on dropdown menu selection")
root.configure(bg="#7b7b7f")

padded_frame = tk.Frame(root, padx=20, pady=15, borderwidth=2, bg="lightblue")
padded_frame.pack(fill="both", expand=True)

tk.Label(padded_frame, text='Select the folder:', bg="lightblue").grid(row=0, column=0, pady=10)
tk.Button(padded_frame, text="Choose Folder", command=choose_folder).grid(row=0, column=1, pady=10)

dropOptions = ["Date based - ANALYSIS", "Battery based - ANALYSIS", "Error Reasoning"]
selected_option = tk.StringVar(root)
selected_option.set(dropOptions[0])
tk.Label(padded_frame, text='Select the analysis to be performed:', bg="lightblue").grid(row=1, column=0)
dropdown = tk.OptionMenu(padded_frame, selected_option, *dropOptions, command=on_select)
dropdown.grid(row=1, column=1)

root.mainloop()
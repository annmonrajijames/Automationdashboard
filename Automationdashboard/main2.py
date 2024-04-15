import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import subprocess

def choose_folder():
    """ Opens a dialog to choose a folder and stores the selected path. """
    folder_path = askdirectory()
    if folder_path:
        print("Folder selected:", folder_path)
        app_data['folder_path'] = folder_path  # Store the folder path in the dictionary.
        update_run_button_state()  # Update the state of the Run button.

def run_script():
    """ Runs a Python script based on the selected analysis type. """
    script_name = app_data.get('selected_option')
    folder_path = app_data.get('6')
    if script_name and folder_path:
        try:
            if script_name == "Date based - ANALYSIS":
                subprocess.run(["python", "CodeForAutomation24AndPowerParameters_excel.py"], check=True)
            elif script_name == "Battery based - ANALYSIS":
                subprocess.run(["python", "battery_analysis.py"], check=True)
            elif script_name == "Error Reasoning":
                subprocess.run(["python", "CellUnderVoltageWarning.py"], check=True)
            messagebox.showinfo("Success", "Script executed successfully!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Script execution failed!")
    else:
        messagebox.showerror("Error", "Folder or analysis type is not selected.")

def on_select(value):
    """ Stores the selected option and updates button state. """
    print("Selected:", value)
    app_data['selected_option'] = value
    update_run_button_state()

def update_run_button_state():
    """ Enables the Run button only if both a folder and an analysis option have been selected. """
    if app_data.get('folder_path') and app_data.get('selected_option'):
        run_button.config(state=tk.NORMAL)
    else:
        run_button.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Run Python file based on dropdown menu selection")
root.configure(bg="#7b7b7f")

app_data = {'folder_path': None, 'selected_option': None}  # Dictionary to hold application data.

padded_frame = tk.Frame(root, padx=20, pady=15, borderwidth=2, bg="lightblue")
padded_frame.pack(fill="both", expand=True)

tk.Label(padded_frame, text='Select the folder:', bg="lightblue").grid(row=0, column=0, pady=10)
tk.Button(padded_frame, text="Choose Folder", command=choose_folder).grid(row=0, column=1, pady=10)

dropOptions = ["Date based - ANALYSIS", "Battery based - ANALYSIS", "Error Reasoning"]
selected_option = tk.StringVar(root)
selected_option.set(dropOptions[0])  # Default option is set but button is still disabled.
tk.Label(padded_frame, text='Select the analysis to be performed:', bg="lightblue").grid(row=1, column=0)
dropdown = tk.OptionMenu(padded_frame, selected_option, *dropOptions, command=on_select)
dropdown.grid(row=1, column=1)

# Run button (initially disabled)
run_button = tk.Button(padded_frame, text="Run", command=run_script, state=tk.DISABLED)
run_button.grid(row=2, column=0, columnspan=2, pady=20)

root.mainloop()

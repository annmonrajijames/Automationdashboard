import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess

def run_selected_script():
    script_name = combo_box.get()
    if script_name:
        try:
            # Using subprocess to run the python file more safely
            completed_process = subprocess.run(['python', script_name], check=True, text=True, capture_output=True)
            messagebox.showinfo("Success", f"Script {script_name} executed successfully!\n\nOutput:\n{completed_process.stdout}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Script {script_name} execution failed!\n\nError:\n{e.stderr}")
    else:
        messagebox.showwarning("Warning", "Please select a script to run.")

# Create the main window
root = tk.Tk()
root.title("Script Runner")

# List of scripts
scripts = ['CellUnderVoltageWarning.py', 'CodeForAutomation24AndPowerParameters_excel.py']

# Create a label
label = ttk.Label(root, text="Select a script to run:")
label.pack(pady=10)

# Create a combobox to select the script
combo_box = ttk.Combobox(root, values=scripts)
combo_box.pack(pady=10)

# Create a button that will run the selected script when clicked
run_button = ttk.Button(root, text="Run Script", command=run_selected_script)
run_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()

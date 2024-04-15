import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import shutil
import os

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

def upload_and_save_file():
    # Open the file dialog to choose the file
    filepath = filedialog.askopenfilename()
    if filepath:
        # Define the destination directory
        destination_dir = r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard'
        # Ensure the directory exists
        os.makedirs(destination_dir, exist_ok=True)
        # Define the full destination path
        destination_path = os.path.join(destination_dir, os.path.basename(filepath))
        # Copy the file to the destination
        shutil.copy(filepath, destination_path)
        messagebox.showinfo("Success", f"File uploaded and saved successfully to {destination_path}")

# Create the main window
root = tk.Tk()
root.title("Script and File Runner")

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

# Create a button to upload and save a file
upload_button = ttk.Button(root, text="Upload and Save File", command=upload_and_save_file)
upload_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()

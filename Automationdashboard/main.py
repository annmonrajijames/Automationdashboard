import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import shutil
import os

def on_script_select(event):
    # Enable the upload button only if a script is selected
    if combo_box.get() != "Choose your task":
        upload_button['state'] = 'normal'
    else:
        upload_button['state'] = 'disabled'
        run_button['state'] = 'disabled'

def run_selected_script():
    script_name = combo_box.get()
    if script_name and script_name != "Choose your task":
        try:
            completed_process = subprocess.run(['python', script_name], check=True, text=True, capture_output=True)
            messagebox.showinfo("Success", f"Script {script_name} executed successfully!\n\nOutput:\n{completed_process.stdout}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Script {script_name} execution failed!\n\nError:\n{e.stderr}")

def upload_and_save_files():
    filepaths = filedialog.askopenfilenames()
    if filepaths:
        destination_dir = r'C:\DestinationDirectory'
        os.makedirs(destination_dir, exist_ok=True)
        for filepath in filepaths:
            shutil.copy(filepath, os.path.join(destination_dir, os.path.basename(filepath)))
        messagebox.showinfo("Success", f"Files uploaded successfully to {destination_dir}")
        run_button['state'] = 'normal'

# Set up the main application window
root = tk.Tk()
root.title("Script and File Runner")
root.configure(bg='lightblue')

# Create a main frame for padding and background
main_frame = tk.Frame(root, padx=20, pady=15, borderwidth=2, bg="lightblue")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Script selection components
tk.Label(main_frame, text="Select the analysis to be performed :-", bg="lightblue").grid(row=0, column=0, sticky="w", pady=10)
scripts = ['CellUnderVoltageWarning.py', 'CodeForAutomation24AndPowerParameters_excel.py']
combo_box = ttk.Combobox(main_frame, values=["Choose your task"] + scripts, state="readonly")
combo_box.set('Choose your task')  # Set placeholder text
combo_box.grid(row=0, column=1, pady=10)
combo_box.bind("<<ComboboxSelected>>", on_script_select)

# File upload components
tk.Label(main_frame, text="Select files :-", bg="lightblue").grid(row=1, column=0, sticky="e", pady=10)
upload_button = ttk.Button(main_frame, text="Choose Files", command=upload_and_save_files, state='disabled')
upload_button.grid(row=1, column=1, pady=10)

# Run script button placed at the bottom
run_button = ttk.Button(main_frame, text="Output", command=run_selected_script, state='disabled')
run_button.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()
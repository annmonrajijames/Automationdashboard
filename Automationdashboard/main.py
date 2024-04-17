import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import subprocess
import shutil
import os
from tkinter import messagebox, filedialog

def choose_folder():
    """ Opens a dialog to choose a folder and stores the selected path. """
    source_folder = askdirectory()
    if source_folder:
        print("Folder selected:", source_folder)
        app_data['folder_path'] = source_folder  # Store the folder path in the dictionary.
        update_run_button_state()  # Update the state of the Run button.

        destination_folder = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard"
        copy_files_to_directory(source_folder, destination_folder)

def copy_files_to_directory(source_folder, destination_folder):
    """ Copies all files and folders from the source folder to the destination folder, overwriting existing files. """
    try:
        os.makedirs(destination_folder, exist_ok=True)
        for item in os.listdir(source_folder):
            src_path = os.path.join(source_folder, item)
            dst_path = os.path.join(destination_folder, item)
            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            elif os.path.isfile(src_path):
                shutil.copy(src_path, dst_path)
        messagebox.showinfo("Success", "Output files have been saved to the selected location successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save output files: {e}")

def on_select(value):
    """ Handles selection changes in the dropdown. """
    print("Selected:", value)
    app_data['selected_option'] = value
    update_run_button_state()

def save_output(output_directory):
    """ Asks the user to select a new location to save the output files, then copies them there. """
    destination = filedialog.askdirectory(title="Select Destination for Output Files")
    if destination:
        copy_files_to_directory(output_directory, destination)
def run_script():
    """ Runs the selected Python script based on dropdown selection and handles file output location. """
    script_name = app_data.get('selected_option')
    folder_path = app_data.get('folder_path')
    if script_name and folder_path:
        try:
            if script_name == "Date based - ANALYSIS":
                output_directory = "C:/Lectrix_company/work/Git_Projects/Automationdashboard/Automationdashboard/OUTPUT_1"
                subprocess.run(["python", "merge_csv_forAutomation_1.py"], check=True)
                save_output(output_directory)
            elif script_name == "Battery based - ANALYSIS":
                output_directory = "C:/Lectrix_company/work/Git_Projects/Automationdashboard/Automationdashboard/OUTPUT_2"
                subprocess.run(["python", "merge_csv_forAutomation_2.py"], check=True)
                save_output(output_directory)
            elif script_name == "Error Reasoning":
                output_directory = "C:/Lectrix_company/work/Git_Projects/Automationdashboard/Automationdashboard/OUTPUT_3"
                subprocess.run(["python", "merge_csv_forAutomation_3.py"], check=True)
                save_output(output_directory)
            messagebox.showinfo("Success", "Script executed successfully!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Script execution failed!")
    else:
        messagebox.showerror("Error", "Folder or analysis type is not selected.")

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
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import subprocess
import shutil
import os
from tkinter import messagebox, filedialog

def choose_folder():
    """ Opens a dialog to choose a folder and stores the selected path. """
    cleanup_directories()
    source_folder = filedialog.askdirectory()
    if source_folder:
        print("Folder selected:", source_folder)
        app_data['folder_path'] = source_folder  # Store the folder path in the dictionary.
        folder_label_text.set(source_folder)  # Update label with chosen folder path
        update_run_button_state()  # Update the state of the Run button.
        new_folder_entry.config(state=tk.NORMAL)
        # Determine destination folder based on the selected analysis type
        if app_data['selected_option'] == "Daily_Analysis":
            destination_folder = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\INPUT_1"
        elif app_data['selected_option'] == "Battery based - ANALYSIS":
            destination_folder = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\INPUT_2"
        elif app_data['selected_option'] == "Error Reasoning":
            destination_folder = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\INPUT_3"
        else:
            messagebox.showerror("Error", "No valid analysis type selected for file operations.")
            return

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
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload Folder/Files: {e}")

def on_select(value):
    """ Handles selection changes in the dropdown. """
    print("Selected:", value)
    app_data['selected_option'] = value
    choose_folder_button.config(state=tk.NORMAL)  # Enable the Choose Folder button
    update_run_button_state()

def update_run_button_state():
    """ Enables the Run button only if both a folder and an analysis option have been selected. """
    if app_data.get('folder_path') and app_data.get('selected_option'):
        run_button.config(state=tk.NORMAL)
    else:
        run_button.config(state=tk.DISABLED)
def save_output(output_directory):
    """ Asks the user to select a new location to save the output files, then copies them there. """
    destination = filedialog.askdirectory(title="Select Destination for Output Files")
    if destination and new_folder_name.get().strip():  # Ensure there's a name
        final_destination = os.path.join(destination, new_folder_name.get().strip())
        os.makedirs(final_destination, exist_ok=True)
        copy_files_to_directory(output_directory, final_destination)
        messagebox.showinfo("Success", "Output files/folders saved successfully!")
        cleanup_directories()
        reset_gui()
    else:
        messagebox.showerror("Error", "You must enter a folder name.")
def run_script():
    """ Runs the selected Python script based on dropdown selection and handles file output location. """
    script_name = app_data.get('selected_option')
    folder_path = app_data.get('folder_path')
    if script_name and folder_path:
        try:
            if script_name == "Daily_Analysis":
                output_directory = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\OUTPUT_1"
                subprocess.run(["python", "Daily_Analysis.py"], check=True)
                save_output(output_directory)
            elif script_name == "Battery based - ANALYSIS":
                output_directory = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\OUTPUT_2"
                subprocess.run(["python", "merge_csv_forAutomation_2.py"], check=True)
                save_output(output_directory)
            elif script_name == "Error Reasoning":
                output_directory = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\OUTPUT_3"
                subprocess.run(["python", "Error_causes.py"], check=True)
                save_output(output_directory)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Script execution failed!")
            reset_gui()
    else:
        messagebox.showerror("Error", "Folder or analysis type is not selected.")
        reset_gui()
def update_run_button_state():
    """ Enables the Run button only if both a folder and an analysis option have been selected. """
    if app_data.get('folder_path') and app_data.get('selected_option'):
        run_button.config(state=tk.NORMAL)
    else:
        run_button.config(state=tk.DISABLED)
def reset_gui():
    """ Resets the GUI to its initial state. """
    folder_label_text.set("----------->")  # Reset the folder label
    selected_option.set(dropOptions[0])  # Reset the dropdown to the first option
    app_data['folder_path'] = None
    app_data['selected_option'] = None
    new_folder_name.set("")  # Clear the new folder name entry box
    new_folder_entry.config(state=tk.DISABLED)  # Disable the entry box again
    choose_folder_button.config(state=tk.DISABLED)  # Re-enable the Choose Folder button
    run_button.config(state=tk.DISABLED)  # Ensure the Run button is disabled
    update_run_button_state()  # Optionally update states of other controls if needed

def clear_directory_contents(directory):
    """ Clears all files and folders in the specified directory. """
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

def cleanup_directories():
    """ Clears all files and folders in specified directories after operations are completed. """
    directories = [
        r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\INPUT_1",
        r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\INPUT_2",
        r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\INPUT_3",
        r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\OUTPUT_1",
        r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\OUTPUT_2",
        r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\OUTPUT_3"
    ]
    for directory in directories:
        clear_directory_contents(directory)
    #messagebox.showinfo("Cleanup", "All directories have been cleared!")
root = tk.Tk()
root.title("Run Python file based on dropdown menu selection")
root.configure(bg="#7b7b7f")

app_data = {'folder_path': None, 'selected_option': None}  # Dictionary to hold application data.

padded_frame = tk.Frame(root, padx=20, pady=15, borderwidth=2, bg="lightblue")
padded_frame.pack(fill="both", expand=True)

folder_label_text = tk.StringVar(root)
folder_label_text.set("----------->")  # Initial placeholder text
folder_label = tk.Label(padded_frame, textvariable=folder_label_text, bg="lightblue")
folder_label.grid(row=0, column=0, pady=10)

# Choose Folder button initially disabled
choose_folder_button = tk.Button(padded_frame, text="Choose Folder", command=choose_folder, state=tk.DISABLED, width=20)
choose_folder_button.grid(row=0, column=1, pady=10)

dropOptions = ["Daily_Analysis", "Battery based - ANALYSIS", "Error Reasoning"]
selected_option = tk.StringVar(root)
selected_option.set(dropOptions[0])  # Default option is set but button is still disabled.
tk.Label(padded_frame, text='Choose the analysis:', bg="lightblue").grid(row=1, column=0)
dropdown = tk.OptionMenu(padded_frame, selected_option, *dropOptions, command=on_select)
dropdown.config(width=20)  # Set the width of the dropdown to prevent resizing
dropdown.grid(row=1, column=1, columnspan=2)

# Entry for new folder name, initially disabled
new_folder_name = tk.StringVar(root)
new_folder_entry = tk.Entry(padded_frame, textvariable=new_folder_name, state=tk.DISABLED, width=27)
new_folder_entry.grid(row=2, column=1, columnspan=2, pady=10)
tk.Label(padded_frame, text='Type the Output folder name:', bg="lightblue").grid(row=2, column=0, pady=10)

# Run button (initially disabled)
run_button = tk.Button(padded_frame, text="Run and Save file", command=run_script, state=tk.DISABLED, width=20)
run_button.grid(row=3, column=0, columnspan=2, pady=20)

root.mainloop()
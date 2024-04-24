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
        wrapped_path = wrap_text(source_folder, 20)
        folder_label_text.set(wrapped_path)  # Update label with chosen folder path
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
def wrap_text(text, length):
    return '\n'.join(text[i:i+length] for i in range(0, len(text), length))
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
# def save_output(output_directory):
#     """ Asks the user to provide a new folder name in the entry box, then copies the files there. """
#     destination = filedialog.askdirectory(title="Select Destination for Output Files")
#     if destination:
#         # Get the folder name from the entry box or use a default name if it's empty
#         folder_name = new_folder_name.get().strip() if new_folder_name.get().strip() else "Lectrix_Analysis"
#         final_destination = os.path.join(destination, folder_name)
#         os.makedirs(final_destination, exist_ok=True)  # Create the new directory
#         copy_files_to_directory(output_directory, final_destination)
#         # cleanup_directories()  # Perform cleanup after saving output
#         reset_gui()  # Reset the GUI to initial state
#     else:
#         messagebox.showerror("Error", "You must select a destination directory.")
def run_script():
    """ Runs the selected Python script based on dropdown selection and handles file output location. """
    script_name = app_data.get('selected_option')
    folder_path = app_data.get('folder_path')
    if script_name and folder_path:
        try:
            if script_name == "Daily_Analysis":
                output_directory = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\OUTPUT_1"
                subprocess.run(["python", "Daily_Analysis.py"], check=True)
                reset_gui()
                #save_output(output_directory)
            elif script_name == "Battery based - ANALYSIS":
                output_directory = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\OUTPUT_2"
                subprocess.run(["python", "merge_csv_forAutomation_2.py"], check=True)
                #save_output(output_directory)
                reset_gui()
            elif script_name == "Error Reasoning":
                output_directory = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\OUTPUT_3"
                subprocess.run(["python", "Error_causes.py"], check=True)
                #save_output(output_directory)
                reset_gui()
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
    folder_label_text.set("Path of selected folder")  # Reset the folder label
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
#     #messagebox.showinfo("Cleanup", "All directories have been cleared!")
root = tk.Tk()
root.title("Run Python file based on dropdown menu selection")
root.configure(bg="lightblue")
root.geometry("400x200")
root.resizable(False, False)  # Disable resizing of the window
app_data = {'folder_path': None, 'selected_option': None}  # Dictionary to hold application data.
 
folder_label_text = tk.StringVar(root)
folder_label_text.set("Path of selected folder")  # Initial placeholder text
folder_label = tk.Label(root, textvariable=folder_label_text, bg="lightblue", justify=tk.LEFT)
folder_label.grid(row=1, column=0, pady=10, padx=20, sticky='w',columnspan=2)
 
# Determine a suitable width for all input-related widgets
uniform_width = 25  # This width value should be sufficient to match the widest element
 
choose_folder_button = tk.Button(root, text="Choose Folder", command=choose_folder, state=tk.DISABLED, width=uniform_width+1)
choose_folder_button.grid(row=1, column=1, pady=10, padx=20)
 
dropOptions = ["Daily_Analysis", "Battery based - ANALYSIS", "Error Reasoning"]
 
selected_option = tk.StringVar(root)
selected_option.set(dropOptions[0])  # Default option is set but button is still disabled.
tk.Label(root, text='Choose the analysis:', bg="lightblue").grid(row=0, column=0, padx=20, sticky='w')
dropdown = tk.OptionMenu(root, selected_option, *dropOptions, command=on_select)
dropdown.config(width=uniform_width)  # Setting the width here to match other elements
dropdown.grid(row=0, column=1, pady=10, padx=20)
 
new_folder_name = tk.StringVar(root)
new_folder_entry = tk.Entry(root, textvariable=new_folder_name, state=tk.DISABLED, width=uniform_width+6)
#new_folder_entry.grid(row=2, column=1, padx=20)
#tk.Label(root, text='Type the Output folder name:', bg="lightblue").grid(row=2, column=0, pady=10, padx=20, sticky='w')
 
run_button = tk.Button(root, text="Run", command=run_script, state=tk.DISABLED, width=uniform_width)
run_button.grid(row=3, column=0, columnspan=2, pady=20, padx=20)
 
root.mainloop()
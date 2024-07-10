import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import os
import shutil
import pandas as pd
import warnings
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplcursors
import threading

def open_folder():
    global folder_path
    folder_path = filedialog.askdirectory()
    if folder_path:
        path_label.config(text=folder_path)
        run_button.config(state='normal')  # Enable the run button

def copy_folder(original_path):
    destination_path = filedialog.askdirectory(title="Select Destination for Copy")
    if destination_path:
        destination_folder = os.path.join(destination_path, os.path.basename(original_path))
        shutil.copytree(original_path, destination_folder)
        save_output_label.config(text=destination_folder)
        return destination_folder
    else:
        return original_path

def run_script():
    if copy_var.get():
        # If the user wants to copy the folder
        new_path = copy_folder(folder_path)
    else:
        new_path = folder_path
    
    script_name = file_var.get()
    script_path = scripts[script_name]  # Get the correct script path from the dropdown
    if script_name and new_path:
        subprocess.run(['python', script_path, new_path], check=True)
        # Run crop_data in a separate thread
        threading.Thread(target=crop_data, args=(new_path,)).start()

def crop_data(main_folder_path):
    def plot_ghps(data, folder_name):
        if 'localtime' not in data.columns:
            # Convert the 'timestamp' column from Unix milliseconds to datetime
            data['localtime'] = pd.to_datetime(data['timestamp'], unit='ms')
            # Adjusting the timestamp to IST (Indian Standard Time) by adding 5 hours and 30 minutes
            data['localtime'] = data['localtime'] + pd.Timedelta(hours=5, minutes=30)

        # Convert 'localtime' column to datetime
        data['localtime'] = pd.to_datetime(data['localtime'], format='%Y-%m-%d %H:%M:%S.%f')
        data.set_index('localtime', inplace=True)

        # Create a figure and axes for plotting
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot 'PackCurr_6' on primary y-axis
        line1, = ax1.plot(data.index, -data['PackCurr_6'], color='blue', label='PackCurr_6')
        ax1.set_ylabel('Pack Current (A)', color='blue')
        ax1.yaxis.set_label_coords(-0.1, 0.7)  # Adjust label position

        # Create secondary y-axis for 'MotorSpeed_340920578' (RPM)
        ax2 = ax1.twinx()
        line2, = ax2.plot(data.index, data['MotorSpeed_340920578'], color='green', label='Motor Speed')
        ax2.set_ylabel('Motor Speed (RPM)', color='green')

        # Add 'AC_Current_340920579' to primary y-axis
        line3, = ax1.plot(data.index, data['AC_Current_340920579'], color='lightgray', label='AC Current')

        # Add 'AC_Voltage_340920580' scaled to 10x to the left side y-axis
        line4, = ax1.plot(data.index, data['AC_Voltage_340920580'] * 10, color='lightgray', label='AC Voltage (x10)')

        # Add 'Throttle_408094978' to the left side y-axis
        line5, = ax1.plot(data.index, data['Throttle_408094978'], color='lightgray', label='Throttle (%)')

        # Add 'Throttle_408094978' to the left side y-axis
        line6, = ax1.plot(data.index, data['SOC_8'], color='red', label='SOC (%)')

        # Hide the y-axis label for 'AC_Current_340920579'
        ax1.get_yaxis().get_label().set_visible(False)

        # Set x-axis label and legend
        ax1.set_xlabel('Local Time')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        # Add a title to the plot
        plt.title('Battery Pack, Motor Data, and Throttle')

        # Format x-axis ticks as hours:minutes:seconds
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # Set grid lines lighter
        ax1.grid(True, linestyle=':', linewidth=0.5, color='gray')
        ax2.grid(True, linestyle=':', linewidth=0.5, color='gray')

        # Enable cursor to display values on graphs
        mplcursors.cursor([line1, line2, line3, line4, line5, line6])

        # Save the plot as an image or display it
        plt.tight_layout()  # Adjust layout to prevent clipping of labels
        subfolder_path = os.path.join(main_folder_path, folder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        plt.savefig(os.path.join(subfolder_path, 'graph.png'))  # Save the plot as an image in the specified directory
        plt.show()

    def remove_anomalies(data, subfolder, deeper_subfolder_path):
        continue_removing = True
        while continue_removing:
            crop = tk.messagebox.askquestion("Remove Anomalies", "Do you want to remove anomalies?")
            if crop == 'yes':
                start_time_input = tk.simpledialog.askstring("Start Time", "Enter start time of anomaly (format: 2024-04-02 12:59:00.000):")
                end_time_input = tk.simpledialog.askstring("End Time", "Enter end time of anomaly (format: 2024-04-02 12:59:00.000):")

                if start_time_input and end_time_input:
                    start_time = pd.to_datetime(start_time_input, format='%Y-%m-%d %H:%M:%S.%f')
                    end_time = pd.to_datetime(end_time_input, format='%Y-%m-%d %H:%M:%S.%f')

                    data = data[(data['localtime'] < start_time) | (data['localtime'] > end_time)]
                    plot_ghps(data, subfolder)
            else:
                continue_removing = False
                output_file_path = os.path.join(deeper_subfolder_path, 'log_withoutanomaly.csv')
                data.to_csv(output_file_path, index=False)

    for subfolder in os.listdir(main_folder_path):
        subfolder_path = os.path.join(main_folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            for deeper_subfolder in os.listdir(subfolder_path):
                deeper_subfolder_path = os.path.join(subfolder_path, deeper_subfolder)
                if os.path.isdir(deeper_subfolder_path):
                    log_withoutanomaly_path = os.path.join(deeper_subfolder_path, 'log_withoutanomaly.csv')
                    log_file_path = os.path.join(deeper_subfolder_path, 'log_km.csv')
                    if not os.path.exists(log_withoutanomaly_path) and os.path.exists(log_file_path):
                        data = pd.read_csv(log_file_path)
                        data['localtime'] = pd.to_datetime(data['timestamp'], unit='ms') + pd.Timedelta(hours=5, minutes=30)
                        plot_ghps(data, subfolder)
                        app.after(0, remove_anomalies, data, subfolder, deeper_subfolder_path)
                    else:
                        if os.path.exists(log_withoutanomaly_path):
                            print("Log without anomaly already exists for folder:", deeper_subfolder)
                        print("No log file found in folder:", deeper_subfolder)

app = tk.Tk()
app.title("Run Python Scripts")
app.configure(bg="lightblue")  # Set the background color

folder_path = ""

label = tk.Label(app, text="Choose the Analysis", bg="lightblue", fg="black")
label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

file_var = tk.StringVar(app)
file_var.set("Select a script")
scripts = {
    "Test Script": "test.py",
    "Battery Analyzer": "Battery_Analyzer.py",
    "Master Dashboard": "Master_dashboard.py"
}
file_dropdown = tk.OptionMenu(app, file_var, *scripts.keys())
file_dropdown.config(bg="lightblue", fg="black")
file_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky='w')

file_var.set(next(iter(scripts.keys())))

path_label = tk.Label(app, text="Choose to see input folder path", bg="lightblue", fg="black", wraplength=200)
path_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

folder_button = tk.Button(app, text="Choose Folder", command=open_folder, bg="lightblue", fg="black")
folder_button.grid(row=1, column=1, padx=10, pady=10, sticky='w')

save_output_label = tk.Label(app, text="Run to see the output folder path", bg="lightblue", fg="black", wraplength=200)
save_output_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')

copy_var = tk.BooleanVar()
copy_check = tk.Checkbutton(app, text="Save output in preferred location", variable=copy_var, bg="lightblue", fg="black")
copy_check.grid(row=2, column=1, padx=10, pady=5, sticky='w')

run_button = tk.Button(app, text="Run", command=run_script, bg="lightblue", fg="black", state='disabled')
run_button.grid(row=3, columnspan=2, padx=10, pady=20)

app.mainloop()

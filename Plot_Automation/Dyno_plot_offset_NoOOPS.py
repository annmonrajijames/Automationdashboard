import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import webbrowser  # Add the webbrowser module

# Global variables to hold file paths, file names, distance entries, checkboxes, and data
file_paths = []
file_names = []
distance_entries = []  # List to hold distance entry widgets
column_checkboxes = {}
data_list = []
filtered_data_list = []  # Store the filtered data for each file
removed_data_list = []  # Store data where 'Idc4' < 0

def browse_folder(path_entry):
    folder_path = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, folder_path)

def select_files(path_entry, checkbox_frame, distance_frame):
    global file_paths, file_names, data_list
    # Allow the user to select multiple CSV files
    file_paths = filedialog.askopenfilenames(
        title="Select CSV files", filetypes=[("CSV Files", "*.csv")], initialdir=path_entry.get())

    if file_paths:
        file_names = [os.path.basename(fp) for fp in file_paths]
        data_list = load_data_and_columns(checkbox_frame)
        create_distance_entries(distance_frame)

def load_data_and_columns(checkbox_frame):
    global data_list, column_checkboxes, removed_data_list

    # Clear previous checkboxes
    for widget in checkbox_frame.winfo_children():
        widget.destroy()

    # Load CSV and extract column names for all files
    data_list = []
    removed_data_list = []
    column_checkboxes = {}

    for file_path in file_paths:
        try:
            data = pd.read_csv(file_path)
            data['Time'] = pd.to_datetime(data['Time'])

            # Create 'derived_time' column
            data['derived_time'] = (data['Time'] - data['Time'].min()).dt.total_seconds()

            # Apply the filtering based on 'Idc' column
            filtered_data, removed_data = filter_data_by_idc(data)
            data_list.append(filtered_data)
            removed_data_list.append(removed_data)  # Store the removed data

            # Create checkboxes for each column
            column_names = data.columns.tolist()
            for col in column_names:
                if col not in column_checkboxes:
                    var = tk.BooleanVar()
                    cb = tk.Checkbutton(checkbox_frame, text=col, variable=var)
                    cb.pack(anchor='w')
                    column_checkboxes[col] = var

        except Exception as e:
            print(f"Error loading data from {file_path}: {e}")

    synchronize_starting_indexes(data)
    return data_list

def filter_data_by_idc(data):
    """Filters the data based on the 'Idc4' column using a flag.
    Stores the removed data separately."""
    flag = 0  # Initialize the flag to 0
    removed_data = pd.DataFrame()  # DataFrame to store removed rows

    def filter_idc(row):
        nonlocal flag, removed_data
        if flag == 0:
            if row['Idc4'] < 0.5:
                removed_data = removed_data.append(row)  # Store rows with 'Idc4' < 0
                return False  # Remove this row from the filtered data
            else:
                flag = 1  # Once 'Idc4' >= 0 is found, set the flag to 1
        return True

    filtered_df = data[data.apply(filter_idc, axis=1)].copy()
    return filtered_df, removed_data

def synchronize_starting_indexes(df):
    """Synchronize the start of all filtered dataframes based on the highest index.
    Then append the removed rows back to the start of each dataframe."""
    print("df--------->",df['Time'])
    global data_list, removed_data_list
    print(df.index[0])
    start_indexes = [df.index[0] for df in data_list]
    print(start_indexes)
    highest_start_index = max(start_indexes)

    for i, (df, removed_df) in enumerate(zip(data_list, removed_data_list)):
        current_start_index = df.index[0]
        if current_start_index < highest_start_index:
            shift_amount = highest_start_index - current_start_index
            df.index = df.index + shift_amount

        # Add the removed data back at the beginning of the dataframe
        if not removed_df.empty:
            df = pd.concat([removed_df, df]).reset_index(drop=True)

        # Recalculate derived_time after adding removed data
        if 'Time' in df.columns:
            df['Time'] = pd.to_datetime(df['Time'])
            df['derived_time'] = (df['Time'] - df['Time'].min()).dt.total_seconds()

        data_list[i] = df  # Update the data_list with the modified dataframe

def create_distance_entries(distance_frame):
    global distance_entries

    # Clear previous distance entries
    for widget in distance_frame.winfo_children():
        widget.destroy()

    # Create a distance entry field for each selected file
    distance_entries = []
    for file_name in file_names:
        label = tk.Label(distance_frame, text=f"Enter total distance (km) for {file_name}:")
        label.pack(pady=5)
        entry = tk.Entry(distance_frame, width=20)
        entry.pack(pady=5)
        distance_entries.append(entry)

def submit(result_label, path_entry):
    global data_list, column_checkboxes

    # Get the columns that are checked
    selected_columns = [col for col, var in column_checkboxes.items() if var.get()]

    if data_list and selected_columns:
        try:
            total_distances = [float(entry.get()) for entry in distance_entries]
        except ValueError:
            result_label.config(text="Please enter valid numeric distances for all files.", fg="red")
            return

        results = [calculate_wh_per_km(data, total_distance) for data, total_distance in zip(data_list, total_distances)]
        plot_columns(selected_columns, path_entry.get(), results)

def calculate_wh_per_km(df, total_distance_km):
    frequency = 20  # Hz, the frequency of the data
    time_step = 1 / frequency  # Time between readings in seconds
    time_step_hours = time_step / 3600  # Convert time step to hours

    # Calculate instantaneous power
    df['Power_W'] = df['Udc4'] * df['Idc4']

    positive_power = df[df['Power_W'] > 0]['Power_W'].sum()
    negative_power = df[df['Power_W'] < 0]['Power_W'].sum()

    total_energy_wh = df['Power_W'].sum() * time_step_hours
    wh_consumed = positive_power * time_step_hours
    wh_regen = abs(negative_power * time_step_hours)

    regen_percentage = (wh_regen / (wh_consumed + wh_regen)) * 100 if wh_consumed + wh_regen > 0 else 0
    wh_per_km = total_energy_wh / total_distance_km if total_distance_km > 0 else 0

    return wh_per_km, wh_regen, wh_consumed, total_energy_wh, regen_percentage

def plot_columns(columns, save_path, results):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown']

    for i, (data, result) in enumerate(zip(data_list, results)):
        wh_per_km, wh_regen, wh_consumed, total_energy_wh, regen_percentage = result
        for col in columns:
            if col in data.columns:
                fig.add_trace(go.Scatter(
                    x=data['derived_time'],
                    y=data[col],
                    name=f"{col} ({i+1})",
                    line=dict(color=colors[i % len(colors)], dash='solid')
                ))

        fig.add_annotation(text=f"{file_names[i]}: Wh/km: {wh_per_km:.2f}, Regen: {wh_regen:.2f} Wh, Consumed: {wh_consumed:.2f} Wh",
                           xref="paper", yref="paper", x=1.01, y=0.99 - (i * 0.05), showarrow=False, font=dict(size=12, color=colors[i % len(colors)]))
        fig.add_annotation(text=f"Total Energy: {total_energy_wh:.2f} Wh, Regen%: {regen_percentage:.2f}%",
                           xref="paper", yref="paper", x=1.01, y=0.97 - (i * 0.05), showarrow=False, font=dict(size=12, color=colors[i % len(colors)]))

    fig.update_layout(title='Combined Plot for Selected Files',
                      xaxis_title='Time (in seconds)',
                      yaxis_title='Values')

    os.makedirs(save_path, exist_ok=True)
    graph_path = os.path.join(save_path, 'Combined_Plot_3.html')
    fig.write_html(graph_path)
    webbrowser.open('file://' + os.path.realpath(graph_path))

# Main Tkinter setup
root = tk.Tk()
root.title("Data Plotter and Wh/km Calculator")

# Folder Path Input
label = tk.Label(root, text="Enter Folder Path or Drag & Drop:")
label.pack(pady=5)

path_entry = tk.Entry(root, width=50)
path_entry.pack(pady=5)

browse_button = tk.Button(root, text="Browse", command=lambda: browse_folder(path_entry))
browse_button.pack(pady=5)

file_button = tk.Button(root, text="Select Files", command=lambda: select_files(path_entry, checkbox_frame, distance_frame))
file_button.pack(pady=5)

# Frame to hold dynamic distance entry fields
distance_frame = tk.Frame(root)
distance_frame.pack(pady=10)

# Frame for column checkboxes
checkbox_frame = tk.Frame(root)
checkbox_frame.pack(pady=10)

# Submit Button
submit_button = tk.Button(root, text="Submit", command=lambda: submit(result_label, path_entry))
submit_button.pack(pady=10)

# Label to display Wh/km result
result_label = tk.Label(root, text="", fg="blue")
result_label.pack(pady=10)

root.mainloop()

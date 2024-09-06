import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Tkinter GUI Setup
class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Plotter and Wh/km Calculator")

        # Folder Path Input
        self.label = tk.Label(root, text="Enter Folder Path or Drag & Drop:")
        self.label.pack(pady=5)

        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.pack(pady=5)

        # Browse Button to select folder
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_folder)
        self.browse_button.pack(pady=5)

        # Select Files Button to select two CSV files
        self.file_button = tk.Button(root, text="Select Files", command=self.select_files)
        self.file_button.pack(pady=5)

        # Entry fields for total_distance_km for both files
        self.distance_label_1 = tk.Label(root, text="Enter total distance (km) for File 1:")
        self.distance_label_1.pack(pady=5)
        self.distance_entry_1 = tk.Entry(root, width=20)
        self.distance_entry_1.pack(pady=5)

        self.distance_label_2 = tk.Label(root, text="Enter total distance (km) for File 2:")
        self.distance_label_2.pack(pady=5)
        self.distance_entry_2 = tk.Entry(root, width=20)
        self.distance_entry_2.pack(pady=5)

        # Frame for column checkboxes
        self.checkbox_frame = tk.Frame(root)
        self.checkbox_frame.pack(pady=10)

        # Submit Button
        self.submit_button = tk.Button(root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

        # Label to display Wh/km result
        self.result_label = tk.Label(root, text="", fg="blue")
        self.result_label.pack(pady=10)

        # To hold the selected file paths, extracted column names, and checkboxes for both files
        self.file_paths = []
        self.column_checkboxes = {}
        self.data_list = []
        self.file_names = []  # Store CSV file names

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, folder_path)

    def select_files(self):
        # Allow the user to select two files
        file_paths = filedialog.askopenfilenames(
            title="Select two CSV files", filetypes=[("CSV Files", "*.csv")], initialdir=self.path_entry.get())
        
        if len(file_paths) == 2:
            self.file_paths = file_paths
            self.file_names = [os.path.basename(fp) for fp in file_paths]  # Get only file names
            self.load_data_and_columns()

    def load_data_and_columns(self):
        # Clear previous checkboxes
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()

        # Load CSV and extract column names for both files
        self.data_list.clear()  # Clear previous data
        for file_path in self.file_paths:
            try:
                data = pd.read_csv(file_path)

                data['Time'] = pd.to_datetime(data['Time'])

                # Create 'derived_time' column that starts from 00:00:00
                data['derived_time'] = (data['Time'] - data['Time'].min()).dt.total_seconds()

                # Ensure the 'Udc4' and 'Idc4' columns exist
                if 'Udc4' not in data.columns or 'Idc4' not in data.columns:
                    raise ValueError(f"CSV file '{file_path}' does not contain required columns 'Udc4' or 'Idc4'.")

                # Append to the data_list for processing later
                self.data_list.append(data)

                # Create checkboxes for each column
                column_names = data.columns.tolist()
                for col in column_names:
                    if col not in self.column_checkboxes:
                        var = tk.BooleanVar()
                        cb = tk.Checkbutton(self.checkbox_frame, text=col, variable=var)
                        cb.pack(anchor='w')
                        self.column_checkboxes[col] = var

            except Exception as e:
                print(f"Error loading data from {file_path}: {e}")

    def submit(self):
        # Get the columns that are checked
        selected_columns = [col for col, var in self.column_checkboxes.items() if var.get()]

        if len(self.data_list) == 2 and selected_columns:
            # Get total distances entered by the user
            try:
                total_distance_km_1 = float(self.distance_entry_1.get())
                total_distance_km_2 = float(self.distance_entry_2.get())
            except ValueError:
                self.result_label.config(text="Please enter valid numeric distances for both files.", fg="red")
                return

            # Calculate Wh/km for both files and return extra values
            wh_per_km_1, wh_regen_1, wh_consumed_1, total_energy_wh_1, regen_percentage_1 = self.calculate_wh_per_km(self.data_list[0], total_distance_km_1)
            wh_per_km_2, wh_regen_2, wh_consumed_2, total_energy_wh_2, regen_percentage_2 = self.calculate_wh_per_km(self.data_list[1], total_distance_km_2)

            # Plot the selected columns from both files and add annotations
            self.plot_columns(selected_columns, self.path_entry.get(),
                              wh_per_km_1, wh_regen_1, wh_consumed_1, total_energy_wh_1, regen_percentage_1,
                              wh_per_km_2, wh_regen_2, wh_consumed_2, total_energy_wh_2, regen_percentage_2)

    def calculate_wh_per_km(self, df, total_distance_km):
        # Constants
        frequency = 20  # Hz, the frequency of the data
        time_step = 1 / frequency  # Time between readings in seconds
        time_step_hours = time_step / 3600  # Convert time step to hours

        # Calculate instantaneous power at each time step (P = Udc4 * Idc4)
        df['Power_W'] = df['Udc4'] * df['Idc4']

        # Separate positive and negative power (for consumption and regeneration)
        positive_power = df[df['Power_W'] > 0]['Power_W'].sum()  # Total consumption power (positive)
        negative_power = df[df['Power_W'] < 0]['Power_W'].sum()  # Total regen power (negative)

        # Calculate total energy (Wh) for both consumption and regen
        total_energy_wh = df['Power_W'].sum() * time_step_hours  # Net total energy (consumption + regen)
        wh_consumed = positive_power * time_step_hours           # Energy consumed (positive power)
        wh_regen = abs(negative_power * time_step_hours)         # Energy regenerated (negative power)

        regen_percentage = (wh_regen / (wh_consumed + wh_regen)) * 100 if wh_consumed + wh_regen > 0 else 0
        
        # Calculate Wh/km (total energy in Wh / total distance in km)
        wh_per_km = total_energy_wh / total_distance_km if total_distance_km > 0 else 0

        return wh_per_km, wh_regen, wh_consumed, total_energy_wh, regen_percentage

    def plot_columns(self, columns, save_path, wh_per_km_1, wh_regen_1, wh_consumed_1, total_energy_wh_1, regen_percentage_1,
                     wh_per_km_2, wh_regen_2, wh_consumed_2, total_energy_wh_2, regen_percentage_2):
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Define colors for each file
        colors = ['blue', 'orange']

        # Loop through each file's data and plot the selected columns
        for i, data in enumerate(self.data_list):
            for col in columns:
                if col in data.columns:
                    # Use index as x-axis
                    fig.add_trace(go.Scatter(
                        # x=data.index,
                        x=data['derived_time'],
                        y=data[col], 
                        name=f"{col} ({i+1})",  # Use short alias
                        line=dict(color=colors[i], dash='solid')
                    ))

        # Add Wh/km and other metrics as annotations for file 1
        fig.add_annotation(text=f"File 1: Wh/km: {wh_per_km_1:.2f}, Regen: {wh_regen_1:.2f} Wh, Consumed: {wh_consumed_1:.2f} Wh",
                           xref="paper", yref="paper", x=1.01, y=0.99, showarrow=False, font=dict(size=12, color="blue"))
        fig.add_annotation(text=f"Total Energy: {total_energy_wh_1:.2f} Wh, Regen%: {regen_percentage_1:.2f}%",
                           xref="paper", yref="paper", x=1.01, y=0.97, showarrow=False, font=dict(size=12, color="blue"))

        # Add Wh/km and other metrics as annotations for file 2
        fig.add_annotation(text=f"File 2: Wh/km: {wh_per_km_2:.2f}, Regen: {wh_regen_2:.2f} Wh, Consumed: {wh_consumed_2:.2f} Wh",
                           xref="paper", yref="paper", x=1.01, y=0.95, showarrow=False, font=dict(size=12, color="orange"))
        fig.add_annotation(text=f"Total Energy: {total_energy_wh_2:.2f} Wh, Regen%: {regen_percentage_2:.2f}%",
                           xref="paper", yref="paper", x=1.01, y=0.93, showarrow=False, font=dict(size=12, color="orange"))

        fig.update_layout(title='Combined Plot for Two Files',
                          xaxis_title='Time (in seconds)',
                          yaxis_title='Values')

        # Save the plot as an HTML file
        os.makedirs(save_path, exist_ok=True)
        graph_path = os.path.join(save_path, 'Combined_Plot.html')
        fig.write_html(graph_path)
        print(f"Plot saved at: {graph_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()

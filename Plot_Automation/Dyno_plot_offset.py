import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import webbrowser  # Add the webbrowser module

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

        # Select Files Button to select one or more CSV files
        self.file_button = tk.Button(root, text="Select Files", command=self.select_files)
        self.file_button.pack(pady=5)

        # Frame to hold dynamic distance entry fields
        self.distance_frame = tk.Frame(root)
        self.distance_frame.pack(pady=10)

        # Frame for column checkboxes
        self.checkbox_frame = tk.Frame(root)
        self.checkbox_frame.pack(pady=10)

        # Submit Button
        self.submit_button = tk.Button(root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

        # Label to display Wh/km result
        self.result_label = tk.Label(root, text="", fg="blue")
        self.result_label.pack(pady=10)

        # Variables to hold file paths, distance entries, and checkboxes
        self.file_paths = []
        self.file_names = []
        self.distance_entries = []  # List to hold distance entry widgets
        self.column_checkboxes = {}
        self.data_list = []
        self.filtered_data_list = []  # Store the filtered data for each file

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, folder_path)

    def select_files(self):
        # Allow the user to select multiple CSV files
        file_paths = filedialog.askopenfilenames(
            title="Select CSV files", filetypes=[("CSV Files", "*.csv")], initialdir=self.path_entry.get())

        if file_paths:
            self.file_paths = file_paths
            self.file_names = [os.path.basename(fp) for fp in file_paths]
            self.load_data_and_columns()

            # Create dynamic distance entry fields based on number of files selected
            self.create_distance_entries()

    def synchronize_starting_indexes(self, data):
        """Synchronize the start of all filtered dataframes based on the highest index."""
        # Get the starting index for each filtered dataframe
        start_indexes = [df.index[0] for df in self.data_list]
        

        # Find the highest starting index
        highest_start_index = max(start_indexes)
        
        
        # Shift each dataframe so that they all start at the highest index
        for i in range(len(self.data_list)):
            df = self.data_list[i]
            current_start_index = self.data_list[i].index[0]   
            print("curr",current_start_index)
            print("high",highest_start_index)
            if current_start_index < highest_start_index:
                print(current_start_index) 
                shift_amount = highest_start_index - current_start_index
                print("shift",shift_amount)
                self.data_list[i].index = self.data_list[i].index + shift_amount

                data['Time'] = pd.to_datetime(data['Time'])

                # Create 'derived_time' column that starts from 00:00:00
                data['derived_time'] = (data['Time'] - data['Time'].min()).dt.total_seconds()

                        # Convert 'Time' column to datetime
            if 'Time' in df.columns:
                df['Time'] = pd.to_datetime(df['Time'])
                
                # Create 'derived_time' column that starts from 00:00:00
                df['derived_time'] = (df['Time'] - df['Time'].min()).dt.total_seconds()


        # Print the new starting indexes for verification
        new_start_indexes = [df.index[0] for df in self.data_list]
        print("New start indexes:", new_start_indexes)

    def load_data_and_columns(self):
        # Clear previous checkboxes
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()

        # Load CSV and extract column names for all files
        self.data_list.clear()
        self.column_checkboxes.clear()

        for file_path in self.file_paths:
            try:
                data = pd.read_csv(file_path)
                data['Time'] = pd.to_datetime(data['Time'])

                # Create 'derived_time' column that starts from 00:00:00
                data['derived_time'] = (data['Time'] - data['Time'].min()).dt.total_seconds()

                # Apply the filtering based on 'Idc' column
                filtered_data = self.filter_data_by_idc(data)
                print("Filtered data--------------------->",filtered_data)
                
                # Append to the data_list for further processing
                self.data_list.append(filtered_data)

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

        # Synchronize starting indexes after all files have been filtered
        self.synchronize_starting_indexes(filtered_data)

    def filter_data_by_idc(self, data):
        """Filters the data based on the 'Idc' column using a flag."""
        flag = 0  # Initialize the flag to 0

        # Function to apply the condition
        def filter_idc(row):
            nonlocal flag  # Use nonlocal to modify the flag inside the nested function
            # If flag is 0 and 'Idc' is less than 0.5, remove this row
            if flag == 0:
                if row['Idc4'] < 0:
                    return False  # Remove this row
                else:
                    flag = 1  # Once 'Idc' >= 0.5 is found, set the flag to 1
            # Keep this row if the flag is set to 1
            return True

        # Apply the filter function to each row
        filtered_df = data[data.apply(filter_idc, axis=1)].copy()  # Use .copy() to avoid warnings
        return filtered_df

    def create_distance_entries(self):
        # Clear previous distance entries
        for widget in self.distance_frame.winfo_children():
            widget.destroy()

        # Create a distance entry field for each selected file
        self.distance_entries.clear()
        for i, file_name in enumerate(self.file_names):
            label = tk.Label(self.distance_frame, text=f"Enter total distance (km) for {file_name}:")
            label.pack(pady=5)
            entry = tk.Entry(self.distance_frame, width=20)
            entry.pack(pady=5)
            self.distance_entries.append(entry)

    def submit(self):
        print("submit")
        # Get the columns that are checked
        selected_columns = [col for col, var in self.column_checkboxes.items() if var.get()]


        if self.data_list and selected_columns:    
        # Get total distances entered by the user for each file
            try:
                total_distances = [float(entry.get()) for entry in self.distance_entries]
            except ValueError:
                self.result_label.config(text="Please enter valid numeric distances for all files.", fg="red")
                return

            # Calculate Wh/km and other metrics for each file
            results = []
            for data, total_distance_km in zip(self.data_list, total_distances):
                results.append(self.calculate_wh_per_km(data, total_distance_km))
            print("1")
            # Plot the selected columns from all files and add annotations
            self.plot_columns(selected_columns, self.path_entry.get(), results)

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

    def plot_columns(self, columns, save_path, results):
        print("plot_columns")
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Define colors for each file (loop to extend for multiple files)
        colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown']
        
        # Print the first 1000 rows of 'Idc4' column for each dataframe
        for i, df in enumerate(self.data_list):
            print(f"DataFrame {i} 'Idc4' column (first 1000 rows):")
            print(df['Idc4'].head(1000))
            print("\n")
        

        for i, (data, result) in enumerate(zip(self.data_list, results)):
            wh_per_km, wh_regen, wh_consumed, total_energy_wh, regen_percentage = result
            for col in columns:
                if col in data.columns:
                    # Use derived time as x-axis
                    fig.add_trace(go.Scatter(
                        x=data['derived_time'],
                        y=data[col], 
                        # name=f"{col} ({self.file_names[i]})",
                        name=f"{col} ({i+1})",
                        line=dict(color=colors[i % len(colors)], dash='solid')
                    ))

            # Add Wh/km and other metrics as annotations
            fig.add_annotation(text=f"{self.file_names[i]}: Wh/km: {wh_per_km:.2f}, Regen: {wh_regen:.2f} Wh, Consumed: {wh_consumed:.2f} Wh",
                               xref="paper", yref="paper", x=1.01, y=0.99 - (i * 0.05), showarrow=False, font=dict(size=12, color=colors[i % len(colors)]))
            fig.add_annotation(text=f"Total Energy: {total_energy_wh:.2f} Wh, Regen%: {regen_percentage:.2f}%",
                               xref="paper", yref="paper", x=1.01, y=0.97 - (i * 0.05), showarrow=False, font=dict(size=12, color=colors[i % len(colors)]))

        fig.update_layout(title='Combined Plot for Selected Files',
                          xaxis_title='Time (in seconds)',
                          yaxis_title='Values')

        # Save the plot as an HTML file
        os.makedirs(save_path, exist_ok=True)
        graph_path = os.path.join(save_path, 'Combined_Plot_2.html')
        fig.write_html(graph_path)
        print(f"Plot saved at: {graph_path}")

        # Automatically open the saved plot in the default web browser
        webbrowser.open('file://' + os.path.realpath(graph_path))  # Open the HTML file


if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()

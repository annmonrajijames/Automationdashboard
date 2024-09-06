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
        self.root.title("dyno_analysis")

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

        # Frame for column checkboxes
        self.checkbox_frame = tk.Frame(root)
        self.checkbox_frame.pack(pady=10)

        # Submit Button
        self.submit_button = tk.Button(root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

        # To hold the selected file paths, extracted column names, and checkboxes for both files
        self.file_paths = []
        self.column_checkboxes = {}
        self.data_list = []

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

                # Ensure the 'Time' column is in datetime format
                data['Time'] = pd.to_datetime(data['Time'])

                # Create 'derived_time' column that starts from 00:00:00
                data['derived_time'] = (data['Time'] - data['Time'].min()).dt.total_seconds()

                # Append to the data_list for plotting later
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
            # Plot the selected columns from both files
            self.plot_columns(selected_columns, self.path_entry.get())

    def plot_columns(self, columns, save_path):
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Define colors for each file
        colors = ['blue', 'orange']

        # Loop through each file's data and plot the selected columns
        for i, data in enumerate(self.data_list):
            for col in columns:
                if col in data.columns:
                    # Use derived_time as x-axis
                    fig.add_trace(go.Scatter(
                        x=data['derived_time'], 
                        y=data[col], 
                        name=f"{col} (File {i+1})", 
                        line=dict(color=colors[i], dash='solid')
                    ))

        fig.update_layout(title='Combined Plot for Two Files',
                          xaxis_title='Derived Time (seconds)',
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

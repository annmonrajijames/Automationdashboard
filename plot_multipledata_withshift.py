import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import webbrowser
import numpy as np

# Tkinter GUI Setup
class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Plotter")

        # File Path Input
        self.label = tk.Label(root, text="Select Files:")
        self.label.pack(pady=5)

        self.file_listbox = tk.Listbox(root, width=60, height=4)
        self.file_listbox.pack(pady=5)

        # Browse Button to select file
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Search Box for filtering columns
        self.search_label = tk.Label(root, text="Search Columns:")
        self.search_label.pack(pady=5)
        self.search_entry = tk.Entry(root, width=50)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.update_checkboxes)

        # Scrollable Frame for checkboxes
        self.checkbox_frame = tk.Frame(root)
        self.checkbox_frame.pack(pady=5)

        # Add a canvas with scrollbar for the checkboxes
        self.canvas = tk.Canvas(self.checkbox_frame)
        self.scrollbar = tk.Scrollbar(self.checkbox_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Dropdown for Index Column Selection
        self.index_label = tk.Label(root, text="Select Index Column:")
        self.index_label.pack(pady=5)
        self.index_column_dropdown = ttk.Combobox(root, state="readonly")
        self.index_column_dropdown.pack(pady=5)

        # Submit Button
        self.submit_button = tk.Button(root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

        # To hold the extracted column names and their corresponding checkboxes
        self.column_names = []
        self.checkbox_vars = {}  # To store the checkbox variables for each column
        self.data_frames = []  # List to store data from multiple files
        self.file_directory = ""  # Directory of the files

    def browse_file(self):
        # Allow the user to select any file type
        file_paths = filedialog.askopenfilenames(filetypes=[("All files", "*.*")])
        if file_paths:
            # Store the directory path
            self.file_directory = os.path.dirname(file_paths[0])

            # Clear the current listbox
            self.file_listbox.delete(0, tk.END)
            
            for file_path in file_paths:
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
                self.load_data_and_columns(file_path)

    def load_data_and_columns(self, file_path):
        # Clear the previous checkboxes and dropdown
        self.index_column_dropdown.set('')

        # Load the file based on its extension
        if os.path.isfile(file_path):
            try:
                if file_path.endswith('.csv'):
                    self.data = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.data = pd.read_excel(file_path)
                else:
                    raise ValueError("Unsupported file format")

                # Store data for each file in the list
                self.data_frames.append(self.data)

                # Extract column names
                self.column_names = self.data.columns.tolist()

                # Initialize checkboxes with the full list of columns
                self.update_checkboxes()

                # Populate the dropdown with column names for index selection
                self.index_column_dropdown['values'] = self.column_names

                print("Columns available for plotting:", self.column_names)
            except Exception as e:
                print(f"Error loading data: {e}")

    def update_checkboxes(self, event=None):
        # Get the search query
        search_query = self.search_entry.get().lower()

        # Filter the column names based on the search query
        filtered_columns = [col for col in self.column_names if search_query in col.lower()]

        # Clear the current checkboxes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Add checkboxes for the filtered columns
        for col in filtered_columns:
            # Retain the checkbox state using self.checkbox_vars
            if col not in self.checkbox_vars:
                self.checkbox_vars[col] = tk.BooleanVar()

            cb = tk.Checkbutton(self.scrollable_frame, text=col, variable=self.checkbox_vars[col])
            cb.pack(anchor='w')

    def submit(self):
        # Get the columns that are checked
        selected_columns = [col for col, var in self.checkbox_vars.items() if var.get()]

        # Get the selected index column from the dropdown
        selected_index_column = self.index_column_dropdown.get()

        if self.data_frames and selected_columns and selected_index_column:
            # Plot the selected columns with the selected index
            self.plot_columns(selected_columns, selected_index_column, self.file_directory)

    def plot_columns(self, columns, index_column, save_path):
        # Create the subplots
        fig = make_subplots()

        # List to store the original x-values (to apply shifts later)
        original_x_values = []

        # Loop through each dataframe (for each file)
        for i, data in enumerate(self.data_frames):
            # Create a relative x-axis (just use the row number as index)
            relative_x = np.arange(len(data))  # Use the row index (0, 1, 2, ...) for comparison
            
            # Store original x-values for shifting purposes (row indices)
            original_x_values.append(relative_x)

            # Add trace for each selected column from the corresponding file
            for col in columns:
                trace_name = f"File {i + 1}: {col}"
                fig.add_trace(go.Scatter(x=relative_x, y=data[col], name=trace_name))

        # Create individual sliders for each trace to allow horizontal movement
        sliders = []
        
        # Iterate over each trace and create a unique slider for it
        for i, trace in enumerate(fig.data):
            steps = []
            
            # Create steps for moving the trace horizontally (adjusting x-values)
            for shift in np.arange(-50.0, 50.0, 1):  # Shift steps (adjust the range as needed)
                shifted_x = original_x_values[i] + shift  # Shift by relative positions

                # Append each step for this trace
                steps.append({
                    'method': 'restyle',
                    'args': [{'x': [shifted_x]}, [i]],  # Apply the shift only to the i-th trace
                    'label': f"{int(shift)}"  # Label shows the amount of shift
                })

            # Append a unique slider for this trace
            sliders.append({
                'active': 50,  # Start at the default position (no shift)
                'currentvalue': {"prefix": f"File {i + 1} shift: "},
                'steps': steps,
                'len': 0.9,  # Length of the slider bar (adjust this if needed)
                'x': 0,    # Position of the slider on the x-axis
                'y': 1.5 - (i * 0.25),  # Stack sliders vertically (adjust spacing as needed)
            })

        # Update layout with the sliders
        fig.update_layout(
            sliders=sliders,
            xaxis_title="Relative Position (Index)",
            yaxis_title="Values",
            height=600 + 50 * len(fig.data)  # Adjust height based on number of traces
        )

        # Save the plot as an HTML file
        os.makedirs(save_path, exist_ok=True)
        graph_path = os.path.join(save_path, 'Generated_Plot.html')
        fig.write_html(graph_path)
        print(f"Plot saved at: {graph_path}")

        # Automatically open the saved plot in the default web browser
        webbrowser.open('file://' + os.path.realpath(graph_path))  # Open the HTML file





if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()

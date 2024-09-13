import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import webbrowser  # Add the webbrowser module


# Tkinter GUI Setup
class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-File Data Plotter")

        # File Path Input
        self.label = tk.Label(root, text="Select File (CSV or Excel):")
        self.label.pack(pady=5)

        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.pack(pady=5)

        # Browse Button to select file
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Button to finalize file selection
        self.done_button = tk.Button(root, text="Done Selecting Files", command=self.finalize_files)
        self.done_button.pack(pady=5)

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
        self.file_paths = []  # To store paths of selected files
        self.data_list = []  # To store dataframes for each file
        self.column_names_list = []  # To store columns for each file
        self.checkbox_vars = {}  # To store the checkbox variables for each column
        self.data = None

    def browse_file(self):
        # Allow the user to select either a CSV or Excel file
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if file_path:
            self.file_paths.append(file_path)  # Store the file path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)

            # After file selection, extract columns and store data
            self.load_data_and_columns(file_path)

    def load_data_and_columns(self, file_path):
        try:
            # Load the file based on its extension
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                data = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")

            # Store the data and columns for this file
            self.data_list.append(data)
            self.column_names_list.append(data.columns.tolist())

            # Initialize checkboxes with the full list of columns from the latest file
            self.update_checkboxes()

            # Populate the dropdown with column names for index selection (latest file)
            self.index_column_dropdown['values'] = self.column_names_list[-1]

            print(f"Columns available for plotting from {file_path}: {self.column_names_list[-1]}")
        except Exception as e:
            print(f"Error loading data: {e}")

    def update_checkboxes(self, event=None):
        if not self.column_names_list:
            return

        # Get the search query
        search_query = self.search_entry.get().lower()

        # Filter the column names of the latest file based on the search query
        filtered_columns = [col for col in self.column_names_list[-1] if search_query in col.lower()]

        # Clear the current checkboxes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Add checkboxes for the filtered columns
        for col in filtered_columns:
            if col not in self.checkbox_vars:
                self.checkbox_vars[col] = tk.BooleanVar()

            cb = tk.Checkbutton(self.scrollable_frame, text=col, variable=self.checkbox_vars[col])
            cb.pack(anchor='w')

    def finalize_files(self):
        # Lock file selection after user is done selecting files
        self.browse_button.config(state=tk.DISABLED)
        print(f"Selected files: {self.file_paths}")

    def submit(self):
        # Get the columns that are checked
        selected_columns = [col for col, var in self.checkbox_vars.items() if var.get()]

        # Get the selected index column from the dropdown
        selected_index_column = self.index_column_dropdown.get()

        if self.data_list and selected_columns and selected_index_column:
            # Plot the selected columns with the selected index for all files
            self.plot_columns(selected_columns, selected_index_column, os.path.dirname(self.path_entry.get()))

    def plot_columns(self, columns, index_column, save_path):
        # Plot using Plotly
        fig = make_subplots()

        # Loop through all selected files and their data
        for i, data in enumerate(self.data_list):
            # Set the selected column as index
            if index_column in data.columns:
                data.set_index(index_column, inplace=True)

            # Add trace for each selected column from each file
            for col in columns:
                fig.add_trace(go.Scatter(x=data.index, y=data[col], name=f"File {i+1}: {col}"))

        # Update layout with opacity dropdown
        fig.update_layout(
            title='Combined Plot from Multiple Files',
            xaxis_title=index_column,
            yaxis_title='Value',
            updatemenus=[{
                'buttons': [
                    {'args': [{'opacity': 0.2}], 'label': '20%', 'method': 'restyle'},
                    {'args': [{'opacity': 0.4}], 'label': '40%', 'method': 'restyle'},
                    {'args': [{'opacity': 0.6}], 'label': '60%', 'method': 'restyle'},
                    {'args': [{'opacity': 0.8}], 'label': '80%', 'method': 'restyle'},
                    {'args': [{'opacity': 1}], 'label': '100%', 'method': 'restyle'}
                ],
                'direction': 'down',
                'showactive': True,
                'x': 1.05,
                'xanchor': 'left',
                'y': 1.20,
                'yanchor': 'top'
            }]
        )

        fig.update_xaxes(tickformat='%H:%M:%S')

        # Save the plot as an HTML file
        os.makedirs(save_path, exist_ok=True)
        graph_path = os.path.join(save_path, 'Generated_MultiFile_Plot.html')
        fig.write_html(graph_path)
        print(f"Plot saved at: {graph_path}")

        # Automatically open the saved plot in the default web browser
        webbrowser.open('file://' + os.path.realpath(graph_path))  # Open the HTML file


if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()

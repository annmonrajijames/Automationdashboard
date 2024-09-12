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
        self.root.title("Data Plotter")

        # File Path Input
        self.label = tk.Label(root, text="Select File (CSV or Excel):")
        self.label.pack(pady=5)

        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.pack(pady=5)

        # Browse Button to select file
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Search Box for filtering columns
        self.search_label = tk.Label(root, text="Search Columns:")
        self.search_label.pack(pady=5)
        self.search_entry = tk.Entry(root, width=50)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.update_checkboxes)  # Bind the search entry to key releases

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

        # Formula Bar for selecting current, voltage, and time columns
        self.formula_label = tk.Label(root, text="Select Columns for Watt-hour Calculation:")
        self.formula_label.pack(pady=5)

        # Dropdown for current, voltage, and time selection
        self.current_label = tk.Label(root, text="Current Column:")
        self.current_label.pack(pady=2)
        self.current_column_dropdown = ttk.Combobox(root, state="readonly")
        self.current_column_dropdown.pack(pady=2)

        self.voltage_label = tk.Label(root, text="Voltage Column:")
        self.voltage_label.pack(pady=2)
        self.voltage_column_dropdown = ttk.Combobox(root, state="readonly")
        self.voltage_column_dropdown.pack(pady=2)


        # Time Difference Input
        self.time_diff_label = tk.Label(root, text="Time Difference (seconds):")
        self.time_diff_label.pack(pady=5)
        self.time_diff_entry = tk.Entry(root, width=20)
        self.time_diff_entry.pack(pady=5)

        # Submit Button
        self.submit_button = tk.Button(root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

        # To hold the extracted column names and their corresponding checkboxes
        self.column_names = []
        self.checkbox_vars = {}  # To store the checkbox variables for each column
        self.data = None

    def browse_file(self):
        # Allow the user to select either a CSV or Excel file
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, file_path)

        # After file selection, extract columns
        self.load_data_and_columns(file_path)

    def load_data_and_columns(self, file_path):
        # Clear the previous checkboxes and dropdowns
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.index_column_dropdown.set('')
        self.current_column_dropdown.set('')
        self.voltage_column_dropdown.set('')
        self.checkbox_vars.clear()

        # Load the file based on its extension
        if os.path.isfile(file_path):
            try:
                if file_path.endswith('.csv'):
                    self.data = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.data = pd.read_excel(file_path)
                else:
                    raise ValueError("Unsupported file format")

                # Extract column names
                self.column_names = self.data.columns.tolist()

                # Initialize checkboxes with the full list of columns
                self.update_checkboxes()

                # Populate the dropdowns with column names for index, current, voltage, and time selection
                self.index_column_dropdown['values'] = self.column_names
                self.current_column_dropdown['values'] = self.column_names
                self.voltage_column_dropdown['values'] = self.column_names

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

        # Get the selected index, current, voltage, and time columns from the dropdowns
        selected_index_column = self.index_column_dropdown.get()
        selected_current_column = self.current_column_dropdown.get()
        selected_voltage_column = self.voltage_column_dropdown.get()

        # Get the time difference entered by the user
        time_diff = self.time_diff_entry.get()

        if self.data is not None and selected_columns and selected_index_column and time_diff:
            try:
                # Convert time difference to float
                time_diff = float(time_diff)
                # Plot the selected columns with the selected index
                self.plot_columns(selected_columns, selected_index_column, selected_current_column, selected_voltage_column,  os.path.dirname(self.path_entry.get()), time_diff)
            except ValueError:
                print("Invalid time difference value")

    def plot_columns(self, columns, index_column, current_column, voltage_column, save_path, time_diff):
        # Set the selected column as index
        if index_column in self.data.columns:
            self.data.set_index(index_column, inplace=True)

        # Calculate Watt-hours using the entered time difference
        watt_h = abs((self.data[current_column] * self.data[voltage_column] * time_diff).sum()) / 3600

        # Plot using Plotly
        fig = make_subplots()

        # Add trace for each selected column
        for col in columns:
            fig.add_trace(go.Scatter(x=self.data.index, y=self.data[col], name=col))

        # Add opacity modification dropdown
        fig.update_layout(
            title=f'Analysis',
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

        # Add Watt-hour value near the legend
        fig.add_annotation(
            text=f"Watt-hours (Wh): {watt_h:.2f}",
            xref="paper", yref="paper",
            x=1.05, y=1.05,
            showarrow=False
        )

        fig.update_xaxes(tickformat='%H:%M:%S')

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

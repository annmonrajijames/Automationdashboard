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
        self.root.title("Data Plotter")

        # File Path Input
        self.label = tk.Label(root, text="Select File (CSV or Excel):")
        self.label.pack(pady=5)

        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.pack(pady=5)

        # Browse Button to select file
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Frame for column checkboxes
        self.checkbox_frame = tk.Frame(root)
        self.checkbox_frame.pack(pady=10)

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
        self.column_checkboxes = {}
        self.data = None

    def browse_file(self):
        # Allow the user to select either a CSV or Excel file
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, file_path)

        # After file selection, extract columns
        self.load_data_and_columns(file_path)

    def load_data_and_columns(self, file_path):
        # Clear the previous checkboxes and dropdown
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
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

                # Extract column names
                self.column_names = self.data.columns.tolist()

                # Create checkboxes for each column
                for col in self.column_names:
                    var = tk.BooleanVar()
                    cb = tk.Checkbutton(self.checkbox_frame, text=col, variable=var)
                    cb.pack(anchor='w')
                    self.column_checkboxes[col] = var

                # Populate the dropdown with column names for index selection
                self.index_column_dropdown['values'] = self.column_names

                print("Columns available for plotting:", self.column_names)
            except Exception as e:
                print(f"Error loading data: {e}")

    def submit(self):
        # Get the columns that are checked
        selected_columns = [col for col, var in self.column_checkboxes.items() if var.get()]

        # Get the selected index column from the dropdown
        selected_index_column = self.index_column_dropdown.get()

        if self.data is not None and selected_columns and selected_index_column:
            # Plot the selected columns with the selected index
            self.plot_columns(selected_columns, selected_index_column, os.path.dirname(self.path_entry.get()))

    def plot_columns(self, columns, index_column, save_path):
        # Set the selected column as index
        if index_column in self.data.columns:
            self.data.set_index(index_column, inplace=True)

        # Plot using Plotly
        fig = make_subplots()

        # Add trace for each selected column
        for col in columns:
            fig.add_trace(go.Scatter(x=self.data.index, y=self.data[col], name=col))

        fig.update_layout(title=f'Analysis',
                          xaxis_title=index_column,
                          yaxis_title='Value')

        fig.update_xaxes(tickformat='%H:%M:%S')

        # Save the plot as an HTML file
        os.makedirs(save_path, exist_ok=True)
        graph_path = os.path.join(save_path, 'Generated_Plot.html')
        fig.write_html(graph_path)
        print(f"Plot saved at: {graph_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()

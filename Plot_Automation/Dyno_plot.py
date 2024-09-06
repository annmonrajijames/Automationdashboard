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

        # Folder Path Input
        self.label = tk.Label(root, text="Enter Folder Path or Drag & Drop:")
        self.label.pack(pady=5)

        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.pack(pady=5)

        # Browse Button to select folder
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_folder)
        self.browse_button.pack(pady=5)

        # Frame for column checkboxes
        self.checkbox_frame = tk.Frame(root)
        self.checkbox_frame.pack(pady=10)

        # Submit Button
        self.submit_button = tk.Button(root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

        # To hold the extracted column names and their corresponding checkboxes
        self.column_names = []
        self.column_checkboxes = {}
        self.data = None

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, folder_path)

        # After folder selection, extract columns
        self.load_data_and_columns(folder_path)

    def load_data_and_columns(self, folder_path):
        # Clear the previous checkboxes
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()

        # Load CSV and extract column names
        if os.path.isdir(folder_path):
            log_file = None
            for file in os.listdir(folder_path):
                if file.startswith('NDURO') and file.endswith('.csv'):
                    log_file = os.path.join(folder_path, file)
                    break

            if log_file:
                try:
                    self.data = pd.read_csv(log_file)
                    # Extract column names
                    self.column_names = self.data.columns.tolist()

                    # Create checkboxes for each column
                    for col in self.column_names:
                        var = tk.BooleanVar()
                        cb = tk.Checkbutton(self.checkbox_frame, text=col, variable=var)
                        cb.pack(anchor='w')
                        self.column_checkboxes[col] = var

                    print("Columns available for plotting:", self.column_names)
                except Exception as e:
                    print(f"Error loading data: {e}")

    def submit(self):
        # Get the columns that are checked
        selected_columns = [col for col, var in self.column_checkboxes.items() if var.get()]

        if self.data is not None and selected_columns:
            # Plot the selected columns
            self.plot_columns(selected_columns, self.path_entry.get())

    def plot_columns(self, columns, save_path):
        # Set the index to 'Time'
        if 'Time' in self.data.columns:
            self.data.set_index('Time', inplace=True)

        # Plot using Plotly
        fig = make_subplots()

        # Add trace for each selected column
        for col in columns:
            fig.add_trace(go.Scatter(x=self.data.index, y=self.data[col], name=col))

        fig.update_layout(title=f'Analysis',
                          xaxis_title='Time',
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

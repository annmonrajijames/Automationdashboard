import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

# Tkinter GUI Setup
class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Plotter")

        # Main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Control frame on the left
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.grid(row=0, column=0, sticky="ns")

        # Plot frame on the right
        self.plot_frame = tk.Frame(self.main_frame)
        self.plot_frame.grid(row=0, column=1, sticky="nsew")

        # Make the plot frame expand more
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # File Path Input
        self.label = tk.Label(self.control_frame, text="Select Files:")
        self.label.pack(pady=5)

        self.file_listbox = tk.Listbox(self.control_frame, width=60, height=4)
        self.file_listbox.pack(pady=5)

        # Browse Button to select file
        self.browse_button = tk.Button(self.control_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Search Box for filtering columns
        self.search_label = tk.Label(self.control_frame, text="Search Columns:")
        self.search_label.pack(pady=5)
        self.search_entry = tk.Entry(self.control_frame, width=50)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.update_checkboxes)

        # Scrollable Frame for checkboxes
        self.checkbox_frame = tk.Frame(self.control_frame)
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
        self.index_label = tk.Label(self.control_frame, text="Select Index Column:")
        self.index_label.pack(pady=5)
        self.index_column_dropdown = ttk.Combobox(self.control_frame, state="readonly")
        self.index_column_dropdown.pack(pady=5)

        # Display Selected Columns
        self.selected_columns_label = tk.Label(self.control_frame, text="Selected Columns:")
        self.selected_columns_label.pack(pady=5)
        self.selected_columns_display = tk.Label(self.control_frame, text="", wraplength=400, justify="left")
        self.selected_columns_display.pack(pady=5)

        # Submit Button
        self.submit_button = tk.Button(self.control_frame, text="Submit", command=self.submit)
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
            # Display selected columns for verification
            self.selected_columns_display.config(text="\n".join(selected_columns))

            # Ask for confirmation before plotting
            if messagebox.askyesno("Confirm Plot", "Do you want to plot the selected columns?"):
                # Plot the selected columns with the selected index
                self.plot_columns(selected_columns, selected_index_column, self.file_directory)

    def plot_columns(self, columns, index_column, save_path):
        fig, ax = plt.subplots(figsize=(10, 6))

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
                line, = ax.plot(relative_x, data[col], label=trace_name)
                line.set_picker(True)  # Enable picking for the line

        ax.set_xlabel("Relative Position (Index)")
        ax.set_ylabel("Values")
        ax.set_title("Comparison Plot")
        legend = ax.legend()

        # Save the plot as an image file
        os.makedirs(save_path, exist_ok=True)
        graph_path = os.path.join(save_path, 'Generated_Plot.png')
        plt.savefig(graph_path)
        print(f"Plot saved at: {graph_path}")

        # Display the plot in the Tkinter application
        self.display_plot(fig, legend)

    def display_plot(self, fig, legend):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self.plot_frame)
        toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

        # Connect the pick event to toggle visibility
        fig.canvas.mpl_connect('pick_event', self.toggle_visibility)

        # Connect the legend click event to toggle visibility
        for legend_line, original_line in zip(legend.get_lines(), fig.axes[0].get_lines()):
            legend_line.set_picker(True)
            legend_line.set_pickradius(5)
            legend_line.original_line = original_line

        fig.canvas.mpl_connect('pick_event', self.toggle_legend_visibility)

    def toggle_visibility(self, event):
        line = event.artist
        visible = not line.get_visible()
        line.set_visible(visible)
        line.figure.canvas.draw()

    def toggle_legend_visibility(self, event):
        legend_line = event.artist
        original_line = legend_line.original_line
        visible = not original_line.get_visible()
        original_line.set_visible(visible)
        legend_line.set_alpha(1.0 if visible else 0.2)
        original_line.figure.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()
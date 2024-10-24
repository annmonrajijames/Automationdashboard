import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import mplcursors  # Import mplcursors

# Tkinter GUI Setup
class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Plotter")

        # Create a main canvas for the entire page
        self.main_canvas = tk.Canvas(root)
        self.main_canvas.pack(side="left", fill=tk.BOTH, expand=True)

        # Add scrollbar to the canvas
        self.main_scrollbar = tk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.main_scrollbar.pack(side="right", fill="y")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)

        # Create a frame inside the canvas to hold the actual content
        self.page_frame = tk.Frame(self.main_canvas)

        # Bind the frame configuration to update the scroll region
        self.page_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        # Create a window within the canvas to contain the frame
        self.main_canvas.create_window((0, 0), window=self.page_frame, anchor="nw")

        # Bind mouse wheel scrolling to the entire canvas
        self.page_frame.bind_all("<MouseWheel>", self._on_mousewheel)

        # Main content inside the frame
        self.build_ui()

    def _on_mousewheel(self, event):
        """Enable scrolling the entire page with mouse wheel."""
        self.main_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    def build_ui(self):
        """Build the UI inside the scrollable page_frame."""
        # Control frame on the left
        self.control_frame = tk.Frame(self.page_frame)
        self.control_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        # Plot frame on the right
        self.plot_frame = tk.Frame(self.page_frame)
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Make the plot frame expand more
        self.page_frame.columnconfigure(1, weight=1)
        self.page_frame.rowconfigure(0, weight=1)

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

        # Bind mouse wheel scrolling to the checkboxes
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Checkbox for Select All
        self.select_all_var = tk.IntVar()
        self.select_all_checkbox = tk.Checkbutton(self.control_frame, text="Select All", variable=self.select_all_var, command=self.toggle_select_all)
        self.select_all_checkbox.pack(pady=5)

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

        # Variables for plot management
        self.fig = None
        self.ax_primary = None
        self.ax_secondary = None
        self.ax_tertiary = None
        self.plot_initialized = False
 
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
        # Clear previous selections
        self.index_column_dropdown.set('')
       
        # Define a function to detect valid header row
        def detect_header_row(df):
            # Check the first two rows to determine which contains the headers
            for i in range(2):
                row = df.iloc[i]
                if all(isinstance(x, str) for x in row):  # Check if all entries are strings (likely headers)
                    return i  # Return the index of the row containing headers
            return 0  # Default to first row if no string-based header is found
 
        # Load the file based on its extension
        if os.path.isfile(file_path):
            try:
                if file_path.endswith('.csv'):
                    # Load the first few rows to check for header location
                    df = pd.read_csv(file_path, nrows=5, skip_blank_lines=True)
 
                    # Detect where the header row is
                    header_row = detect_header_row(df)
 
                    # Reload the CSV using the detected header row
                    self.data = pd.read_csv(file_path, header=header_row, skip_blank_lines=True)
 
                elif file_path.endswith('.xlsx'):
                    # Load the first few rows to check for header location
                    df = pd.read_excel(file_path, nrows=5, skip_blank_lines=True)
 
                    # Detect where the header row is
                    header_row = detect_header_row(df)
 
                    # Reload the Excel file using the detected header row
                    self.data = pd.read_excel(file_path, header=header_row, skip_blank_lines=True)
 
                else:
                    raise ValueError("Unsupported file format")
 
                # Drop any fully empty rows
                self.data.dropna(how='all', inplace=True)
 
                # Handle Serial Number addition if missing
                if 'Serial Number' not in self.data.columns:
                    self.data['Serial Number'] = range(1, len(self.data) + 1)
 
                # Handle Time conversion if present
                if 'Time' in self.data.columns:
                    try:
                        self.data['Time'] = pd.to_datetime(self.data['Time'], errors='coerce')
                    except Exception as e:
                        print(f"Error parsing Time column: {e}")
 
                # Store data for each file in the list
                self.data_frames.append(self.data)
 
                # Extract the column names
                self.column_names = self.data.columns.tolist()
 
                # Update the checkboxes with the full list of columns
                self.update_checkboxes()
 
                # Filter only 'Serial Number' and 'Time' columns for index selection
                filtered_index_columns = [col for col in self.column_names if col.lower() in ['serial number', 'time']]
 
                # Populate the dropdown with filtered column names for index selection
                self.index_column_dropdown['values'] = filtered_index_columns
 
                print("Columns available for plotting:", self.column_names)
            except Exception as e:
                print(f"Error loading data: {e}")

    def toggle_select_all(self):
        """Toggle all checkboxes that are currently visible (filtered)."""
        select_all = self.select_all_var.get()
        search_term = self.search_entry.get().lower()

        # Iterate only over the checkboxes that are currently visible (i.e., filtered)
        for col, var in self.checkbox_vars.items():
            if search_term in col.lower():  # Only toggle those that match the search
                var.set(select_all)
 
    def update_checkboxes(self, event=None):
        """Update checkboxes based on the filtered column names."""
        search_term = self.search_entry.get().lower()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Re-create checkboxes based on the filtered columns
        for column_name in self.column_names:
            if search_term in column_name.lower():
                var = self.checkbox_vars.get(column_name, tk.IntVar())
                checkbox = tk.Checkbutton(self.scrollable_frame, text=column_name, variable=var, command=self.update_select_all_checkbox)
                checkbox.pack(anchor="w")
                self.checkbox_vars[column_name] = var

        # Update the "Select All" checkbox state based on the visible checkboxes
        self.update_select_all_checkbox()

    def update_select_all_checkbox(self):
        """Update the state of the Select All checkbox based on filtered checkboxes."""
        search_term = self.search_entry.get().lower()
        all_selected = True

        # Only check the visible (filtered) checkboxes
        for col, var in self.checkbox_vars.items():
            if search_term in col.lower():
                if var.get() == 0:  # If any visible checkbox is unchecked, all_selected becomes False
                    all_selected = False
                    break

        # Update the Select All checkbox based on the state of the visible checkboxes
        self.select_all_var.set(1 if all_selected else 0)
 
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
                # If this is the first submission, initialize the plot
                if not self.plot_initialized:
                    self.plot_columns(selected_columns, selected_index_column, self.file_directory)
                    self.plot_initialized = True
                else:
                    # Store current zoom limits if they exist
                    current_xlim = self.ax_primary.get_xlim()
                    current_ylim = self.ax_primary.get_ylim()

                    # Update the plot with new parameters
                    self.update_plot(selected_columns)

                    # Restore the zoom limits if the user has zoomed in
                    if current_xlim != self.ax_primary.get_xlim() or current_ylim != self.ax_primary.get_ylim():
                        self.ax_primary.set_xlim(current_xlim)
                        self.ax_primary.set_ylim(current_ylim)

                    self.fig.canvas.draw_idle()  # Refresh the canvas
        else:
            messagebox.showerror("Error", "Please select columns and an index column.")

 
    def plot_columns(self, selected_columns, index_column, file_directory):
        # Clear previous plots if necessary
        if self.fig:
            plt.close(self.fig)

        # Create a new figure and axes
        self.fig, self.ax_primary = plt.subplots(figsize=(10, 6))

        # Loop through selected columns and plot each
        for i, col in enumerate(selected_columns):
            for df in self.data_frames:
                # Ensure that index_column is numeric and usable for plotting
                x = df[index_column]  # Use the selected index column here
                y = df[col]
                if i == 0:  # Primary Y-axis
                    self.ax_primary.plot(x, y, label=col, color='blue')  # Primary line color
                    self.ax_primary.set_ylabel("Primary Y-axis Values")
                elif i == 1:  # Secondary Y-axis
                    self.ax_secondary = self.ax_primary.twinx()
                    self.ax_secondary.plot(x, y, label=col, color='orange')  # Secondary line color
                    self.ax_secondary.set_ylabel("Secondary Y-axis Values")
                elif i == 2:  # Tertiary Y-axis
                    self.ax_tertiary = self.ax_primary.twinx()
                    self.ax_tertiary.spines['right'].set_position(('outward', 60))  # Offset the tertiary axis
                    self.ax_tertiary.plot(x, y, label=col, color='green')  # Tertiary line color

        # Set labels and title
        self.ax_primary.set_xlabel(index_column)
        self.ax_primary.set_title("Data Plot")
        self.ax_primary.legend(loc='upper left')
        if self.ax_secondary:
            self.ax_secondary.legend(loc='upper right')
        if self.ax_tertiary:
            self.ax_tertiary.legend(loc='lower right')

        # Add interactive data cursors
        mplcursors.cursor(hover=True)

        # Create a canvas for the plot and pack it into the plot frame
        canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create a navigation toolbar for the plot
        toolbar = NavigationToolbar2Tk(canvas, self.plot_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Draw the canvas
        canvas.draw()

        # Connect the toolbar's 'home' button to reset zoom
        toolbar.home = lambda: (self.ax_primary.set_xlim(None), self.ax_primary.set_ylim(None),
                                self.ax_secondary.set_ylim(None) if self.ax_secondary else None,
                                self.ax_tertiary.set_ylim(None) if self.ax_tertiary else None)

    def update_plot(self, selected_columns):
        # Clear the current plot without resetting the figure
        self.ax_primary.cla()
        if self.ax_secondary:
            self.ax_secondary.cla()
        if self.ax_tertiary:
            self.ax_tertiary.cla()

        # Loop through selected columns and update existing plot
        for i, col in enumerate(selected_columns):
            for df in self.data_frames:
                # Ensure that the selected index column is usable for plotting
                x = df[self.index_column_dropdown.get()]  # Use the selected index column here
                y = df[col]
                if i == 0:  # Primary Y-axis
                    self.ax_primary.plot(x, y, label=col, color='blue')  # Primary line color
                    self.ax_primary.set_ylabel("Primary Y-axis Values")
                elif i == 1:  # Secondary Y-axis
                    if self.ax_secondary is None:
                        self.ax_secondary = self.ax_primary.twinx()
                    self.ax_secondary.plot(x, y, label=col, color='orange')  # Secondary line color
                    self.ax_secondary.set_ylabel("Secondary Y-axis Values")
                elif i == 2:  # Tertiary Y-axis
                    if self.ax_tertiary is None:
                        self.ax_tertiary = self.ax_primary.twinx()
                        self.ax_tertiary.spines['right'].set_position(('outward', 60))  # Offset the tertiary axis
                    self.ax_tertiary.plot(x, y, label=col, color='green')  # Tertiary line color

        # Set labels and title
        self.ax_primary.set_xlabel(self.index_column_dropdown.get())
        self.ax_primary.set_title("Updated Data Plot")
        self.ax_primary.legend(loc='upper left')
        if self.ax_secondary:
            self.ax_secondary.legend(loc='upper right')
        if self.ax_tertiary:
            self.ax_tertiary.legend(loc='lower right')

        # Redraw the canvas without affecting the zoom level
        self.fig.canvas.draw_idle()



 
# Create the application window
if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()

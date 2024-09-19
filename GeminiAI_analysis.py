import requests
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Replace with your actual API key
API_KEY = "AIzaSyBs2vcp1NhRUPWzNftzA-yGfw8orm5MdYA"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

# Function to query the Gemini API for the formula
def get_python_formula(requirement):
    data = {
        "contents": [
            {"parts": [{"text": f"Give only the Python function for finding the {requirement} of the column in excel or csv. Note: your response should only contain one word, which is the function."}]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        print("Response from Gemini API:", json.dumps(result, indent=4))
        # Extract the formula from the 'candidates' field
        if 'candidates' in result and len(result['candidates']) > 0:
            formula = result['candidates'][0]['content']['parts'][0]['text'].strip()
            print("formula--AI_prompt-->", formula)
            return formula
        else:
            return "Error: Unexpected response structure"

    else:
        return f"Error: {response.status_code} {response.text}"

# Function to load the file (Excel or CSV)
def load_file():
    # file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")])
    file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])

    if file_path:
        try:
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            else:
                data = pd.read_excel(file_path)
            return data, file_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            return None, None
    return None, None

# Function to apply the formula
def apply_formula(data, columns, requirement):
    try:
        # Get the formula from Gemini API
        formula = get_python_formula(requirement)
        print("Columns------->", columns)
        print("req-------->", requirement)
        if formula.startswith("Error"):
            result_textbox.insert(tk.END, f"Error: {formula}\n")
        else:
            # Display the formula
            result_textbox.insert(tk.END, f"Formula: {formula}\n")

            # Dynamically evaluate the formula for each selected column
            for column in columns:
                if column in data.columns:
                    result = eval(f"data['{column}'].{formula}()")
                    result_textbox.insert(tk.END, f"Result for {column}: {result}\n")
                else:
                    result_textbox.insert(tk.END, f"Error: Column '{column}' not found!\n")
    except Exception as e:
        result_textbox.insert(tk.END, f"Error executing formula: {e}\n")

# Function to update the listbox based on the search box
def update_listbox(event):
    search_term = search_entry.get().lower()
    listbox.delete(0, tk.END)
    for column in columns:
        if search_term in column.lower():
            listbox.insert(tk.END, column)

# Function to handle the load file button
def on_load_file():
    global data, file_path, columns
    data, file_path = load_file()
    if data is not None:
        columns = data.columns.tolist()
        listbox.delete(0, tk.END)
        for column in columns:
            listbox.insert(tk.END, column)
        messagebox.showinfo("Success", f"Loaded file: {file_path}")

# Function to handle the apply formula button
def on_apply_formula():
    selected_columns = [listbox.get(i) for i in listbox.curselection()]
    requirement = formula_entry.get()
    if data is not None and selected_columns:
        apply_formula(data, selected_columns, requirement)
    else:
        messagebox.showerror("Error", "No file loaded or no columns selected!")

# Tkinter UI setup
def create_ui():
    global listbox, search_entry, result_textbox, columns

    window = tk.Tk()
    window.title("Excel/CSV Analysis Tool with Gemini API")

    # Load file button
    load_button = tk.Button(window, text="Load File", command=on_load_file)
    load_button.grid(row=0, column=0, padx=10, pady=10)

    # Column search and listbox
    search_label = tk.Label(window, text="Search Columns:")
    search_label.grid(row=1, column=0, padx=10, pady=5)
    search_entry = tk.Entry(window, width=30)
    search_entry.grid(row=1, column=1, padx=10, pady=5)
    search_entry.bind("<KeyRelease>", update_listbox)

    listbox_frame = tk.Frame(window)
    listbox_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
    
    scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, height=10, width=50)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    # Requirement input (for example: max, min, sum, average)
    formula_label = tk.Label(window, text="Enter Requirement (e.g., max, min, sum, avg):")
    formula_label.grid(row=3, column=0, padx=10, pady=5)
    global formula_entry
    formula_entry = tk.Entry(window, width=30)
    formula_entry.grid(row=3, column=1, padx=10, pady=5)

    # Result Text Box
    global result_textbox
    result_textbox = tk.Text(window, height=15, width=50)
    result_textbox.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    # Apply formula button
    apply_button = tk.Button(window, text="Apply Formula", command=on_apply_formula)
    apply_button.grid(row=4, column=0, columnspan=2, pady=10)

    window.mainloop()

# Global variables
data = None
file_path = None
columns = []

# Start the UI
if __name__ == "__main__":
    create_ui()

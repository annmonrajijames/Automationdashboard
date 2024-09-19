import requests
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# Replace with your actual API key
API_KEY = "API_key"
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
        # formula = result['contents'][0]['parts'][0]['text'].strip()
        # Extract the formula from the 'candidates' field
        if 'candidates' in result and len(result['candidates']) > 0:
            formula = result['candidates'][0]['content']['parts'][0]['text'].strip()
            print("formulat--AI_prompt_------------>",formula)
            return formula
        else:
            return "Error: Unexpected response structure"

    else:
        return f"Error: {response.status_code} {response.text}"

# Function to load the file (Excel or CSV)
def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")])
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
def apply_formula(data, column_name, requirement):
    try:
        # Get the formula from Gemini API
        formula = get_python_formula(requirement)
        print("column name------->",column_name)
        print("req-------->",requirement)
        if formula.startswith("Error"):
            result_textbox.insert(tk.END, f"Error: {formula}\n")
        else:
            # Display the formula
            result_textbox.insert(tk.END, f"Formula: {formula}\n")

            # Dynamically evaluate the formula for the column
            result = eval(f"data['{column_name}'].{formula}()")
            result_textbox.insert(tk.END, f"Result: {result}\n")
    except Exception as e:
        result_textbox.insert(tk.END, f"Error executing formula: {e}\n")

# Tkinter UI setup
def create_ui():
    window = tk.Tk()
    window.title("Excel/CSV Analysis Tool with Gemini API")

    # Load file button
    load_button = tk.Button(window, text="Load File", command=lambda: on_load_file())
    load_button.grid(row=0, column=0, padx=10, pady=10)

    # Column name input
    column_label = tk.Label(window, text="Enter Column Name:")
    column_label.grid(row=1, column=0, padx=10, pady=5)
    column_entry = tk.Entry(window, width=30)
    column_entry.grid(row=1, column=1, padx=10, pady=5)

    # Requirement input (for example: max, min, sum, average)
    formula_label = tk.Label(window, text="Enter Requirement (e.g., max, min, sum, avg):")
    formula_label.grid(row=2, column=0, padx=10, pady=5)
    formula_entry = tk.Entry(window, width=30)
    formula_entry.grid(row=2, column=1, padx=10, pady=5)

    # Result Text Box
    global result_textbox
    result_textbox = tk.Text(window, height=15, width=50)
    result_textbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # Apply formula button
    apply_button = tk.Button(window, text="Apply Formula", command=lambda: on_apply_formula(data, column_entry.get(), formula_entry.get()))
    apply_button.grid(row=3, column=0, columnspan=2, pady=10)

    window.mainloop()

# Global variable to store the loaded data
data = None
file_path = None

# Function to load the file
def on_load_file():
    global data, file_path
    data, file_path = load_file()
    if data is not None:
        messagebox.showinfo("Success", f"Loaded file: {file_path}")

# Function to apply the formula to the selected column
def on_apply_formula(data, column_name, requirement):
    if data is not None and column_name in data.columns:
        apply_formula(data, column_name, requirement)
    else:
        messagebox.showerror("Error", "Invalid column name or no file loaded!")

# Start the UI
if __name__ == "__main__":
    create_ui()

import openai
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

# Set your OpenAI API key
OPENAI_API_KEY = 'enter openAI API key'
openai.api_key = OPENAI_API_KEY

# Function to handle OpenAI API query for Python code generation
def get_analysis_code(column_name, formula):
    try:
        # OpenAI API request for code suggestion based on user input
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are helping to analyze an Excel file. Generate Python code for the following task."},
                {"role": "user", "content": f"I have a column named '{column_name}' in an Excel or CSV file. Please generate a Python formula to calculate the '{formula}' for this column."}
            ]
        )
        generated_code = response['choices'][0]['message']['content']
        return generated_code
    except Exception as e:
        return f"Error: {e}"

# Function to read the file (Excel or CSV)
def load_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
    )
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

# Function to apply the generated code
def apply_formula(data, column_name, formula):
    try:
        # Send user input to OpenAI API and get generated code
        generated_code = get_analysis_code(column_name, formula)

        # Display the generated code in the result textbox
        result_textbox.delete(1.0, tk.END)
        result_textbox.insert(tk.END, f"Generated Code:\n{generated_code}\n")

        # Dynamically execute the code (you can also write it to a file for safety if needed)
        exec(generated_code)

    except Exception as e:
        result_textbox.insert(tk.END, f"Error executing formula: {e}")

# Tkinter UI setup
def create_ui():
    window = tk.Tk()
    window.title("Excel/CSV Analysis Tool with OpenAI")

    # File loading button
    load_button = tk.Button(window, text="Load File", command=lambda: on_load_file())
    load_button.grid(row=0, column=0, padx=10, pady=10)

    # Column name input
    column_label = tk.Label(window, text="Enter Column Name:")
    column_label.grid(row=1, column=0, padx=10, pady=5)
    column_entry = tk.Entry(window, width=30)
    column_entry.grid(row=1, column=1, padx=10, pady=5)

    # Formula input
    formula_label = tk.Label(window, text="Enter Formula:")
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

# Load file and store data globally
data = None
file_path = None
def on_load_file():
    global data, file_path
    data, file_path = load_file()
    if data is not None:
        messagebox.showinfo("Success", f"Loaded file: {file_path}")

# Apply formula on the column
def on_apply_formula(data, column_name, formula):
    if data is not None and column_name in data.columns:
        apply_formula(data, column_name, formula)
    else:
        messagebox.showerror("Error", "Invalid column name or no file loaded!")

# Start the UI
if __name__ == "__main__":
    create_ui()

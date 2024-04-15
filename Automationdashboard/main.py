import tkinter as tk
from tkinter import messagebox
import subprocess

def run_script():
    try:
        # Using subprocess to run the python file more safely
        completed_process = subprocess.run(['python', 'CodeForAutomation24AndPowerParameters_excel.py'], check=True, text=True, capture_output=True)
        messagebox.showinfo("Success", f"Script executed successfully!\n\nOutput:\n{completed_process.stdout}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Script execution failed!\n\nError:\n{e.stderr}")

# Create the main window
root = tk.Tk()
root.title("Script Runner")

# Create a button that will run the script when clicked
run_button = tk.Button(root, text="Run Script", command=run_script)
run_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()

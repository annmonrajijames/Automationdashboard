import tkinter as tk
from tkinter import messagebox, filedialog
import re
 
# Sample CAN matrix for demonstration purposes
CAN_MATRIX = {
    "0x18530902": {
        "parse_type": [0, 1, 2, 3, 4],  # Parse types for each byte
        # Add other metadata or byte meanings as needed
    },
    "0x14520902": {
        "parse_type": [0, 1],
    }
}
 
def hex_to_binary(hex_data):
    return [bin(int(byte, 16))[2:].zfill(8) for byte in hex_data]
 
def parse_byte(byte, parse_type):
    # Existing parsing logic here...
    pass
 
def process_trace_file():
    file_path = filedialog.askopenfilename(filetypes=[("Trace Files", "*.trc")])
    if not file_path:
        return
 
    with open(file_path, 'r') as file:
        lines = file.readlines()
 
    output_text.delete(1.0, tk.END)  # Clear previous output
 
    for line in lines:
        # Assuming the line format is: Time Identifier Data (e.g., "12.345 0x18530902 00 80 00 27 00 00 00 00")
        match = re.match(r'(\S+)\s+(\S+)\s+(.+)', line)
        if match:
            time, identifier, data = match.groups()
            if identifier in CAN_MATRIX:
                hex_data = data.split()
                # Process the identified bytes according to the CAN matrix
                output_text.insert(tk.END, f"Time: {time}, Identifier: {identifier}\n")
                binary_values = hex_to_binary(hex_data)
 
                for i, byte in enumerate(binary_values):
                    byte_value = int(hex_data[i], 16)
                    output_text.insert(tk.END, f"  Byte {i}: {byte} (Hex: {hex_data[i]})\n")
                    # Use the CAN matrix to get parse types
                    parse_type = CAN_MATRIX[identifier]["parse_type"][i]
                    parsed_flags = parse_byte(byte_value, parse_type)
                    output_text.insert(tk.END, f"  Parsed Flags for Byte {i}:\n")
                    for key, value in parsed_flags.items():
                        output_text.insert(tk.END, f"    {key.replace('_', ' ').title()}: {value}\n")
                output_text.insert(tk.END, "\n")
            else:
                output_text.insert(tk.END, f"Unknown Identifier: {identifier}\n")
 
# Create the main window
root = tk.Tk()
root.title("CAN Trace Parser")
 
# Create a button to load the trace file
load_button = tk.Button(root, text="Load Trace File", command=process_trace_file)
load_button.pack()
 
# Create a text widget to display the output
output_text = tk.Text(root, width=70, height=20)
output_text.pack()
 
root.mainloop()
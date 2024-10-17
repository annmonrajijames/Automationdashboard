import tkinter as tk
from tkinter import messagebox
 
def hex_to_binary(hex_data):
    return [bin(int(byte, 16))[2:].zfill(8) for byte in hex_data]
 
def parse_byte(byte, parse_type):
    binary_value = bin(byte)[2:].zfill(8)
 
    if parse_type == 0:  # Throttle percentage for Identifier 1
        throttle_percentage = (byte / 255) * 100
        return {
            "binary": binary_value,
            "throttle_percentage": throttle_percentage
        }
 
    elif parse_type == 1:  # Mode acknowledgment for Identifier 1
        mode_ack = byte & 0b00000111
        mode_mapping = {
            0x00: "Throttle Disabled (neutral)",
            0b100: "Eco Mode",
            0b010: "Normal Mode",
            0b001: "Power Mode",
            0b101: "Limp Mode",
            0b111: "Secure Mode"
        }
        return {
            "binary": binary_value,
            "mode_ack": mode_mapping.get(mode_ack, "Unknown mode"),
            "side_stand_ack": (byte >> 3) & 0b00000001,
            "direction": "Forward" if (byte >> 4) & 0b00000001 == 0 else "Reverse",
            "ride_ack": (byte >> 5) & 0b00000001,
            "hill_hold_enabled_ack": (byte >> 6) & 0b00000001,
            "wakeup_ack": (byte >> 7) & 0b00000001
        }
 
    elif parse_type == 2:  # Status flags for Byte 2
        return {
            "binary": binary_value,
            "motor_hall_input_abnormal": (byte >> 0) & 0b00000001,
            "motor_stalling": (byte >> 1) & 0b00000001,
            "motor_phase_loss": (byte >> 2) & 0b00000001,
            "controller_over_temperature": (byte >> 3) & 0b00000001,
            "motor_over_temperature": (byte >> 4) & 0b00000001,
            "throttle_error": (byte >> 5) & 0b00000001,
            "mosfet_protection": (byte >> 6) & 0b00000001,
            "reserved": (byte >> 7) & 0b00000001,
        }
 
    elif parse_type == 3:  # Status flags for Byte 3
        return {
            "binary": binary_value,
            "regenerative_braking": (byte >> 0) & 0b00000001,
            "mode_r_pulse": (byte >> 1) & 0b00000001,
            "mode_l_pulse": (byte >> 2) & 0b00000001,
            "brake_pulse": (byte >> 3) & 0b00000001,
            "park_pulse": (byte >> 4) & 0b00000001,
            "reverse_pulse": (byte >> 5) & 0b00000001,
            "side_stand_pulse": (byte >> 6) & 0b00000001,
            "forward_parking_mode_ack": (byte >> 7) & 0b00000001,
        }
 
    elif parse_type == 4:  # Status flags for Byte 4
        return {
            "binary": binary_value,
            "controller_overvoltage": (byte >> 0) & 0b00000001,
            "controller_undervoltage": (byte >> 1) & 0b00000001,
            "overcurrent_fault": (byte >> 2) & 0b00000001,
        }
 
    return {"binary": binary_value}  # Return binary for other parse types
 
def process_input():
    byte_string1 = entry1.get()
    byte_string2 = entry2.get()
   
    hex_data1 = byte_string1.split()
    hex_data2 = byte_string2.split()
 
    # Normalize input case and validate for identifier 1
    hex_data1 = [byte.upper() for byte in hex_data1]
    if len(hex_data1) != 8 or any(len(byte) != 2 or not all(c in '0123456789ABCDEF' for c in byte) for byte in hex_data1):
        messagebox.showerror("Input Error", "Invalid input for Identifier 1! Please enter exactly 8 valid 2-digit hex values.")
        return
 
    # Normalize input case and validate for identifier 2
    hex_data2 = [byte.upper() for byte in hex_data2]
    if len(hex_data2) != 8 or any(len(byte) != 2 or not all(c in '0123456789ABCDEF' for c in byte) for byte in hex_data2):
        messagebox.showerror("Input Error", "Invalid input for Identifier 2! Please enter exactly 8 valid 2-digit hex values.")
        return
 
    output_text.delete(1.0, tk.END)  # Clear previous output
 
    # Process Identifier 1 (0x18530902)
    output_text.insert(tk.END, "Processing Identifier 1 (0x18530902):\n")
    binary_values1 = hex_to_binary(hex_data1)
 
    for i, byte in enumerate(binary_values1):
        byte_value = int(hex_data1[i], 16)
        output_text.insert(tk.END, f"  Byte {i}: {byte} (Hex: {hex_data1[i]})\n")
 
        parsed_flags = parse_byte(byte_value, i)
        output_text.insert(tk.END, f"  Parsed Flags for Byte {i}:\n")
        for key, value in parsed_flags.items():
            output_text.insert(tk.END, f"    {key.replace('_', ' ').title()}: {value}\n")
 
        if i == 2:  # Additional details for Byte 2
            motor_phase_loss = parsed_flags["motor_phase_loss"]
            if motor_phase_loss:
                output_text.insert(tk.END, "    Note: Motor Phase Loss is ACTIVE.\n")
            else:
                output_text.insert(tk.END, "    Note: Motor Phase Loss is NOT ACTIVE.\n")
 
        if i == 3:  # Additional details for Byte 3
            mode_r_pulse = parsed_flags["mode_r_pulse"]
            if mode_r_pulse:
                output_text.insert(tk.END, "    Note: Mode R Pulse is ACTIVE.\n")
            else:
                output_text.insert(tk.END, "    Note: Mode R Pulse is NOT ACTIVE.\n")
 
        if i == 4:  # Additional details for Byte 4
            overcurrent_fault = parsed_flags["overcurrent_fault"]
            if overcurrent_fault:
                output_text.insert(tk.END, "    Note: Overcurrent Fault is ACTIVE.\n")
            else:
                output_text.insert(tk.END, "    Note: Overcurrent Fault is NOT ACTIVE.\n")
 
        output_text.insert(tk.END, "\n")
 
    # Process Identifier 2 (0x14520902)
    output_text.insert(tk.END, "Processing Identifier 2 (0x14520902):\n")
    binary_values2 = hex_to_binary(hex_data2)
 
    for i, byte in enumerate(binary_values2):
        byte_value = int(hex_data2[i], 16)
        output_text.insert(tk.END, f"  Byte {i}: {byte} (Hex: {hex_data2[i]})\n")
 
        # Only process bytes 0 and 1 for motor speed calculation
        if i == 0 or i == 1:
            parsed_flags = {"binary": byte}
            output_text.insert(tk.END, f"  Parsed Flags for Byte {i}:\n")
            for key, value in parsed_flags.items():
                output_text.insert(tk.END, f"    {key.replace('_', ' ').title()}: {value}\n")
            output_text.insert(tk.END, "\n")
 
    # Calculate motor speed for Identifier 2
    if len(hex_data2) >= 2:
        motor_speed_byte0 = int(hex_data2[0], 16)
        motor_speed_byte1 = int(hex_data2[1], 16)
       
        # Reverse the bytes and concatenate
        motor_speed = motor_speed_byte1 * 100 + motor_speed_byte0
        output_text.insert(tk.END, f"  Motor Speed: {motor_speed} RPM\n")
 
# Create the main window
root = tk.Tk()
root.title("Hex to Binary Parser")
 
# Create a label and entry for input for Identifier 1
label1 = tk.Label(root, text="Enter 8 hex values for 0x18530902 (e.g., 00 80 00 27 00 00 00 00):")
label1.pack()
entry1 = tk.Entry(root, width=50)
entry1.pack()
 
# Create a label and entry for input for Identifier 2
label2 = tk.Label(root, text="Enter 8 hex values for 0x14520902 (e.g., 20 23 00 00 00 00 00 00):")
label2.pack()
entry2 = tk.Entry(root, width=50)
entry2.pack()
 
# Create a button to process the input
button = tk.Button(root, text="Parse", command=process_input)
button.pack()
 
# Create a text widget to display the output
output_text = tk.Text(root, width=70, height=20)
output_text.pack()
 
 
root.mainloop()
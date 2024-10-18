import tkinter as tk
import winsound

# Set up the main application window
root = tk.Tk()
root.title("Basic Tkinter Window")

# Set up the canvas
width, height = 800, 600
canvas = tk.Canvas(root, width=width, height=height, bg="black")
canvas.pack()

# Define rectangle properties
rect_color = "blue"
rect_x, rect_y = 50, 50
rect_width, rect_height = 60, 60
rect_speed_x, rect_speed_y = 5, 5

# Create the rectangle
rect = canvas.create_rectangle(rect_x, rect_y, rect_x + rect_width, rect_y + rect_height, fill=rect_color)

# Function to update the rectangle's position
def update_rectangle():
    global rect_x, rect_y, rect_speed_x, rect_speed_y

    # Move the rectangle
    rect_x += rect_speed_x
    rect_y += rect_speed_y

    # Bounce the rectangle off the edges and play sound
    if rect_x < 0 or rect_x + rect_width > width:
        rect_speed_x = -rect_speed_x
        winsound.Beep(1000, 100)  # Frequency 1000 Hz, Duration 100 ms
    if rect_y < 0 or rect_y + rect_height > height:
        rect_speed_y = -rect_speed_y
        winsound.Beep(1000, 100)  # Frequency 1000 Hz, Duration 100 ms

    # Update the rectangle's position on the canvas
    canvas.coords(rect, rect_x, rect_y, rect_x + rect_width, rect_y + rect_height)

    # Schedule the next update
    root.after(30, update_rectangle)

# Start the update loop
update_rectangle()

# Run the application
root.mainloop()
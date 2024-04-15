import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
   
def choose_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        # folder_entry.delete(0, tk.END)
        # folder_entry.insert(0, folder_path)
        print(folder_path)
 
def on_select(value):
    print("Selected:", value)
 
def on_radio_select():
    selection = radio_var.get()
    print("Selected:", selection)
 
def on_checkbox_click():
    print("Selected options:")
    for index, option in enumerate(checkbox_vars):
        if option.get():
            print(f"Option {index + 1}")
 
# def on_checkbox_click():
#     if checkbox_var.get():
#         print("Checkbox is checked")
#     else:
#         print("Checkbox is unchecked")
 
 
root = tk.Tk()
radio_var = tk.StringVar()
# checkbox_var = tk.BooleanVar()
checkbox_vars = []
 
 
padded_frame = tk.Frame(root, padx=20, pady=15, borderwidth=2)
padded_frame.configure(bg="lightblue")
root.configure(bg="#7b7b7f")
 
padded_frame.pack(fill="both", expand=True)  # Optional: Fill remaining space
 
# defining dropOptions for the drop down
dropOptions = ["Daily Report", "Error Protection", "Battery Cycler"]
radioOptions = ["Option 1", "Option 2", "Option 3", "Option 4"]
checkbox_texts = ["Option 1", "Option 2", "Option 3", "Option 1", "Option 2", "Option 3", "Option 1", "Option 2", "Option 3", "Option 1", "Option 2", "Option 3", "Option 1",
                  "Option 2", "Option 3", "Option 1", "Option 2", "Option 3", "Option 1", "Option 2", "Option 3", "Option 1", "Option 2", "Option 3", "Option 1", "Option 2", "Option 3"]
 
radio_var.set(radioOptions[0])
 
root.title("SpikeBot")
label = tk.Label(padded_frame, text='Select the folder :----------',
                 background="lightblue").grid(row=0, column=0, pady=10)
choose_button = tk.Button(padded_frame, text="Choose Folder", command=choose_folder).grid(row=0, column=1, pady=10)
 
selected_option = tk.StringVar(root)
selected_option.set(dropOptions[0])  # set the default option
 
# Create the dropdown menu
label = tk.Label(padded_frame, text='Select the analysis to be performed :-',
                 background="lightblue").grid(row=1, column=0)
dropdown = tk.OptionMenu(padded_frame, selected_option,
                         *dropOptions, command=on_select).grid(row=1, column=1)
 
 
# choose_button = tk.Button(root, text="Choose Folder", command=choose_folder)
# choose_button.pack()
v = tk.StringVar()
 
# tk.Button(root, text='Generate and download report',
#           bg="#3d76bf", fg="white").pack()
 
# folder_entry = tk.Entry(root, width=40)
# folder_entry.pack(pady=(0, 10))
root.mainloop()
import pandas as pd

def calculate_mode_percentage(file_path):
    # Load the CSV file
    data = pd.read_csv(file_path)
    
    # Ensure the 'Mode_Ack_408094978' column is present
    if 'Mode_Ack_408094978' not in data.columns:
        print("Column 'Mode_Ack_408094978' is missing from the data.")
        return
    
    # Count the occurrences of each mode and calculate the percentage
    mode_counts = data['Mode_Ack_408094978'].value_counts(normalize=True) * 100
    
    # Print the results
    for mode, percentage in mode_counts.items():
        print(f"Mode {mode}: {percentage:.2f}%")

# Define the path to the CSV file
file_path = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\master\accessories\Mar-23\Battery_4\log_withoutanomaly.csv"

# Call the function
calculate_mode_percentage(file_path)

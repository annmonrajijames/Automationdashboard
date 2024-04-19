import pandas as pd
 
# Define the paths for input and output
input_file_path = r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\log.csv'
output_file_path = r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\filtered_log.csv'
# Load the data
data = pd.read_csv(input_file_path)
 
# Convert 'localtime' column to datetime
data['localtime'] = pd.to_datetime(data['localtime'], format='%d/%m/%Y %H:%M:%S.%f')
 
# Sample input simulation (You will replace these with actual user inputs or logic to handle absence of inputs)
start_time = "30-03-2024 14:23:31"  # Replace None with user input if available
end_time = "30-03-2024 14:23:33"    # Replace None with user input if available
 
# Determine start_time and end_time based on user input or default to first and last entry
if start_time is None:
    start_time = data['localtime'].iloc[-1]  # Most recent time if no start_time provided
if end_time is None:
    end_time = data['localtime'].iloc[0]    # Oldest time if no end_time provided
 
# Filter the data
filtered_data = data[(data['localtime'] >= start_time) & (data['localtime'] <= end_time)]
 
filtered_data.to_csv(output_file_path, index=False)
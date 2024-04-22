import pandas as pd

# Define the paths for input and output
input_file_path = r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\log.csv'
output_file_path = r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\filtered_log.csv'

# Load the data
data = pd.read_csv(input_file_path)

# Convert 'localtime' column to datetime
data['localtime'] = pd.to_datetime(data['localtime'], format='%d/%m/%Y %H:%M:%S.%f')

# Sample input simulation (You will replace these with actual user inputs or logic to handle absence of inputs)
start_time = "30-03-2024 14:23:31" 
end_time = None 

# Convert input strings to datetime if they are not None
if start_time is not None:
    start_time = pd.to_datetime(start_time, format='%d-%m-%Y %H:%M:%S')
else:
    start_time = data['localtime'].min()  # Use the earliest time if no start_time provided

if end_time is not None:
    end_time = pd.to_datetime(end_time, format='%d-%m-%Y %H:%M:%S')
else:
    end_time = data['localtime'].max()    # Use the latest time if no end_time provided

# Filter the data
filtered_data = data[(data['localtime'] >= start_time) & (data['localtime'] <= end_time)]

# Save the filtered data to CSV
filtered_data.to_csv(output_file_path, index=False)
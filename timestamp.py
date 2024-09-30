import pandas as pd
import os

# Load the CSV file
df = pd.read_csv(r'C:\Users\kamalesh.kb\Downloads\data.csv')

# Assuming the DATETIME column is named 'DATETIME'
df['DATETIME'] = pd.to_datetime(df['DATETIME'], unit='s')  # Convert to datetime from seconds

# Add 5 hours and 30 minutes to each timestamp
df['DATETIME'] = df['DATETIME'] + pd.to_timedelta('5h30m')

# Format the DATETIME to your desired format
df['formatted_timestamp'] = df['DATETIME'].dt.strftime('%H:%M:%S')  # Example: HH:MM:SS

# Get the directory of the input file
input_file_dir = os.path.dirname(r'C:\Users\kamalesh.kb\Downloads\data.csv')

# Save the modified DataFrame to a new CSV file in the same directory
output_file = os.path.join(input_file_dir, 'output.csv')
df.to_csv(output_file, index=False)

import pandas as pd
from datetime import datetime, timedelta

# Load your data
file_path = r'C:\Users\kamalesh.kb\Influx_master\Influx_enduro\aug_7\r1_speed_notShown\log.csv'  # Update with your actual file path
data = pd.read_csv(file_path)

# Enter the start time
start_time_str = '06:13:00'  # Update this with your actual start time
start_time = datetime.strptime(start_time_str, '%H:%M:%S')

# Function to convert fractional seconds to hh:mm:ss format
def convert_to_hhmmss(row, start_time):
    # Calculate the time in seconds
    seconds = row['Time'] 
    # Add these seconds to the start time
    new_time = start_time + timedelta(seconds=seconds)
    print(new_time)
    # Return the time in hh:mm:ss format
    return new_time.strftime('%H:%M:%S')

# Apply the function to create a new column
data['FormattedTime'] = data.apply(convert_to_hhmmss, start_time=start_time, axis=1)

# Save the modified DataFrame if needed
data.to_csv('path_to_your_output_csv_file.csv', index=False)

print(data.head())
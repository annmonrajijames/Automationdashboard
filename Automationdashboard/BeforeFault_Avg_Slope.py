import pandas as pd

# Load the CSV file into a pandas DataFrame
csv_file = 'log 1.csv'  # Adjust the path as necessary
data = pd.read_csv(csv_file)

# Convert 'localtime' column to datetime format, specifying dayfirst=True
data['localtime'] = pd.to_datetime(data['localtime'], dayfirst=True)

# Example fault_timestamp, replace this with the actual timestamp you're analyzing
fault_timestamp = data['localtime'].iloc[0]

# Calculate start time (5 minutes before the fault)
start_time = fault_timestamp - pd.Timedelta(minutes=5)

# Filter data to get rows exactly at start_time and fault_timestamp
# It might be necessary to adjust this to get the nearest available timestamps if exact matches are not present
start_temp = data.loc[data['localtime'] == start_time, 'MCU_Temperature_408094979'].iloc[0]
fault_temp = data.loc[data['localtime'] == fault_timestamp, 'MCU_Temperature_408094979'].iloc[0]

# Calculate the time difference in seconds
time_difference_seconds = (fault_timestamp - start_time).total_seconds()

# Calculate the slope (rate of change) of MCU_Temperature_408094979
if time_difference_seconds > 0:
    slope = (fault_temp - start_temp) / time_difference_seconds
    print("Slope of MCU_Temperature_408094979 between start_time and fault_timestamp:", slope, "degrees per second")
else:
    print("Time difference is zero or negative, cannot calculate slope.")

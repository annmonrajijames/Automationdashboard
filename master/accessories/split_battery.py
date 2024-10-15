import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Assuming 'df' is your dataframe with SOC data
df = pd.read_csv(r'C:\Users\kamalesh.kb\PAVE\PAVE_Aug\31_8\log.csv')
folder_path = r'C:\Users\kamalesh.kb\PAVE\PAVE_Aug\31_8'

# Set the threshold for detecting battery change
threshold = 35  # Example threshold value, adjust as needed

# Convert 'DATETIME' column to datetime objects
# df['DATETIME'] = pd.to_datetime(df['DATETIME'])

if 'DATETIME' not in df.columns:                                                                       #if 'DATETIME' not in column Present 
            # start_time_str = '01-08-24 14:16:00'  # Update this with your actual start time
            start_time_str = df['Creation Time'].iloc[0]  # Update this with your actual start time
            # Parse the time, defaulting to ":00" if seconds are missing
            start_time = datetime.strptime(start_time_str, '%d-%m-%y %H:%M')
            print("Start_time--->",start_time)



            

            # Function to convert fractional seconds to hh:mm:ss format
            def convert_to_hhmmss(row, start_time):
                # Calculate the time in seconds
                seconds = row['Time'] 
                # Add these seconds to the start time
                new_time = start_time + timedelta(seconds=seconds)
                # Return the time in 'dd-mm-yy hh:mm:ss' format
                return new_time.strftime('%d-%m-%y %H:%M:%S')

            # Apply the function to create a new column
            df['DATETIME'] = df.apply(convert_to_hhmmss, start_time=start_time, axis=1)

            df['DATETIME'] = pd.to_datetime(df['DATETIME'])


            df = df.dropna(subset=['DATETIME'])
        
            df['DATETIME'] = pd.to_datetime(df['DATETIME'], unit='s')
        

            df['DATETIME'] = pd.to_datetime(df['DATETIME'])

# Interpolate NaN values in SOC [SA: 08] column
df['SOC [SA: 08]'] = df['SOC [SA: 08]'].interpolate(method='linear', limit_direction='both')

# Initialize battery_end_index and battery_number
battery_end_index = 0
battery_number = 1
anomaly_window = 40
Time_window = 60

# Start from the leftmost end of the dataframe
i = 2
# Initialize the index of the last battery change
last_battery_change_index = 0
excelStartTime_index = 1

t2_index = 1  # to avoid the while loop entering into an infinite loop
# Find the last non-NaN index of the SOC_8 column
last_valid_index = df['SOC [SA: 08]'].last_valid_index()

last_Valid_time = df['DATETIME'].iloc[last_valid_index]


# Iterate over the dataframe in steps of 60 seconds
while i < len(df) and t2_index > 0:
    t1 = df.iloc[i]['DATETIME']
    # print("t1:", t1)
    print("i:", i)
    t2 = t1 + pd.Timedelta(seconds=Time_window)  # t2 is 60 seconds later than t1

    # Find the index of t2
    t2_index = df[df['DATETIME'] >= t2].index.min()

    if pd.isna(t2_index):
        # Find the nearest index
        nearest_index = df['DATETIME'].sub(t2).abs().idxmin()
        t2_index = nearest_index

    if abs(df.iloc[i]['SOC [SA: 08]'] - df.iloc[t2_index]['SOC [SA: 08]']) > threshold or t2_index == len(df) - 1:
        # Print the time when battery change occurred (using t1 as it's the most recent timestamp)
        print("Battery changed at:", t1)

        # Adjust end time to remove 40 seconds after t2_index
        end_time = df.iloc[t2_index]['DATETIME']
        end_time = end_time - pd.Timedelta(seconds=anomaly_window)
        end_time_index = df[df['DATETIME'] <= end_time].index.max()

        battery_data = df.iloc[excelStartTime_index:end_time_index].copy()  # Data from the last battery change to the current battery change

        # Create a folder for each battery
        folder_name = f'Battery_{battery_number}'
        os.makedirs(os.path.join(folder_path, folder_name), exist_ok=True)

        # Save the battery data to a new CSV file inside the folder
        battery_data.to_csv(os.path.join(folder_path, folder_name, f'log.csv'), index=False)

        # Update battery end index and battery number
        battery_end_index = i
        battery_number += 1

        # Update the index of the last battery change
        last_battery_change_index = i + 1

        # Move to the next window (t1 becomes t2 for the next iteration)
        i = t2_index

        start_time = t2 + pd.Timedelta(seconds=anomaly_window)
        start_time_index = df[df['DATETIME'] <= start_time].index.max()
        if pd.isna(start_time_index):
            nearest_index = (df['DATETIME'] - start_time).abs().idxmax()
            start_time = df.iloc[nearest_index]['DATETIME']
            start_time_index = nearest_index
        excelStartTime_index = start_time_index

    if i == len(df) - 1 or i == last_valid_index or t1 == last_Valid_time or t2 == last_Valid_time: 
        print('loop broken')
        break

    else:
        # Move to the next window
        i = t2_index
        

    
import pandas as pd
import os

# Assuming 'df' is your dataframe with SOC data
df = pd.read_csv(r'C:\Users\kamalesh.kb\CodeForAutomation\OneDayData\B4_30_03_24\log_file.csv')
folder_path= r'C:\Users\kamalesh.kb\CodeForAutomation\OneDayData\B4_30_03_24'

# Set the threshold for detecting battery change
threshold = 40  # Example threshold value, adjust as needed

# Convert 'localtime' column to datetime objects
df['localtime'] = pd.to_datetime(df['localtime'])

# Initialize battery_end_index and battery_number
battery_end_index = 0
battery_number = 1
anomaly_window= 40
Time_window=60

# Start from the leftmost end of the dataframe
i = 2
# Initialize the index of the last battery change
last_battery_change_index = 0
excelStartTime_index= 1

t2_index = 1  # to avoid the while loop entering into an infinite loop

# Iterate over the dataframe in steps of 60 seconds
while i < len(df) and t2_index > 0:
    t1 = df.iloc[i]['localtime']
    t2 = t1 + pd.Timedelta(seconds=Time_window)  # t2 is 60 seconds later than t1
    print("t1----------->",t1,"t2------------>",t2)

    # Find the index of t2
    t2_index = df[df['localtime'] >= t2].index.min()

    if pd.isna(df.iloc[t2_index]['SOC_8']):
        # Find the nearest index with a valid SOC_8 value after t2_index
        nearest_index = (df['localtime'] > df.iloc[t2_index]['localtime']) & (~df['SOC_8'].isna())
        nearest_index = nearest_index.idxmax()

        # Check if there is any valid SOC_8 value after t2_index
        if not pd.isna(df.iloc[nearest_index]['SOC_8']):
            next_soc_index = nearest_index
            print("Nearest valid SOC after NaN at t2_index:", df.iloc[next_soc_index]['SOC_8'])
            t2_index= next_soc_index
        else:
            # If there are no valid SOC values after t2_index, we cannot proceed with battery change detection
            print("Error: No valid SOC value found after t2_index.")
            continue  # Skip to the next iteration of the loop

    print("t1_index---------->",i,"t2_index----------->",t2_index)
    # Check if SOC difference is greater than the threshold
       # Check if SOC_8 at t1 is NaN
    # if pd.isna(df.iloc[i]['SOC_8']):
    #     # Find the next few rows with valid SOC_8 values
    #     next_soc_index = df.iloc[i + 1: t2_index]['SOC_8'].first_valid_index()

    # if pd.isna(df.iloc[t2_index]['SOC_8']):
    # # Find the next few rows with valid SOC_8 values
    #     next_soc_index = df.iloc[t2_index + 1:]['SOC_8'].first_valid_index()
    #     print("SOC-nan---------->",df.iloc[t2_index]['SOC_8'])
    
    # print("df.iloc[i]['SOC_8']------------>",abs(df.iloc[i]['SOC_8']))
    # print("df.iloc[t2_index]['SOC_8']------------>",abs(df.iloc[t2_index]['SOC_8']))


    print("SOC difference----------->",abs(df.iloc[i]['SOC_8'] - df.iloc[t2_index]['SOC_8']))
    
    
    
    if abs(df.iloc[i]['SOC_8'] - df.iloc[t2_index]['SOC_8']) > threshold or t2_index>(len(df)-200):
        # Print the time when battery change occurred (using t1 as it's the most recent timestamp)
        print("Battery changed at:", t1)

        # start_time = t1 - pd.Timedelta(seconds=anomaly_window)
        # start_time_index = df[df['localtime'] <= start_time].index.min()
        # print("start_time_index--------->",start_time_index)
        # # If start_time_index is NaN, find the nearest index to start_time
        # if pd.isna(start_time_index):
        #     nearest_index = (df['localtime'] - start_time).abs().idxmin()
        #     start_time = df.iloc[nearest_index]['localtime']
        #     start_time_index = nearest_index

        # last_battery_change_time = df.iloc[last_battery_change_index]['localtime']
        # end_time = last_battery_change_time + pd.Timedelta(seconds=anomaly_window)
        # end_time_index = df[df['localtime'] >= end_time].index.min()
        # print("end_time_index--------->",end_time_index)
        # # If end_time_index is NaN, find the nearest index to end_time
        # if pd.isna(end_time_index):
        #     nearest_index = (df['localtime'] - end_time).abs().idxmin()
        #     end_time = df.iloc[nearest_index]['localtime']
        #     end_time_index = nearest_index
        print("excelStartTime_index--->",excelStartTime_index,"excelendTime_index---->",t2_index)
        battery_data = df.iloc[excelStartTime_index:t2_index].copy()  # Data from the last battery change to the current battery change

        # Create a folder for each battery
        folder_name = f'Battery_{battery_number}'
        os.makedirs(os.path.join(folder_path, folder_name), exist_ok=True)

        # Save the battery data to a new CSV file inside the folder
        battery_data.to_csv(os.path.join(folder_path, folder_name, f'log_file.csv'), index=False)
        print("Folder and Excel file for Battery", battery_number, "generated----------------->")
        print("Excel file for", battery_number, "generated----------------->")

        # Update battery end index and battery number
        battery_end_index = i
        battery_number += 1

        # Update the index of the last battery change
        last_battery_change_index = i + 1

        # Move to the next window (t1 becomes t2 for the next iteration)
        i = t2_index
        excelStartTime_index=t2_index 

    else:
        # Move to the next window
        i = t2_index

    if t2_index>(len(df)-200):
        break

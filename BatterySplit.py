import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplcursors  # Import mplcursors
 
# Assuming 'df' is your dataframe with SOC data
df = pd.read_csv(r'C:\Users\kamalesh.kb\CodeForAutomation\BB4\OUTPUT_1\Mar-28\log_file.csv')
folder_path= r'C:\Users\kamalesh.kb\CodeForAutomation\BB4\OUTPUT_1\Mar-28'
 
def adjust_current(row):
    adjust_current.zero_count = getattr(adjust_current, 'zero_count', 0)
    if row['MotorSpeed_340920578'] == 0:
        adjust_current.zero_count += 1
    else:
        adjust_current.zero_count = 0
   
    if adjust_current.zero_count >= 10:
        return 0
    else:
        return row['PackCurr_6']
   
 
 
def plot_ghps(data,folder_name):
    # data = pd.read_csv(r"C:\Users\kamalesh.kb\CodeForAutomation\MAIN_FOLDER\MAR_21\log_file.csv")
 
    # Apply the adjustment function to the DataFrame
 
    # data['localtime'] = pd.to_datetime(data['localtime'], format='%d/%m/%Y %H:%M:%S.%f', dayfirst=True)
    data['localtime'] = pd.to_datetime(data['localtime'])
    data.set_index('localtime', inplace=True)
    data['PackCurr_6'] = data.apply(adjust_current, axis=1)
   
    # Create a figure and axes for plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))
 
    # Plot 'PackCurr_6' on primary y-axis
    line1, = ax1.plot(data.index, -data['PackCurr_6'], color='blue', label='PackCurr_6')
    ax1.set_ylabel('Pack Current (A)', color='blue')
    ax1.yaxis.set_label_coords(-0.1, 0.7)  # Adjust label position
 
    # Create secondary y-axis for 'MotorSpeed_340920578' (RPM)
    ax2 = ax1.twinx()
    line2, = ax2.plot(data.index, data['MotorSpeed_340920578'], color='green', label='Motor Speed')
    ax2.set_ylabel('Motor Speed (RPM)', color='green')
 
    # Add 'AC_Current_340920579' to primary y-axis
    line3, = ax1.plot(data.index, data['AC_Current_340920579'], color='lightgray', label='AC Current')
 
    # Add 'AC_Voltage_340920580' scaled to 10x to the left side y-axis
    line4, = ax1.plot(data.index, data['AC_Voltage_340920580'] * 10, color='lightgray', label='AC Voltage (x10)')
 
    # Add 'Throttle_408094978' to the left side y-axis
    line5, = ax1.plot(data.index, data['Throttle_408094978'], color='lightgray', label='Throttle (%)')
 
        # Add 'Throttle_408094978' to the left side y-axis
    line6, = ax1.plot(data.index, data['SOC_8'], color='red', label='SOC (%)')
 
    # Hide the y-axis label for 'AC_Current_340920579'
    ax1.get_yaxis().get_label().set_visible(False)
 
    # Set x-axis label and legend
    ax1.set_xlabel('Local Time')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
 
    # Add a title to the plot
    plt.title('Battery Pack, Motor Data, and Throttle')
 
    # Format x-axis ticks as hours:minutes:seconds
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
 
    # Set grid lines lighter
    ax1.grid(True, linestyle=':', linewidth=0.5, color='gray')
    ax2.grid(True, linestyle=':', linewidth=0.5, color='gray')
 
    # Enable cursor to display values on graphs
    mplcursors.cursor([line1, line2, line3, line4, line5])
 
    # Save the plot as an image or display it
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    # plt.savefig('graph.png')  # Save the plot as an image
    subfolder_path = os.path.join(folder_path, folder_name)
    os.makedirs(subfolder_path, exist_ok=True)
    plt.savefig(os.path.join(subfolder_path, 'graph.png'))  # Save the plot as an image in the specified directory
    plt.show()
 
 
 
 
# Set the threshold for detecting battery change
threshold = 35  # Example threshold value, adjust as needed
 
# Convert 'localtime' column to datetime objects
df['localtime'] = pd.to_datetime(df['localtime'])
# # Interpolate NaN values in SOC_8 column
df['SOC_8'] = df['SOC_8'].interpolate(method='linear', limit_direction='both')
 
 
 
 
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
 
# Initialize variables to track consecutive occurrences and time duration
consecutive_nan_or_less_than_10 = 0
nan_or_less_than_10_start_time = None
# Initialize variables to track the start and end of the interval
start_time = None
end_time = None
drop_indices = []
 
 
 
 
# Initialize start_time and a flag to track if the condition is met
start_time = None
condition_met = False
 
# # Iterate over the DataFrame rows
# for index, row in df.iterrows():
#     # Step 1: Create t1 and t2
#     if start_time is None:
#         t1 = row['localtime']
#         t2 = t1 + pd.Timedelta(minutes=5)
#         start_time = t1
#     # Step 2: Check if motor speed is NaN or less than 1 between t1 and t2 consistently
#     if t1 <= row['localtime'] <= t2:
#         if not (np.isnan(row['MotorSpeed_340920578']) or row['MotorSpeed_340920578'] < 10):
#             # Reset start_time and flag and move to the next window
#             start_time = None
#             condition_met = False
#         else:
#             # Check if the condition is met for the entire window
#             if row['localtime'] == t2:
#                 condition_met = True
#     else:
#         # If the condition is met for the entire window, set SOC to 0 for all indices in the window
#         if condition_met:
 
#             df.loc[(df['localtime'] >= t1) & (df['localtime'] < t2), 'SOC_8'] = 0
 
#             print("time", start_time,t2)
#         # Reset start_time and flag and move to the next window
#         start_time = None
#         condition_met = False
# # Drop the rows from the DataFrame
# # df = df.drop(drop_indices)
# # print(drop_indices)
 
 
 
 
# Iterate over the dataframe in steps of 60 seconds
while i < len(df) and t2_index > 0:
    t1 = df.iloc[i]['localtime']
 
 
    t2 = t1 + pd.Timedelta(seconds=Time_window)  # t2 is 60 seconds later than t1
    # print("t1----------->",t1,"t2------------>",t2)
   
 
    # Find the index of t2
    t2_index = df[df['localtime'] >= t2].index.min()
   
 
 
 
    if pd.isna(t2_index):
    # Find the nearest index
        print("nan value detected")
        nearest_index = df['localtime'].sub(t2).abs().idxmin()
        print("t2_index is NaN. Nearest index:", nearest_index)
        t2_index= nearest_index
 
   
    # if abs(df.iloc[i]['SOC_8'] - df.iloc[t2_index]['SOC_8']) > threshold or t2_index>(len(df)-500):
    if abs(df.iloc[i]['SOC_8'] - df.iloc[t2_index]['SOC_8']) > threshold or t2_index == len(df)-1:
        # Print the time when battery change occurred (using t1 as it's the most recent timestamp)
        print("Battery changed at:", t1)
 
        # Adjust end time to remove 40 seconds after t2_index
        end_time = df.iloc[t2_index]['localtime']
        end_time = end_time - pd.Timedelta(seconds=anomaly_window)
        end_time_index = df[df['localtime'] <= end_time].index.max()
 
 
        # battery_data = df.iloc[start_time_index:end_time_index].copy()  # Data within the adjusted time window
 
 
 
##################
        print("time: ",end_time)
        print("index: ", excelStartTime_index,end_time_index)
        battery_data = df.iloc[excelStartTime_index:end_time_index].copy()  # Data from the last battery change to the current battery change
       
 
        # Create a folder for each battery
        folder_name = f'Battery_{battery_number}'
        os.makedirs(os.path.join(folder_path, folder_name), exist_ok=True)
       
 
       
        plot_ghps(battery_data,folder_name)
 
 
 
 
 
                # Save the battery data to a new CSV file inside the folder
       # battery_data['localtime'] = battery_data.index  # Add 'localtime' column using DataFrame index
       # battery_data.to_csv(os.path.join(folder_path, folder_name, f'log_file.csv'), index=False)  # Save DataFrame to CSV with 'localtime'
 
 
        # Save the battery data to a new CSV file inside the folder
        battery_data.to_csv(os.path.join(folder_path, folder_name, f'log_file.csv'), index=False)
        # print("Folder and Excel file for Battery", battery_number, "generated----------------->")
        # print("Excel file for", battery_number, "generated----------------->")
       
       
 
 
        # Update battery end index and battery number
        battery_end_index = i
        battery_number += 1
 
        # Update the index of the last battery change
        last_battery_change_index = i + 1
 
        # Move to the next window (t1 becomes t2 for the next iteration)
        i = t2_index
       
        start_time = t2 + pd.Timedelta(seconds=anomaly_window)
        start_time_index = df[df['localtime'] <= start_time].index.max()
        if pd.isna(start_time_index):
            nearest_index = (df['localtime'] - start_time).abs().idxmax()
            start_time = df.iloc[nearest_index]['localtime']
            start_time_index = nearest_index
        excelStartTime_index=start_time_index
 
    else:
        # Move to the next window
        i = t2_index
 
    if i==len(df)-1:
        break
 
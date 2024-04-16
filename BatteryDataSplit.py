import pandas as pd
import os



# Assuming 'df' is your dataframe with SOC data
df = pd.read_csv(r'C:\Users\kamalesh.kb\CodeForAutomation\Automationdashboard\Automationdashboard\MAIN_FOLDER\Automation_Dashboard_Batterywise\OneDayData\B4_30_03_24\log_file.csv')
folder_path= r'C:\Users\kamalesh.kb\CodeForAutomation\Automationdashboard\Automationdashboard\MAIN_FOLDER\Automation_Dashboard_Batterywise\OneDayData\B4_30_03_24'

# Set the threshold for detecting battery change
threshold = 40  # Example threshold value, adjust as needed

# Convert 'localtime' column to datetime objects
df['localtime'] = pd.to_datetime(df['localtime'])

# Initialize battery_end_index and battery_number
battery_end_index = 0
battery_number = 1
anomaly_window= 40
Time_window=60



# Start from the rightmost end of the dataframe
i = len(df) - 1
# Initialize the index of the last battery change
last_battery_change_index = len(df) - 1

t2_index=1      #to avoid the while loop enter into the infinite loop

# Iterate over the dataframe in steps of 60 seconds
while i >= 0 and t2_index >0:
    t1 = df.iloc[i]['localtime']
    t2 = t1 + pd.Timedelta(seconds=Time_window)  # t2 is 60 seconds earlier than t1
    # print("t1---------->: ",t1,"t2---------->: ",t2)

    # Find the index of t2
    t2_index = df[df['localtime'] <= t2].index.min()
    
    print(i,t2_index)
    # If t2_index is NaN, find the nearest index to t2
    if pd.isna(t2_index):
        nearest_index = (df['localtime'] - t2).abs().idxmin()
        t2 = df.iloc[nearest_index]['localtime']
        t2_index = nearest_index
       

    # print(df.iloc[i]['localtime'],df.iloc[t2_index]['localtime'])    

    # Check if SOC difference is greater than the threshold
    print(df.iloc[i]['SOC_8'] - df.iloc[t2_index]['SOC_8'])
    
    if abs(df.iloc[i]['SOC_8'] - df.iloc[t2_index]['SOC_8']) > threshold:
        print("Entered if---------->")
        # Print the time when battery change occurred (using t1 as it's the most recent timestamp)
        print("Battery changed at:", t1)

        start_time = t1 - pd.Timedelta(seconds=anomaly_window)
        start_time_index = df[df['localtime'] <= start_time].index.min()
        # If t2_index is NaN, find the nearest index to t2
        if pd.isna(start_time_index):
                nearest_index = (df['localtime'] - start_time).abs().idxmin()
                start_time= df.iloc[nearest_index]['localtime']
                start_time_index = nearest_index        

        
        last_battery_change_time = df.iloc[last_battery_change_index]['localtime']
        end_time = last_battery_change_time - pd.Timedelta(seconds=anomaly_window)
        end_time_index = df[df['localtime'] <= end_time].index.min()
        # If t2_index is NaN, find the nearest index to t2
        if pd.isna(end_time_index):
                nearest_index = (df['localtime'] - end_time).abs().idxmin()
                end_time= df.iloc[nearest_index]['localtime']
                end_time_index = nearest_index

        battery_data = df.iloc[start_time_index:end_time_index].copy()  # Data from the last battery change to the current battery change


                    #Create a new dataframe for each battery within the current window
                    #For original data(will have redundant data when the battery is changed so, dropped 40 seconds before and after of the battery change)
                    #battery_data = df.iloc[start_time_index:last_battery_change_index].copy()  # Data from the last battery change to the current battery change
        
        
         # Create a folder for each battery
        folder_name = f'Battery_{battery_number}'
        os.makedirs(os.path.join(folder_path, folder_name), exist_ok=True)
 
        # Save the battery data to a new CSV file inside the folder
        battery_data.to_csv(os.path.join(folder_path, folder_name, f'log_file.csv'), index=False)
        print("Folder and Excel file for Battery", battery_number, "generated----------------->")
        print("Excel file for", battery_number ,"generated----------------->")

        
        # Update battery end index and battery number
        battery_end_index = i
        battery_number += 1

         # Update the index of the last battery change
        last_battery_change_index = i + 1
        
        # Move to the next window (t1 becomes t2 for the next iteration)
        i = t2_index
    else:
        # Move to the next window
        i = t2_index
import pandas as pd

# Assuming 'df' is your dataframe with SOC data
df = pd.read_csv(r'C:\Users\kamalesh.kb\CodeForAutomation\Automationdashboard\Automationdashboard\MAIN_FOLDER\Automation_Dashboard_Batterywise\V2\D11_03_2024_MulBattery\B3_wholeDayBB\b3_11_03_24.csv',low_memory=False)
df['localtime'] = pd.to_datetime(df['localtime'], format=r'%d-%m-%Y %H:%M:%S')

# Reverse the order of the rows
df_reversed = df[::-1]

# Sort the DataFrame based on 'localtime' column
df_reversed = df_reversed.sort_values(by='localtime')

# Write the reversed DataFrame to a new CSV file
df_reversed.to_csv("reversed_csv_file.csv", index=False)

# Convert 'SOC_8' column to numeric
df_reversed['SOC_8'] = pd.to_numeric(df_reversed['SOC_8'], errors='coerce')  # 'coerce' will convert non-numeric values to NaN

# Set the threshold for detecting battery change
threshold = 40  # Example threshold value, adjust as needed

# Convert 'localtime' column to datetime objects
df_reversed['localtime'] = pd.to_datetime(df_reversed['localtime'], format=r'%d-%m-%Y %H:%M:%S')
# df_reversed['localtime'] = pd.to_datetime(df_reversed['localtime'], format=r'%y-%m-%d %H:%M:%S')


# Initialize battery_end_index and battery_number
battery_end_index = 0
battery_number = 1
anomaly_window= 40
Time_window=60

#Got1BatterySplit


# Start from the rightmost end of the dataframe
i = len(df_reversed) - 1
# Initialize the index of the last battery change
last_battery_change_index = len(df_reversed) - 1

t2_index=1      #to avoid the while loop enter into the infinite loop

# Iterate over the dataframe in steps of 60 seconds
while i >= 0 and t2_index >0:
    t1 = df_reversed.iloc[i]['localtime']
    t2 = t1 + pd.Timedelta(seconds=Time_window)  # t2 is 60 seconds earlier than t1
    print("t1------------------>",t1)
    print("t2------------------>",t2)
    # print("t1---------->: ",t1,"t2---------->: ",t2)

    # Find the index of t2
    t2_index = df_reversed[df_reversed['localtime'] <= t2].index.min()
    
    print(i,t2_index)
    # If t2_index is NaN, find the nearest index to t2
    if pd.isna(t2_index):
        print("t2 not available in the dataframe.")
        nearest_index = (df_reversed['localtime'] - t2).abs().idxmax
        t2 = df_reversed.iloc[nearest_index]['localtime']
        t2_index = nearest_index
       

    # print(df.iloc[i]['localtime'],df.iloc[t2_index]['localtime'])    

    # Check if SOC difference is greater than the threshold
    print(df_reversed.iloc[i]['SOC_8'] - df_reversed.iloc[t2_index]['SOC_8'])
    
    if abs(df_reversed.iloc[i]['SOC_8'] - df_reversed.iloc[t2_index]['SOC_8']) > threshold:
        print("Entered if---------->")
        # Print the time when battery change occurred (using t1 as it's the most recent timestamp)
        print("Battery changed at:", t1)

        start_time = t1 - pd.Timedelta(seconds=anomaly_window)
        start_time_index = df_reversed[df_reversed['localtime'] <= start_time].index.min()
        # If t2_index is NaN, find the nearest index to t2
        if pd.isna(start_time_index):
                nearest_index = (df_reversed['localtime'] - start_time).abs().idxmin()
                start_time= df_reversed.iloc[nearest_index]['localtime']
                start_time_index = nearest_index        

        
        last_battery_change_time = df_reversed.iloc[last_battery_change_index]['localtime']
        end_time = last_battery_change_time - pd.Timedelta(seconds=anomaly_window)
        end_time_index = df_reversed[df_reversed['localtime'] <= end_time].index.min()
        # If t2_index is NaN, find the nearest index to t2
        if pd.isna(end_time_index):
                nearest_index = (df_reversed['localtime'] - end_time).abs().idxmin()
                end_time= df_reversed.iloc[nearest_index]['localtime']
                end_time_index = nearest_index

        battery_data = df_reversed.iloc[start_time_index:end_time_index].copy()  # Data from the last battery change to the current battery change


                    #Create a new dataframe for each battery within the current window
                    #For original data(will have redundant data when the battery is changed so, dropped 40 seconds before and after of the battery change)
                    #battery_data = df.iloc[start_time_index:last_battery_change_index].copy()  # Data from the last battery change to the current battery change
        
        # Save the battery data to a new CSV file
        battery_data.to_csv(f'Battery_{battery_number}_data.csv', index=False)
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
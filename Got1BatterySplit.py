import pandas as pd

# Read the CSV file
df = pd.read_csv(r'C:\Users\kamalesh.kb\CodeForAutomation\Automationdashboard\Automationdashboard\MAIN_FOLDER\Automation_Dashboard_Batterywise\V4\D11_03_2024_MulBattery\B4_17.33_21.40\log_file.csv')

# Sort the dataframe by SOC_8 column
df.sort_values(by='SOC_8', inplace=True)

# Define a threshold for SOC difference between batteries
threshold = 40
length= len(df)

# Initialize variables to track battery changes
battery_end_index = len(df)
battery_number = 1

# Iterate through the dataframe in reverse to split the data into separate batteries
# Iterate through the dataframe in reverse by groups of 10 to split the data into separate batteries
for i in range(length, 1, -10):
    if df.iloc[i-1]['SOC_8'] - df.iloc[i-11]['SOC_8'] > threshold:
        print("Entered if---------->")
        # Create a new dataframe for each battery
        battery_data = df.iloc[i-1:battery_end_index].copy()
        
        # Save the battery data to a new CSV file
        battery_data.to_csv(f'Battery_{battery_number}_data.csv', index=False)
        
        # Update battery end index and battery number
        battery_end_index = i
        battery_number += 1
        length = i-10
        print("length",length)

        


# Save the data of the first battery
battery_data = df.iloc[0:battery_end_index].copy()
battery_data.to_csv(f'Battery_{battery_number}_data.csv', index=False)

print("Data has been split and saved into separate CSV files for each battery.")




import pandas as pd
 
# Define the paths for input and output
input_file_path = r'C:\Users\kamalesh.kb\CodeForAutomation\OUTPUT_1\Mar-13\Battery_2\log_file.csv'
output_file_path = r'C:\Users\kamalesh.kb\CodeForAutomation\OUTPUT_1\Mar-13\Battery_2\filtered_log2.csv'
# main_folder_path= r'C:\Users\kamalesh.kb\CodeForAutomation\OUTPUT_1'


start_time =  None
end_time = None


start_time =  "13-03-2024  10:10:00"

end_time = "13-03-2024  12:22:00"




 
data = pd.read_csv(input_file_path)

if 'localtime' not in data.columns:
    # Convert the 'timestamp' column from Unix milliseconds to datetime
    data['localtime'] = pd.to_datetime(data['timestamp'], unit='ms')

    # Adjusting the timestamp to IST (Indian Standard Time) by adding 5 hours and 30 minutes
    data['localtime'] = data['localtime'] + pd.Timedelta(hours=5, minutes=30)


# Convert 'localtime' column to datetime
data['localtime'] = pd.to_datetime(data['localtime'], format='%Y-%m-%d %H:%M:%S.%f')
 
# Sample input simulation (You will replace these with actual user inputs or logic to handle absence of inputs)

 
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


          

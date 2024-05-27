import pandas as pd
from scipy.spatial import KDTree
import numpy as np
import os

def Merge_log_km():
    # Define the main directory containing all project subfolders
    main_folder = r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard'

    # Get all project folders within the main directory
    project_folders = [os.path.join(main_folder, f) for f in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, f))]

    # Process each project folder
    for project_folder in project_folders:
        all_merged_dfs = []  # List to store each merged dataframe for the current project

        # Iterate over each subdirectory in the current project folder
        for subfolder in os.listdir(project_folder):
            subfolder_path = os.path.join(project_folder, subfolder)

            # Check if the path is indeed a directory
            if os.path.isdir(subfolder_path):
                log_file = os.path.join(subfolder_path, 'log.csv')
                km_file = os.path.join(subfolder_path, 'km.csv')

                # Check if both files exist in the subfolder
                if os.path.exists(log_file) and os.path.exists(km_file):
                    # Load the CSV files
                    log_df = pd.read_csv(log_file)
                    km_df = pd.read_csv(km_file)

                    # Process the files as per your existing logic
                    log_df['localtime'] = pd.to_datetime(log_df['localtime'], dayfirst=True)
                    km_df['localtime'] = pd.to_datetime(km_df['localtime'], dayfirst=True)
                    log_timestamps = log_df['localtime'].astype('int64').to_numpy()
                    km_timestamps = km_df['localtime'].astype('int64').to_numpy()

                    km_tree = KDTree(km_timestamps.reshape(-1, 1))
                    distances, indices = km_tree.query(log_timestamps.reshape(-1, 1))

                    log_df['km2_index'] = indices
                    merged_df = pd.merge(log_df, km_df, left_on='km2_index', right_index=True, suffixes=('_log', '_km'))

                    merged_df.rename(columns={
                        'id_log': 'id',
                        'timestamp_log': 'timestamp',
                        'localtime_log': 'localtime'
                    }, inplace=True)

                    merged_df.drop(columns=['km2_index'], inplace=True)

                    # Save the merged_df to the same subfolder as "log_km.csv"
                    merged_df_output_path = os.path.join(subfolder_path, 'log_km.csv')
                    merged_df.to_csv(merged_df_output_path, index=False)
                    print(f"Merged file saved to {merged_df_output_path}")

                    # Append the merged dataframe to the list
                    all_merged_dfs.append(merged_df)

        # Concatenate all dataframes from the list for the current project
        if all_merged_dfs:
            all_data = pd.concat(all_merged_dfs)
            # Sort by 'localtime' and remove duplicates if needed
            all_data_sorted = all_data.sort_values(by='localtime')
            all_data_unique = all_data_sorted.drop_duplicates(subset='localtime', keep='first')

            # Construct output file name based on the project folder name
            folder_name = os.path.basename(project_folder)
            final_output_path = os.path.join(project_folder, f'{folder_name}_final_merged_output.csv')

            # Save the final merged dataframe to the current project folder
            all_data_unique.to_csv(final_output_path, index=False)
            print(f"Final merged file saved to {final_output_path}")

def crop_data():
    import os
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import mplcursors  # Import mplcursors
    import warnings
    
    # Disable the SettingWithCopyWarning
    warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
    
    # Define the paths for input and output
    main_folder_path = r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard'
    
    
    
    
    #################
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
        if 'localtime' not in data.columns:
            # Convert the 'timestamp' column from Unix milliseconds to datetime
            data['localtime'] = pd.to_datetime(data['timestamp'], unit='ms')
    
            # Adjusting the timestamp to IST (Indian Standard Time) by adding 5 hours and 30 minutes
            data['localtime'] = data['localtime'] + pd.Timedelta(hours=5, minutes=30)
    
    
        # Convert 'localtime' column to datetime
        data['localtime'] = pd.to_datetime(data['localtime'], format='%Y-%m-%d %H:%M:%S.%f')
    
    
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
        subfolder_path = os.path.join(main_folder_path, folder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        plt.savefig(os.path.join(deeper_subfolder_path, 'graph.png'))  # Save the plot as an image in the specified directory
        plt.show()
        
    
    ################
        if 'localtime' not in data.columns:
            # Convert the 'timestamp' column from Unix milliseconds to datetime
            data['localtime'] = pd.to_datetime(data['timestamp'], unit='ms')
    
            # Adjusting the timestamp to IST (Indian Standard Time) by adding 5 hours and 30 minutes
            data['localtime'] = data['localtime'] + pd.Timedelta(hours=5, minutes=30)
    
    
        # Convert 'localtime' column to datetime
        data['localtime'] = pd.to_datetime(data['localtime'], format='%Y-%m-%d %H:%M:%S.%f')
    
    
    # Iterate through all subfolders in the main folder
    for subfolder in os.listdir(main_folder_path):
        subfolder_path = os.path.join(main_folder_path, subfolder)
        print("Subfolder name or Date=", subfolder)
        if os.path.isdir(subfolder_path):
            # Iterate through next level of subfolders
            for deeper_subfolder in os.listdir(subfolder_path):
                deeper_subfolder_path = os.path.join(subfolder_path, deeper_subfolder)
                if os.path.isdir(deeper_subfolder_path):
                    # Find the log file in the deepest subfolder
                    log_file_path = os.path.join(deeper_subfolder_path, 'log_km.csv')
                    if os.path.exists(log_file_path):
                        data = pd.read_csv(log_file_path)
                    
                        # Convert 'timestamp' to datetime
                        data['localtime'] = pd.to_datetime(data['timestamp'], unit='ms') + pd.Timedelta(hours=5, minutes=30)
            
                        plot_ghps(data,subfolder)
            
            
                        # Check if cropping is needed
                        crop = input("Do you want to remove anomalies? (yes/no): ")
                        if crop.lower() == "yes":
                            # Allow user to input start time and end time for the anomalies after seeing the graph
                            start_time_input = input("Enter start time of anomaly (format: DD-MM-YYYY HH:MM:SS): ")
                            end_time_input = input("Enter end time of anomaly (format: DD-MM-YYYY HH:MM:SS): ")

                            # Convert input strings to datetime
                            start_time = pd.to_datetime(start_time_input, format='%d-%m-%Y %H:%M:%S')
                            end_time = pd.to_datetime(end_time_input, format='%d-%m-%Y %H:%M:%S')

                            # Filter the data to exclude only the anomaly data between user-specified start and end times
                            filtered_data = data[(data['localtime'] < start_time) | (data['localtime'] > end_time)]

                            #the following is the code for checking whether the anamoly data deleted or not
                            # Filter the DataFrame to check data between start_time and end_time
                            filtered_data = data[(data['localtime'] <start_time) | (data['localtime'] > end_time)]

                            # Replot and save the normal data
                            plot_ghps(filtered_data, subfolder)  # Plotting the data without the anomalies

                            # Define output file path for this Battery folder
                            output_file_path = os.path.join(deeper_subfolder_path, 'log_withoutanomaly.csv')

                            # Save the normal data to CSV in the same folder
                            filtered_data.to_csv(output_file_path, index=False)

                    else:
                        print("No log file found in folder:", subfolder)
Merge_log_km()
crop_data()
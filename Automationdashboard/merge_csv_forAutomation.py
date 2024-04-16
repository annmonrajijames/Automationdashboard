import pandas as pd
from scipy.spatial import KDTree
import numpy as np
import os

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
        final_output_path = os.path.join(project_folder, f'{folder_name}_dailyreport.csv')
        all_data_unique.to_csv(final_output_path, index=False)
        print(f"Final merged file saved to {final_output_path}")

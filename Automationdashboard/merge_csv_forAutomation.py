import pandas as pd
from scipy.spatial import KDTree
import numpy as np
import os

# Define the main directory containing the subfolders
main_folder = r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\Mar-30'

# Iterate over each subdirectory in the main folder
for subfolder in os.listdir(main_folder):
    subfolder_path = os.path.join(main_folder, subfolder)

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

            # Save the merged dataframe to a new CSV file in the same subfolder
            merged_path = os.path.join(subfolder_path, 'log_km_merged.csv')
            merged_df.to_csv(merged_path, index=False)

            print(f"Merged file saved to {merged_path}")

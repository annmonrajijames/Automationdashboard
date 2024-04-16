import pandas as pd
from scipy.spatial import KDTree
import numpy as np

# Load the CSV files
log1_df = pd.read_csv(r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\log.csv")
km2_df = pd.read_csv(r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\km.csv")

# Convert "localtime" columns to datetime format for both DataFrames, specifying day-first parsing
log1_df['localtime'] = pd.to_datetime(log1_df['localtime'], dayfirst=True)
km2_df['localtime'] = pd.to_datetime(km2_df['localtime'], dayfirst=True)

# Convert the "localtime" to numeric timestamps for KDTree, using astype instead of view
log1_timestamps = log1_df['localtime'].astype('int64').to_numpy()
km2_timestamps = km2_df['localtime'].astype('int64').to_numpy()

# Build a KDTree for efficient nearest neighbor search, converting to a 2D array for KDTree
km2_tree = KDTree(km2_timestamps.reshape(-1, 1))

# Find the closest timestamp in km2 for each entry in log1, converting log1_timestamps to a 2D array
distances, indices = km2_tree.query(log1_timestamps.reshape(-1, 1))

# Use the found indices to match entries from km2_df to log1_df
log1_df['km2_index'] = indices

# Merge the two dataframes based on the matched indices
merged_df = pd.merge(log1_df, km2_df, left_on='km2_index', right_index=True, suffixes=('_log1', '_km2'))

# Rename columns back to their original names from log 1.csv
merged_df.rename(columns={
    'id_log1': 'id',
    'timestamp_log1': 'timestamp',
    'localtime_log1': 'localtime'
}, inplace=True)

# Drop the auxiliary column used for merging
merged_df.drop(columns=['km2_index'], inplace=True)

# Save the merged dataframe to a new CSV file
merged_path = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\log 1_km 2_merged.csv"
merged_df.to_csv(merged_path, index=False)

print(f"Merged file saved to {merged_path}")
import pandas as pd

# Load the CSV files
km2_df = pd.read_csv('c:\Git_Projects\Automationdashboard\Automationdashboard/km 2.csv')
log1_df = pd.read_csv('c:\Git_Projects\Automationdashboard\Automationdashboard/log 1.csv')

# Convert timestamps to datetime for easier handling
km2_df['timestamp_dt'] = pd.to_datetime(km2_df['timestamp'], unit='ms')
log1_df['timestamp_dt'] = pd.to_datetime(log1_df['timestamp'], unit='ms')

# Set the index to the timestamp for both dataframes for alignment
km2_df.set_index('timestamp_dt', inplace=True)
log1_df.set_index('timestamp_dt', inplace=True)

# Create a unified index from both dataframes to ensure no timestamp is missed
combined_index = km2_df.index.union(log1_df.index)

# Reindex both dataframes to this combined index with the nearest method to align on the closest timestamp
km2_df_reindexed = km2_df.reindex(combined_index, method='nearest')
log1_df_reindexed = log1_df.reindex(combined_index, method='nearest')

# Prepare for merging based on localtime by first calculating mismatches (optional for understanding discrepancies)
comparison_df = pd.DataFrame({
    'km2_localtime': km2_df_reindexed['localtime'],
    'log1_localtime': log1_df_reindexed['localtime'],
    'matches': km2_df_reindexed['localtime'] == log1_df_reindexed['localtime']
})
mismatches_df = comparison_df[~comparison_df['matches']]

# Convert 'localtime' to datetime in mismatches_df for variation calculation (optional analysis)
mismatches_df['km2_localtime_dt'] = pd.to_datetime(mismatches_df['km2_localtime'], format='%d/%m/%Y %H:%M:%S.%f')
mismatches_df['log1_localtime_dt'] = pd.to_datetime(mismatches_df['log1_localtime'], format='%d/%m/%Y %H:%M:%S.%f')
mismatches_df['time_difference'] = (mismatches_df['km2_localtime_dt'] - mismatches_df['log1_localtime_dt']).dt.total_seconds().abs()
average_variation = mismatches_df['time_difference'].mean()

# Overwrite localtime in km2_df_reindexed with the localtime from log1_df_reindexed
km2_df_reindexed['localtime'] = log1_df_reindexed['localtime']

# Combine both dataframes with a suffix for log1_df_reindexed columns to avoid conflicts
merged_df = km2_df_reindexed.combine_first(log1_df_reindexed.add_suffix('_log1'))

# Reset index to include the timestamp in the data and save to CSV
merged_df.reset_index(inplace=True)
merged_csv_path = 'c:\Git_Projects\Automationdashboard\Automationdashboard/merged_km_log.csv'
merged_df.to_csv(merged_csv_path, index=False)

# Output the path to the new merged CSV file
print(merged_csv_path)
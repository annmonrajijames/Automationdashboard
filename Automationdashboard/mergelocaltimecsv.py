import pandas as pd

# List of file paths (replace these with the correct paths to your files)
file_paths = [
    r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\Mar-30\1\log_km_merged.csv',
    r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\Mar-30\2\log_km_merged_1.csv',
    # Add more paths as necessary
]

# Load all CSV files into DataFrames
dataframes = [pd.read_csv(file) for file in file_paths]

# Convert 'localtime' to datetime for sorting and potential overlap handling
for df in dataframes:
    df['localtime'] = pd.to_datetime(df['localtime'])

# Concatenate all dataframes
all_data = pd.concat(dataframes)

# Sort by 'localtime'
all_data_sorted = all_data.sort_values(by='localtime')

# Remove duplicate rows based on 'localtime' to handle overlapping times
all_data_unique = all_data_sorted.drop_duplicates(subset='localtime', keep='first')

# Optionally, save the final merged dataframe to a new CSV file
all_data_unique.to_csv(r'C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\Mar-30\log_km_merged_merged.csv', index=False)

# Display the first few rows of the resulting dataframe and its shape
print(all_data_unique.head())
print(all_data_unique.shape)

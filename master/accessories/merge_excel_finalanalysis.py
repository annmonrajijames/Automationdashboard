import pandas as pd
import os
 
def merge_excel_files(root_directory):
    # Create an empty DataFrame for the merged data
    merged_df = None
    # Walk through all directories and subdirectories
    for subdir, dirs, files in os.walk(root_directory):
        for file in files:
            if file == 'merged_analysis.xlsx':  # Specific file name to look for
                file_path = os.path.join(subdir, file)
                # Load the Excel file
                data = pd.read_excel(file_path)
                # Set 'File name' as the index
                data.set_index('File name', inplace=True)
                # Add a suffix based on the folder name to distinguish between files
                folder_name = os.path.basename(subdir)
                data.columns = [f"{col}_{folder_name}" for col in data.columns]
                # Merge with the existing DataFrame
                if merged_df is None:
                    merged_df = data
                else:
                    # Use 'outer' join and avoid sorting the indices
                    merged_df = pd.concat([merged_df, data], axis=1)
 
    # Reset index if you prefer 'File name' as a regular column
    merged_df.reset_index(inplace=True)
 
    return merged_df
 
# Specify the root directory containing all subdirectories with 'merged_analysis.xlsx' files
root_directory_path = r'D:\March_BB3\March_BB3'
merged_data = merge_excel_files(root_directory_path)
 
# Save the merged DataFrame to a new Excel file
merged_data.to_excel(r'D:\March_BB3\March_BB3\merged_monthly_analysis.xlsx', index=False)
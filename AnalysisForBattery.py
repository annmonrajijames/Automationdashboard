import pandas as pd
import os
 
# Define the main folder path (replace with your actual path)
main_folder_path = r"C:\Users\kamalesh.kb\CodeForAutomation\Battery_data\B2"
 
# Define a list to store row values
summary_data = []

# Define a list to store subfolder names
subfolder_names = []

# Define the list of keywords
keywords = ["Cycle Count of battery",
            "Total distance covered (km)",
            "Minimum Temperature(C)",
            "Maximum Temperature(C)",
            "highest cell temp(C)",
            "lowest cell temp(C)"]

# Loop through each subfolder
for subfolder in os.listdir(main_folder_path):
    if subfolder.startswith("B") and os.path.isdir(os.path.join(main_folder_path, subfolder)):
        subfolder_names.append(subfolder)
        
        # Find excel file starting with "analysis"
        analysis_file = None
        for filename in os.listdir(os.path.join(main_folder_path, subfolder)):
            if filename.startswith("analysis") and filename.endswith(".xlsx"):
                analysis_file = os.path.join(main_folder_path, subfolder, filename)
                break  # Stop iterating after finding the first matching file
    
        # Check if an analysis file was found
        if analysis_file:
            try:
                # Try reading the excel file
                data = pd.read_excel(analysis_file)
    
                # Initialize dictionary to store keyword data
                keyword_data = {"Subfolder": subfolder}
    
                # Extract data for each keyword
                for keyword in keywords:
                    found = False
                    # Search for keyword in each row
                    for index, row in data.iterrows():
                        if keyword in row.tolist():
                            keyword_data[keyword] = row.tolist()[1]  # Store data
                            found = True
                            break  # Stop searching after finding the first match
                    if not found:
                        keyword_data[keyword] = ""  # Store empty string if keyword not found
    
                summary_data.append(keyword_data)  # Append data for this subfolder
            except FileNotFoundError:
                print(f"File not found: {analysis_file}")
            except pd.errors.ParserError:
                print(f"Error parsing excel file: {analysis_file}")
 
# Check if summary data was found (optional)
if not summary_data:
    print("Summary data not found in any excel files.")
 
# If summary data is found, convert the list to a dataframe
if summary_data:
    # Define the full path for saving the summary Excel file
    summary_file_path = os.path.join(main_folder_path, "BatteryAnalysis.xlsx")
    summary_df = pd.DataFrame(summary_data)  # Convert list of dictionaries to DataFrame
    summary_df = summary_df.set_index("Subfolder")  # Set subfolder names as index
    summary_df = summary_df.T  # Transpose DataFrame
    summary_df.to_excel(summary_file_path)  # Save DataFrame to Excel file
    print("Analysis file created successfully!")

import pandas as pd
import os

# Define the main folder path (replace with your actual path)
main_folder_path = r"C:\Users\kamalesh.kb\CodeForAutomation\Battery_data\B2"

# Define the folder path where you want to save the summary file
summary_folder_path = r"C:\Users\kamalesh.kb\CodeForAutomation\Battery_data\B2\Summary"

# Create the folder if it doesn't exist
os.makedirs(summary_folder_path, exist_ok=True)

# Define a list to store row values
summary_data = []

# Loop through each subfolder
for subfolder in os.listdir(main_folder_path):
    # Find excel file starting with "analysis"
    analysis_file = None
    for filename in os.listdir(os.path.join(main_folder_path, subfolder)):
        if filename.startswith("analysis") and filename.endswith(".xlsx"):
            analysis_file = os.path.join(main_folder_path, subfolder, filename)
            print("debug")
            break  # Stop iterating after finding the first matching file

    # Check if an analysis file was found
    if analysis_file:
        try:
            # Try reading the excel file
            data = pd.read_excel(analysis_file)
            print(data)

            # Define expected keywords and corresponding columns
            summary_keywords = {
                "Total distance covered (km)": "Total Distance",
                "Maximum Temperature(C)": "Max Temperature"
            }

            # Search for rows containing the specified keywords
            for keyword, column_name in summary_keywords.items():
                for index, row in data.iterrows():
                    if keyword in row.tolist():
                        # Append the entire row with renamed columns
                        row_dict = {column_name: value for column_name, value in zip(data.columns, row)}
                        summary_data.append(row_dict)
                        break  # Stop searching after finding the first matching row

        except FileNotFoundError:
            print(f"File not found: {analysis_file}")
        except pd.errors.ParserError:
            print(f"Error parsing excel file: {analysis_file}")

# Check if summary data was found
if not summary_data:
    print("Summary data not found in any excel files.")
else:
    # Convert the list of dictionaries to DataFrame
    summary_df = pd.DataFrame(summary_data)

    # Save the summary DataFrame to the specified folder
    summary_file_path = os.path.join(summary_folder_path, 'summary.xlsx')
    summary_df.to_excel(summary_file_path, index=False)  # Save without index
    print(f"Summary created successfully and saved at {summary_file_path}!")

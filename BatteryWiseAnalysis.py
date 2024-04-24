import pandas as pd
import os
 
# Define the main folder path (replace with your actual path)
main_folder_path = r"C:\Users\kamalesh.kb\CodeForAutomation\Battery_data\B2"
 
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
 
      # Define expected keywords in the first row (modify as needed)
      summary_keywords = ["Cycle Count of battery", "Total distance covered (km)",
                          "Minimum Temperature(C)", "Maximum Temperature(C)",
                          "highest cell temp(C)", "lowest cell temp(C)"]
 
      # Search for rows containing all keywords in the first row
      for index, row in data.iterrows():
        if any(keyword in row.tolist() for keyword in summary_keywords):
          summary_data.append(row.tolist())  # Append entire row as list
          break  # Stop searching after finding the first matching row
 
    except FileNotFoundError:
      print(f"File not found: {analysis_file}")
    except pd.errors.ParserError:
      print(f"Error parsing excel file: {analysis_file}")
 
# Check if summary data was found (optional)
if not summary_data:
  print("Summary data not found in any excel files.")
 
# If summary data is found, convert the list to a dataframe
if summary_data:
  summary_df = pd.DataFrame(summary_data)  # Use column names from first row
  summary_df.to_excel("summary.xlsx", index=False)  # Save without index
  print("Summary created successfully!")
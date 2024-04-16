import pandas as pd
import os
 
# Define the main folder path
main_folder_path = r"C:\Users\kamalesh.kb\CodeForAutomation\Automationdashboard\Battery_dataAnalysis"  # Replace with your actual path
 
# Create an empty dictionary to store summary data
summary_data = {"Max Cycle Count": 0,
                "Total Kilometers": 0,
                "Min Temperature": float("inf"),
                "Max Temperature": float("-inf"),
                "Min Cell Temp": float("inf"),
                "Max Cell Temp": float("-inf")}
 
# Loop through each subfolder
for subfolder in os.listdir(main_folder_path):
  # Find excel file starting with "analysis"
  analysis_file = None
  for filename in os.listdir(os.path.join(main_folder_path, subfolder)):
    if filename.startswith("analysis") and filename.endswith(".xlsx"):
      analysis_file = os.path.join(main_folder_path, subfolder, filename)
      break  # Stop iterating after finding the first matching file
 
  # Check if an analysis file was found
  if analysis_file:
    try:
      # Read the excel file using pandas
      data = pd.read_excel(analysis_file)
 
      # Update summary data (same logic as before)
      summary_data["Max Cycle Count"] = max(summary_data["Max Cycle Count"], data["Cycle Count of battery"].max())
      summary_data["Total Kilometers"] += data["Total distance covered (km)"].sum()
      summary_data["Min Temperature"] = min(summary_data["Min Temperature"], data["Minimum Temperature (C)"].min())
      summary_data["Max Temperature"] = max(summary_data["Max Temperature"], data["Maximum Temperature (C)"].max())
      summary_data["Min Cell Temp"] = min(summary_data["Min Cell Temp"], data["lowest cell temp(C)"].min())
      summary_data["Max Cell Temp"] = max(summary_data["Max Cell Temp"], data["highest cell temp(C)"].max())
    except FileNotFoundError:
      print(f"File not found: {analysis_file}")
    except pd.errors.ParserError:
      print(f"Error parsing excel file: {analysis_file}")
 
# Create pandas dataframe and save to excel (same as before)
summary_df = pd.DataFrame.from_dict(summary_data, orient='index', columns=['Values'])
summary_df.to_excel("summary.xlsx")
 
print("Summary created successfully!")
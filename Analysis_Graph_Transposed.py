import pandas as pd

# Full file path of the original Excel file
file_path = r'C:\Users\kamalesh.kb\CodeForAutomation\Graph_analysis\BB3\analysis_monthly.xlsx'

# Read the original Excel file
df = pd.read_excel(file_path)

# Define the specific rows you want to extract
specific_rows = ['File name','Total distance covered (km)','Total energy consumption(WH/KM)','Total SOC consumed(%)','Mode','Peak Power(kW)','Average Power(kW)','Regenerative Effectiveness(%)','Difference in Cell Voltage(V)','Difference in Temperature(C)','Maximum Fet Temperature-BMS(C)']

# Filter the DataFrame to keep only the rows that match the specified criteria
filtered_df = df[df['File name'].isin(specific_rows)]

# Transpose the DataFrame
transposed_df = filtered_df.T

# Full file path of the new transposed CSV file
transposed_output_file_path = r'C:\Users\kamalesh.kb\CodeForAutomation\Graph_analysis\BB3\transposed_specific_analysis.csv'

# Write the transposed DataFrame to a new CSV file without including the index
transposed_df.to_csv(transposed_output_file_path, header=False, index=False)  # Don't write column names as header and exclude the index

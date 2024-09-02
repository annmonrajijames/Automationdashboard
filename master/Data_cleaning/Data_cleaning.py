import pandas as pd
import os

# Read the CSV file into a DataFrame
input_file = r'C:\Users\kamalesh.kb\Anomaly_test\Anomaly\log.csv'
df = pd.read_csv(input_file)

# Remove rows where 'IgnitionStatus_12' is '0'
cleaned_df = df[df['IgnitionStatus_12'] != 0]

# Get the directory of the input file
input_dir = os.path.dirname(os.path.abspath(input_file))

# Save the cleaned DataFrame to a new CSV file in the same directory
output_file = os.path.join(input_dir, 'cleaned_data.csv')
cleaned_df.to_csv(output_file, index=False)

print(f"Cleaned data saved to: {output_file}")
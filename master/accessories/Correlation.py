import pandas as pd

# Load the CSV file
file_path = r"D:\Git_Projects\Automationdashboard\Automationdashboard/log 1.csv"  # Update this to your actual file path
data = pd.read_csv(file_path)

# Define the column of interest
column_of_interest = 'Controller_Over_Temperature_408094978'

# Check if the column exists in the dataset
if column_of_interest in data.columns:
    # Select only numeric columns for the correlation calculation
    numeric_cols = data.select_dtypes(include=[float, int]).columns
    correlation_matrix = data[numeric_cols].corr()
    
    # Extract correlations with the specific column
    correlations = correlation_matrix[column_of_interest].sort_values(key=abs, ascending=False)
    
    # Display the top correlated columns
    print(correlations.head(40))
else:
    print(f"The column '{column_of_interest}' was not found in the dataset.")

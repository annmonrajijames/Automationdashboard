import pandas as pd

log_file = "path_to_your_log_file.csv"
data = pd.read_csv(log_file)
print(data.head())

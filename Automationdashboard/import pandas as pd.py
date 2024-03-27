import pandas as pd

log_file = r"Automationdashboard/MAIN_FOLDER/MAR_21/log_file.csv"
data = pd.read_csv(log_file)
print(data.head())

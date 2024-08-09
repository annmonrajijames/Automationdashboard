import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
file_path = r"C:\Users\srijanani.LTPL\Downloads\City_LXS_G_2.0_Latest_final_4 1.csv"  # Update with your actual file path
data = pd.read_csv(file_path)

if 'localtime' not in data.columns:
          data['localtime'] = pd.to_datetime(data['DATETIME'], unit='s') + pd.Timedelta(hours=5, minutes=30)


print(data['localtime'] )
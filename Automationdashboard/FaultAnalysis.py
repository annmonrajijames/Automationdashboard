import pandas as pd
path=r'C:\Work\Git_Projects\Automationdashboard\Automationdashboard\log 1.csv'
log_data = pd.read_csv(path, parse_dates=['localtime'])
error_indices = log_data['Controller_Over_Temeprature_408094978'] == 1  # Adjust condition as needed
window = pd.Timedelta(minutes=5)  # Example window size
for error_time in log_data[error_indices]['localtime']:
    window_data = log_data[(log_data['localtime'] >= error_time - window) & 
                           (log_data['localtime'] <= error_time + window)]
    # Analyze window_data for correlated metrics
import matplotlib.pyplot as plt
import seaborn as sns

# Example plot
plt.figure(figsize=(10, 6))
sns.lineplot(data=window_data, x='localtime', y='PcbTemp_12')
plt.show()
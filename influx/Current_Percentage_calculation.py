import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the Excel file
file_path = r'C:\Users\kamalesh.kb\Influx_master\lxsVsNduro\lxs\17_8\log.csv'  # Update with your actual file path
# folder_path =r'C:\Users\kamalesh.kb\ENDURO_CURRENT\HYPER_MODE_DUAL_21_JULY_13.23_14.12'
data = pd.read_csv(file_path)

data['DATETIME'] = pd.to_datetime(data['DATETIME'], unit='s')
data.set_index('DATETIME', inplace=True)  # Setting DATETIME as index
data['localtime_Diff'] = data.index.to_series().diff().dt.total_seconds().fillna(0)
print(data['localtime_Diff'])

# Filter out rows where Current_value is greater than 0
filtered_data = data[data['Regeneration'] ==1]
total_current =0
for index, row in filtered_data.iterrows():

            current = row['Current_value']
            # Calculate the distance traveled in this interval
            total_current += current
            # print("Current------->",total_current)

regen = (total_current/10) /3600
print("Regen Current",regen)


filtered_data_discharge = data[data['Regeneration'] ==0]
total_current_dis=0
for index, row in filtered_data_discharge.iterrows():

            current = row['Current_value']
            # Calculate the distance traveled in this interval
            if not pd.isna(current):
                total_current_dis += current
                # print("Current------->",total_current)
                # print(total_current_dis)

discharge = (total_current_dis/10) /3600
print("Discharge Current",discharge)



# Define the bins and labels for categorization
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, float('inf')]
labels = ['0 to 10', '10 to 20', '20 to 30', '30 to 40', '40 to 50',
          '50 to 60', '60 to 70', '70 to 80', '80 to 90', '90 to 100', '> 100']


# Cut the data into categories using the bins
categories = pd.cut(filtered_data['Current_value'], bins=bins, labels=labels, right=False)

# Add the category column to the filtered data
filtered_data['Category'] = categories

# Calculate the sum of 'Current_value' values in each category
category_sums = filtered_data.groupby('Category')['Current_value'].sum()

# Calculate the absolute sum for percentage calculation (ignoring signs since all values are negative)
total_sum = category_sums.abs().sum()

# Calculate the percentage each category contributes
percentages = (category_sums.abs() / total_sum * 100).reset_index(name='Percentage')

# Plotting the results
plt.figure(figsize=(10, 6))
bars = plt.bar(percentages['Category'], percentages['Percentage'], color='skyblue')

# Adding the percentage labels on top of each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), ha='center', va='bottom')

plt.xlabel('Current Ranges (A)')
plt.ylabel('Percentage of Total Current (%)')
plt.title('Percentage Distribution of Pack Currents')
plt.text(10,8,f'Regen_Current(Ah): {regen}', fontsize=12, color='red')
plt.text(10,15,f'Discharge_Current(Ah): {discharge}', fontsize=12, color='red')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()



# plot_file = f"{folder_path}/Percentage in current intervals.png"
# plt.savefig(folder_path)
plt.show()
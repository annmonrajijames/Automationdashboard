import pandas as pd
import matplotlib.pyplot as plt
import os



# Load the new data from the CSV file
# file_path = r""
# data = pd.read_csv(file_path)

def current_percentage_calc(data,save_path):
    # Define the bins and labels for categorization
    bins = [-float('inf'), -100, -90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, float('inf')]
    labels = ['< -100', '-100 to -90', '-90 to -80', '-80 to -70', '-70 to -60', '-60 to -50',
            '-50 to -40', '-40 to -30', '-30 to -20', '-20 to -10', '-10 to 0', '0 to 10', '10 to 20',
            '20 to 30', '30 to 40', '40 to 50', '50 to 60', '60 to 70', '70 to 80', '80 to 90', '90 to 100', '> 100']

    # Cut the data into categories using the bins
    categories = pd.cut(data['PackCurr [SA: 06]'], bins=bins, labels=labels, right=False)

    # Add the category column to the data
    data['Category'] = categories

    # Calculate the sum of 'PackCurr [SA: 06]' values in each category
    category_sums = data.groupby('Category')['PackCurr [SA: 06]'].sum()

    # Calculate the absolute sum for percentage calculation
    total_sum = category_sums.abs().sum()

    # Calculate the percentage each category contributes
    percentages = (category_sums.abs() / total_sum * 100).reset_index(name='Percentage')

    # Plotting the results
    plt.figure(figsize=(14, 8))
    bars = plt.bar(percentages['Category'], percentages['Percentage'], color='skyblue')

    # Adding the percentage labels on top of each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{round(yval, 2)}%", ha='center', va='bottom')

    plt.xlabel('Current Value Ranges (A)')
    plt.ylabel('Percentage of Total Current (%)')
    plt.title('Percentage Distribution of Current Values')
    plt.xticks(rotation=90)  # Rotate labels for better visibility
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    # Save the plot to the specified path
    plt.savefig(save_path)
    plt.show()


main_folder_path = r"C:\Users\kamalesh.kb\Influx_master\lxsVsNduro\Nduro_analysis"


# Iterate over immediate subfolders of main_folder_path
for subfolder_1 in os.listdir(main_folder_path):
    subfolder_1_path = os.path.join(main_folder_path, subfolder_1)
    
    # Check if subfolder_1 is a directory
    if os.path.isdir(subfolder_1_path):

        # Iterate over subfolders within subfolder_1
        for subfolder in os.listdir(subfolder_1_path):
            subfolder_path = os.path.join(subfolder_1_path, subfolder)
            print(subfolder_path)
            save_path = os.path.join(subfolder_path, 'current_distribution.png')
            
            # Check if subfolder starts with "Battery" and is a directory
            if os.path.isdir(subfolder_path):                
                log_file = None
                log_found = False
                
                # Iterate through files in the subfolder
                for file in os.listdir(subfolder_path):
                    if file.startswith('log.') and file.endswith('.csv'):
                        log_file = os.path.join(subfolder_path, file)
                        log_found = True
                        break  # Stop searching once the log file is found
                
                # Process the log file if found
                if log_found:
                    print(f"Processing log file: {log_file}")
                    try:
                        data = pd.read_csv(log_file)
                        # print("file_path--------->",log_file)
                        # Process your data here
                    except Exception as e:
                        print(f"Error processing {log_file}: {e}")


                    current_percentage_calc(data,save_path)
                    
                    
                    
                else:
                    print("Log file or KM file not found in subfolder:", subfolder)
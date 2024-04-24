## Welcome to Accessories folder

### Files
1. Code_to_crop.py \
It is designed to facilitate data visualization, anomaly detection, and selective data extraction from vehicle telemetry logs. It uses graphical plots to help users identify potential data issues and offers functionality to filter out unwanted data anomalies. 

2. KDTree.py \
The merging of two CSV files based on the closest timestamps using a KDTree for efficient nearest neighbor search. This tool is particularly useful for integrating data from different sources that share a common time frame but may not be synchronized to the exact same timestamps.

3. KD_Tree_Mergefiles_across_directories.py \
It is designed to consolidate data from multiple project subfolders within a main directory, merging them based on timestamps using KDTree for efficient spatial searches. This tool is particularly useful for scenarios where data from various sources or projects need to be combined and synchronized for comprehensive analysis.

4. merge_battery_month.py \
It will merge data based on the first common column from multiple Excel files located within a root directory and its subdirectories. It identifies Excel files named "merged_analysis.xlsx" within each directory, loads their contents into a pandas DataFrame, and merges them into a single DataFrame.

5. split_battery_wise.py \
It is designed to analyze battery data from a DataFrame, detect battery changes based on a predefined threshold, and visualize the data for each battery separately. It processes the DataFrame in time windows and identifies battery changes when the difference in State of Charge (SOC) exceeds a specified threshold. After detecting a battery change, it saves the corresponding data to a CSV file and generates a visualization plot showing battery-related parameters over time.

6. Correlation.py \
Does correlation analysis on a dataset loaded from a CSV file, focusing on a specific column of interest. It calculates the Pearson correlation coefficients between the column of interest and all other numeric columns in the dataset. The script identifies the top correlated columns based on the absolute correlation values and presents them in descending order.

5. README.md \
You are reading me now
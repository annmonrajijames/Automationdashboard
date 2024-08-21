import os
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go

# Define the folder where the CSV files are located
main_folder_path = r"C:\Users\kamalesh.kb\Influx_master\lxsVsNduro\lxsVsNduro_plot"

# File names for the two vehicles
file_names = ['lxs.csv', 'nduro.csv']

# Initialize lists to store data and labels
data_list = []
labels = ['LXS', 'Nduro']  # Labels corresponding to the filenames

# Iterate through the file names and load data
for i, file_name in enumerate(file_names):
    file_path = os.path.join(main_folder_path, file_name)
    
    if os.path.isfile(file_path):
        print(f"Found file: {file_path}")
        
        # Read the CSV file into a DataFrame
        data = pd.read_csv(file_path)
        
        # Determine the correct column for motor speed
        if file_name == 'lxs.csv':
            motor_speed_column = 'RPM'  # For LXS
        else:
            motor_speed_column = 'MotorSpeed [SA: 02]'  # For Nduro
        
        # Calculate speed from motor speed
        data['speed'] = data[motor_speed_column] * 0.0836
        data['DATETIME'] = pd.to_datetime(data['DATETIME'], unit='s')
        data.set_index('DATETIME', inplace=True)
        
        # Store the data
        data_list.append(data)
    else:
        print(f"File not found: {file_path}")

# Plotting function for two datasets
def plot_two_vehicles(data_list, labels, output_path):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Plot data from both vehicles
    for i, data in enumerate(data_list):
        fig.add_trace(go.Scatter(
            x=data.index, y=data['speed'], 
            name=f'Speed - {labels[i]}', 
            line=dict(color='blue' if i == 0 else 'red')
        ), secondary_y=False)
    
    # Update layout
    fig.update_layout(
        title='Speed vs Time for Two Vehicles',
        xaxis_title='Time',
        yaxis_title='Speed (km/h)',
        yaxis2_title='Speed'
    )
    
    fig.update_xaxes(tickformat='%H:%M:%S')
    
    # Save the plot as an HTML file
    os.makedirs(output_path, exist_ok=True)
    graph_path = os.path.join(output_path, 'Benchmark_Speed_Comparison.html')
    fig.write_html(graph_path)
    print(f"Graph saved to {graph_path}")

# Call the plotting function
output_folder = r"C:\Users\kamalesh.kb\Influx_master\lxsVsNduro_plot"
plot_two_vehicles(data_list, labels, output_folder)

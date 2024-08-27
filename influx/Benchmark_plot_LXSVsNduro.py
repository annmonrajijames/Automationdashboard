import os
import pandas as pd
from collections import defaultdict
from plotly.subplots import make_subplots
import plotly.graph_objs as go

# Define the folder where the CSV files are located
main_folder_path = r"C:\Users\kamalesh.kb\lXSvsNDURO\LXSVsNduro_Plot\17_aug"

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
        
        # Determine the correct columns for motor speed, current, voltage, and SOC
        if file_name == 'lxs.csv':
            motor_speed_column = 'RPM'  # For LXS
            current_column = 'Current_value'
            voltage_column = 'voltage_value'
            soc_column = 'SOC_value'

            filtered_data_DischargeCurrent = data[(data['Regeneration']==0)]
            filtered_data_DischargeCurrent['discharge_current'] = filtered_data_DischargeCurrent[current_column]

            filtered_data_regen = data[(data['Regeneration']==1)]
            filtered_data_regen['regen_current'] = filtered_data_regen[current_column]


        else:
            motor_speed_column = 'MotorSpeed [SA: 02]'  # For Nduro
            current_column = 'PackCurr [SA: 06]'
            data[current_column]=-data[current_column]
            voltage_column = 'PackVol [SA: 06]'
            soc_column = 'SOC [SA: 08]'

        # Calculate speed from motor speed
        data['Speed_kmh'] = data[motor_speed_column] * 0.0836
        data['Speed_ms'] = data['Speed_kmh'] / 3.6
        
        # Convert DATETIME to datetime format and calculate time differences
        data['DATETIME'] = pd.to_datetime(data['DATETIME'], unit='s')
        data['localtime_Diff'] = data['DATETIME'].diff().dt.total_seconds().fillna(0)
        data.set_index('DATETIME', inplace=True)
        
        # Calculate average speed
        avg_motor_rpm = data[motor_speed_column].mean()
        avg_motor_speed = avg_motor_rpm * 0.0836
        
        # Initialize total distance and total watt-hours covered
        total_distance_with_RPM = 0
        total_watt_h = 0
        distance_list = []
        wh_list = []

        # Calculate distance and watt-hours incrementally
        for index, row in data.iterrows():
            if 0 < row[motor_speed_column] < 1000:
                distance_interval = row['Speed_ms'] * row['localtime_Diff']
                total_distance_with_RPM += distance_interval

                # Calculate watt-hours incrementally using the trapezoidal rule
                watt_h_interval = abs(row[current_column] * row[voltage_column] * row['localtime_Diff']) / 3600
                total_watt_h += watt_h_interval

            distance_list.append(total_distance_with_RPM / 1000)  # Convert to km
            wh_list.append(total_watt_h)
        
        # Add the distance and watt-hours columns to the data
        data['distance_km'] = distance_list
        data['watt_hours'] = wh_list
        
        # Calculate SOC parameters
        starting_soc_percentage = data[soc_column].max()
        cutoff_soc_percentage = data[soc_column].min()
        soc_consumed = starting_soc_percentage - cutoff_soc_percentage

        ending_soc_rows = data[data[soc_column] == cutoff_soc_percentage]


        if not ending_soc_rows.empty:
            ending_soc_first_occurrence = ending_soc_rows.iloc[0]
            ending_battery_voltage = ending_soc_first_occurrence[voltage_column]
        else:
             # If exact starting SOC percentage is not found, find the nearest SOC percentage
            nearest_soc_index = (data[soc_column] - cutoff_soc_percentage).abs().idxmin()
            ending_soc_first_occurrence = data.iloc[nearest_soc_index]
            ending_battery_voltage = ending_soc_first_occurrence[voltage_column]
            

        # Add SOC parameters to data
        data['soc'] = data[soc_column]
        
        # Store the data along with average speed and SOC parameters
        data_list.append((data, current_column, voltage_column, avg_motor_speed, soc_column, starting_soc_percentage, cutoff_soc_percentage, soc_consumed,ending_battery_voltage))
    else:
        print(f"File not found: {file_path}")

# Plotting function for speed, current, voltage, distance, watt-hours, and average speed
def plot_two_vehicles(data_list, labels, output_path):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Plot data from both vehicles
    for i, (data, current_column, voltage_column, avg_motor_speed, soc_column, starting_soc_percentage, cutoff_soc_percentage, soc_consumed,ending_battery_voltage) in enumerate(data_list):

          # Plot SOC as a line plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['soc'], 
            name=f'SOC - {labels[i]}', 
            marker=dict(color='blue' if i == 0 else 'green')
        ), secondary_y=False)

        # if i == 0:        # Plot SOC as a line plot
        #     fig.add_trace(go.Scatter(
        #         x=data.index, y=-filtered_data_regen['regen_current'], 
        #         name=f'regen current - {labels[i]}', 
        #         marker=dict(color='Green' if i == 0 else 'red')
        #     ), secondary_y=True)

        #         # Plot SOC as a line plot
        #     fig.add_trace(go.Scatter(
        #         x=data.index, y=filtered_data_DischargeCurrent['discharge_current'], 
        #         name=f'discharge current - {labels[i]}', 
        #         marker=dict(color='Red' if i == 0 else 'red')
        #     ), secondary_y=True)
        
        # Plot speed as scatter plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['Speed_kmh'], 
            name=f'Speed - {labels[i]}', 
            marker=dict(color='blue' if i == 0 else 'green')
        ), secondary_y=False)
        
        # Plot current as scatter plot on secondary y-axis
        fig.add_trace(go.Scatter(
            x=data.index, y=data[current_column], 
            name=f'Current - {labels[i]}', 
            marker=dict(color='blue' if i == 0 else 'green')
        ), secondary_y=True)

        # Plot voltage as scatter plot on secondary y-axis
        fig.add_trace(go.Scatter(
            x=data.index, y=data[voltage_column], 
            name=f'Voltage - {labels[i]}', 
            marker=dict(color='blue' if i == 0 else 'green')
        ), secondary_y=True)

        # Plot distance as a separate line plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['distance_km'], 
            name=f'Distance - {labels[i]}', 
            marker=dict(color='blue' if i == 0 else 'green')
        ), secondary_y=False)

        # Plot watt-hours as a separate line plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['watt_hours'], 
            name=f'Watt-hours - {labels[i]}', 
            marker=dict(color='blue' if i == 0 else 'green')
        ), secondary_y=False)

        # Add a horizontal line for average speed
        fig.add_trace(go.Scatter(
            x=[data.index.min(), data.index.max()],
            y=[avg_motor_speed, avg_motor_speed],
            mode='lines',
            line=dict(color='blue' if i == 0 else 'green', dash='dash'),
            name=f'Avg Speed - {labels[i]}'
        ), secondary_y=False)
    
    # Update layout
    fig.update_layout(
        title='Speed, Current, Voltage, Distance, Watt-hours, and Average Speed vs Time for Two Vehicles',
        xaxis_title='Time',
        yaxis_title='Speed (km/h), Distance (km), and Watt-hours (Wh)',
        yaxis2_title='Current (A) and Voltage (V)'
    )
    
    fig.update_xaxes(tickformat='%H:%M:%S')
    
    # Save the plot as an HTML file
    os.makedirs(output_path, exist_ok=True)
    graph_path = os.path.join(output_path, 'Benchmark_Speed_Current_Voltage_Distance_Wh_Comparison.html')
    fig.write_html(graph_path)
    print(f"Graph saved to {graph_path}")

# Plotting function for Battery Parameters
def plot_battery_parameters(data_list, labels, output_path):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Plot SOC and SOC parameters from both vehicles
    for i, (data, _, _, _, soc_column, starting_soc_percentage, cutoff_soc_percentage, soc_consumed,ending_battery_voltage) in enumerate(data_list):
      

        fig.add_trace(go.Scatter(
            x=[data.index.min(), data.index.max()],
            y=[cutoff_soc_percentage, cutoff_soc_percentage],
            mode='lines',
            line=dict(color='blue' if i == 0 else 'green'),
            name=f'Cut-off SoC (%) - {labels[i]}'
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=[data.index.min(), data.index.max()],
            y=[ending_battery_voltage, ending_battery_voltage],
            mode='lines',
            line=dict(color='blue' if i == 0 else 'green'),
            name=f'Cut-off voltage (V) - {labels[i]}'
        ), secondary_y=False)


        

        # # Add annotations for SOC parameters
        # fig.add_annotation(
        #     x=data.index.max(), 
        #     y=cutoff_soc_percentage,
        #     text=f'Cutoff SOC: {cutoff_soc_percentage:.2f}%',
        #     showarrow=True,
        #     arrowhead=2
        # )

        # fig.add_annotation(
        #     x=data.index.max(), 
        #     y=starting_soc_percentage,
        #     text=f'Starting SOC: {starting_soc_percentage:.2f}%',
        #     showarrow=True,
        #     arrowhead=2
        # )
        
        # fig.add_annotation(
        #     x=data.index.max(), 
        #     y=starting_soc_percentage - soc_consumed,
        #     text=f'SOC Consumed: {soc_consumed:.2f}%',
        #     showarrow=True,
        #     arrowhead=2
        # )
    
    # Update layout
    fig.update_layout(
        title='Battery Parameters: SOC, Cutoff SOC, SOC Consumed',
        xaxis_title='Time',
        yaxis_title='SOC (%)'
    )
    
    fig.update_xaxes(tickformat='%H:%M:%S')
    
    # Save the plot as an HTML file
    os.makedirs(output_path, exist_ok=True)
    graph_path = os.path.join(output_path, 'Battery_Parameters.html')
    fig.write_html(graph_path)
    print(f"Graph saved to {graph_path}")

# Call the plotting functions
plot_two_vehicles(data_list, labels, main_folder_path)
plot_battery_parameters(data_list, labels, main_folder_path)
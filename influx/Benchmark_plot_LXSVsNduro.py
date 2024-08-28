import os
import pandas as pd
from collections import defaultdict
from plotly.subplots import make_subplots
import plotly.graph_objs as go
 
# Define the folder where the CSV files are located
main_folder_path = r"C:\Users\annmon.james\Downloads\LXSVsNduro_Plot\19_aug"
 
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
 
            # filtered_data_DischargeCurrent = data[(data['Regeneration']==0)]
            # filtered_data_DischargeCurrent['discharge_current'] = filtered_data_DischargeCurrent[current_column]
 
            # filtered_data_regen = data[(data['Regeneration']==1)]
            # filtered_data_regen['regen_current'] = filtered_data_regen[current_column]
           
            battery_temp_column = 'Battery_Temperature'
            Motor_temp_column = 'Motor_Temp'
            MCU_temp_column= 'MCS_Temp'
   
               
        else:
            motor_speed_column = 'MotorSpeed [SA: 02]'  # For Nduro
            current_column = 'PackCurr [SA: 06]'
            data[current_column]=-data[current_column]
            voltage_column = 'PackVol [SA: 06]'
            soc_column = 'SOC [SA: 08]'
 
            battery_temp_column = 'MaxTemp [SA: 07]'
            Motor_temp_column= 'Motor_Temperature [SA: 03]'
            MCU_temp_column= 'MCU_Temperature [SA: 03]'
 
#######for delta cell voltage
                # Specify the columns of interest
            columns_of_interest = [
                'CellVol01 [SA: 01]', 'CellVol02 [SA: 01]', 'CellVol03 [SA: 01]', 'CellVol04 [SA: 01]',
                'CellVol05 [SA: 02]', 'CellVol06 [SA: 02]', 'CellVol07 [SA: 02]', 'CellVol08 [SA: 02]',
                'CellVol09 [SA: 03]', 'CellVol10 [SA: 03]', 'CellVol11 [SA: 03]', 'CellVol12 [SA: 03]',
                'CellVol13 [SA: 04]', 'CellVol14 [SA: 04]', 'CellVol15 [SA: 04]', 'CellVol16 [SA: 04]'
            ]
       
            # Create an empty list to store computed differences
            differences = []
       
            # Iterate through each row and compute max, min, and their difference for each row
            for index, row in data[columns_of_interest].iterrows():
                max_value = row.max()
                min_value = row.min()
                difference = max_value - min_value
           
                differences.append(difference)  # Append the computed difference to the list
       
            # Add the differences list as a new column 'CellDifference' in the DataFrame
            data['DeltaCellVoltage'] = differences
##############
 
#######for delta and max cell temperature
            # Specify the temperature columns of interest
            temp_columns = [f'Temp{i} [SA: 0A]' for i in range(1, 9)]
 
            # Calculate the maximum cell temperature for each row
            data['Max_Cell_Temperature'] = data[temp_columns].max(axis=1)
 
            # Calculate the minimum cell temperature for each row
            data['Min_Cell_Temperature'] = data[temp_columns].min(axis=1)
 
            # Calculate the difference (delta) between the maximum and minimum cell temperatures for each row
            data['Delta_Cell_Temperature'] = data['Max_Cell_Temperature'] - data['Min_Cell_Temperature']
 
 
       
 
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
 
        # data['Battery'] = abs(data['PackCurr [SA: 06]'] * data['localtime_Diff']).cumsum() / 3600         //for incrementing and storing
        # data_resampled['Battery_Temperature']
 
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
        data['battery_temp']= data[battery_temp_column]
        data['Motor_temp']= data[Motor_temp_column]
        data['MCU_temp']= data[MCU_temp_column]
               
        # Store the data along with average speed and SOC parameters
        data_list.append((data, current_column, voltage_column, avg_motor_speed, soc_column, starting_soc_percentage, cutoff_soc_percentage, soc_consumed,ending_battery_voltage))
    else:
        print(f"File not found: {file_path}")
 
# Plotting function for speed, current, voltage, distance, watt-hours, and average speed
def plot_two_vehicles(data_list, labels, output_path):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
   
    # Define a color palette with contrasting colors for each vehicle's data
    vehicle_colors = [
        {
            'soc': 'blue',
            'Speed_kmh': 'orange',
            'current': 'green',
            'voltage': 'purple',
            'distance_km': 'red',
            'Motor_temp': 'cyan',
            'MCU_temp': 'magenta'
        },
        {
            'soc': 'black',
            'Speed_kmh': 'yellow',
            'current': 'brown',
            'voltage': 'pink',
            'distance_km': 'darkgreen',
            'Motor_temp': 'navy',
            'MCU_temp': 'darkred'
        }
    ]
   
    # Plot data from both vehicles
    for i, (data, current_column, voltage_column, avg_motor_speed, soc_column, starting_soc_percentage, cutoff_soc_percentage, soc_consumed, ending_battery_voltage) in enumerate(data_list):
       
        # Define line style: solid for first vehicle, dashed for second
        line_style = 'dash' if i == 0 else 'solid'
        colors = vehicle_colors[i]  # Choose color set based on vehicle index
 
        # Plot SOC as a line plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['soc'],
            name=f'SOC - {labels[i]}',
            line=dict(color=colors['soc'], dash=line_style)
        ), secondary_y=False)
       
        # Plot Speed as scatter plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['Speed_kmh'],
            name=f'Speed - {labels[i]}',
            line=dict(color=colors['Speed_kmh'], dash=line_style)
        ), secondary_y=False)
       
        # Plot current as scatter plot on secondary y-axis
        fig.add_trace(go.Scatter(
            x=data.index, y=data[current_column],
            name=f'Current - {labels[i]}',
            line=dict(color=colors['current'], dash=line_style)
        ), secondary_y=True)
 
        # Plot voltage as scatter plot on secondary y-axis
        fig.add_trace(go.Scatter(
            x=data.index, y=data[voltage_column],
            name=f'Voltage - {labels[i]}',
            line=dict(color=colors['voltage'], dash=line_style)
        ), secondary_y=True)
 
        # Plot distance as a separate line plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['distance_km'],
            name=f'Distance - {labels[i]}',
            line=dict(color=colors['distance_km'], dash=line_style)
        ), secondary_y=False)
 
        # Plot Motor Temperature as a separate line plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['Motor_temp'],
            name=f'Motor Temperature - {labels[i]}',
            line=dict(color=colors['Motor_temp'], dash=line_style)
        ), secondary_y=False)
 
        # Plot MCU Temperature as a separate line plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['MCU_temp'],
            name=f'MCU Temperature - {labels[i]}',
            line=dict(color=colors['MCU_temp'], dash=line_style)
        ), secondary_y=False)
 
    # Update layout
    fig.update_layout(
        title='Speed, Current, Voltage, Distance',
        xaxis_title='Time',
        yaxis_title='Y1',
        yaxis2_title='Y2'
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
 
           # Plot watt-hours as a separate line plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['watt_hours'],
            name=f'Watt-hours - {labels[i]}',
            marker=dict(color='blue' if i == 0 else 'green')
        ), secondary_y=False)
 
                  # Plot distance as a separate line plot
        fig.add_trace(go.Scatter(
            x=data.index, y=data['battery_temp'],
            name=f'Battery Temperature - {labels[i]}',
            marker=dict(color='blue' if i == 0 else 'green')
        ), secondary_y=False)
 
        if i == 1:
             # Plot cell voltage difference as a separate line plot
            fig.add_trace(go.Scatter(
                x=data.index, y=data['DeltaCellVoltage'],
                name=f'DeltaCellVoltage - {labels[i]}',
                marker=dict(color='blue' if i == 0 else 'green')
            ), secondary_y=False)
 
            fig.add_trace(go.Scatter(
                x=data.index, y=data['Max_Cell_Temperature'],
                name=f'Max_Cell_Temperature - {labels[i]}',
                marker=dict(color='blue' if i == 0 else 'green')
            ), secondary_y=False)
 
 
            fig.add_trace(go.Scatter(
                x=data.index, y=data['Delta_Cell_Temperature'],
                name=f'Delta_Cell_Temperature - {labels[i]}',
                marker=dict(color='blue' if i == 0 else 'green')
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
        title='Battery Parameters',
        xaxis_title='Time',
        yaxis_title='Y1'
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
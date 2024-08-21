
from matplotlib.mlab import window_none
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import sys
import io
import openpyxl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from PIL import Image
import os
import matplotlib.dates as mdates
import mplcursors  # Import mplcursors
from contextlib import redirect_stdout
from pptx.util import Inches, Pt  # Correcting the import statement
from pptx import Presentation
from pptx.util import Inches
from docx import Document
from docx.shared import Inches
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image
from matplotlib.widgets import CheckButtons
from collections import defaultdict
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

main_folder_path = r"C:\Users\kamalesh.kb\Influx_master\lxsVsNduro\Nduro"



for subfolder in os.listdir(main_folder_path):
    subfolder_path = os.path.join(main_folder_path, subfolder)
    print(subfolder_path)
    
    # Check if subfolder starts with "Battery" and is a directory
    if os.path.isdir(subfolder_path):                
        log_file = None
        log_found = False
        
        # Iterate through files in the subfolder
        for file in os.listdir(subfolder_path):
            if file.startswith('log.') and file.endswith('.csv'):
                log_file = os.path.join(subfolder_path, file)
                print("file:",log_file)
                log_found = True
                break  # Stop searching once the log file is found
        
        # Process the log file if found
        if log_found:
            print(f"Processing log file: {log_file}")
            try:
                data = pd.read_csv(log_file)
                                # Enter the start time
                start_time_str = '06:13:00'  # Update this with your actual start time
                start_time = datetime.strptime(start_time_str, '%H:%M:%S')

                # Function to convert fractional seconds to hh:mm:ss format
                def convert_to_hhmmss(row, start_time):
                    # Calculate the time in seconds
                    seconds = row['Time'] 
                    # Add these seconds to the start time
                    new_time = start_time + timedelta(seconds=seconds)
                    # Return the time in hh:mm:ss format
                    return new_time.strftime('%H:%M:%S')

                # Apply the function to create a new column
                # data['FormattedTime'] = data.apply(convert_to_hhmmss, start_time=start_time, axis=1)
                print("file_path--------->",log_file)
                # Process your data here
            except Exception as e:
                print(f"Error processing {log_file}: {e}")



def plot_ghps(data,Path):

      # Convert the Unix timestamps to datetime
    data['DATETIME'] = pd.to_datetime(data['DATETIME'], unit='s')
 
    # Print the converted DATETIME column
    data['DATETIME'] = pd.to_datetime(data['DATETIME'])

    data['speed'] = data['MotorSpeed [SA: 02]'] * 0.0836
    print("speed----------->",data['speed'])

    # data.set_index('', inplace=True)  # Setting DATETIME as index
    data.set_index('DATETIME', inplace=True)  # Setting DATETIME as index



    fig = make_subplots(specs=[[{"secondary_y": True}]])
#     fig.add_trace(go.Scatter(x=data.index, y=-data['PackCurr [SA: 06]'], name='Pack Current', line=dict(color='blue')), secondary_y=False)
#     fig.add_trace(go.Scatter(x=data.index, y=data['MotorSpeed [SA: 02]'], name='Motor Speed[RPM]', line=dict(color='green')), secondary_y=True)
#     # fig.add_trace(go.Scatter(x=data.index, y=data['AC_Current [SA: 03]'], name='AC Current', line=dict(color='red')), secondary_y=False)
#     # fig.add_trace(go.Scatter(x=data.index, y=data['AC_Voltage [SA: 04]'] * 10, name='AC Voltage (x10)', line=dict(color='yellow')), secondary_y=False)
#     fig.add_trace(go.Scatter(x=data.index, y=data['Throttle [SA: 02]'], name='Throttle (%)', line=dict(color='Black')), secondary_y=False)
#     fig.add_trace(go.Scatter(x=data.index, y=data['SOC [SA: 08]'], name='SOC (%)', line=dict(color='Red')), secondary_y=False)
#     fig.add_trace(go.Scatter(x=data.index, y=speed, name='Speed[Km/hr]', line=dict(color='grey')), secondary_y=False)
#     fig.add_trace(go.Scatter(x=data.index, y=data['PackVol [SA: 06]'], name='PackVoltage', line=dict(color='Green')), secondary_y=False)
#     # fig.add_trace(go.Scatter(x=data.index, y=data['ALTITUDE'], name='ALTITUDE', line=dict(color='red')), secondary_y=True)

#     fig.add_trace(go.Scatter(x=data.index, y=data['FetTemp [SA: 08]'], name='BMS temperature (FET)', line=dict(color='orange')), secondary_y=True)
#     fig.add_trace(go.Scatter(x=data.index, y=data['MCU_Temperature [SA: 03]'], name='MCU temperature', line=dict(color='orange')), secondary_y=True)
#     fig.add_trace(go.Scatter(x=data.index, y=data['Motor_Temperature [SA: 03]'], name='Motor Temperature', line=dict(color='orange')), secondary_y=True)
#     fig.add_trace(go.Scatter(x=data.index, y=data['Brake_Pulse [SA: 02]'], name='Break Pulse', line=dict(color='Black')), secondary_y=True)

# #########################
#     fig.add_trace(go.Scatter(x=data.index, y=data['Ride_Ack [SA: 02]']*100, name='Ride Ack', line=dict(color='Blue')), secondary_y=True)
#     fig.add_trace(go.Scatter(x=data.index, y=data['DchgFetStatus [SA: 09]']*100, name='DchgFet Ack', line=dict(color='Purple')), secondary_y=True)
#     fig.add_trace(go.Scatter(x=data.index, y=data['ChgFetStatus [SA: 09]']*100, name='Charge Ack', line=dict(color='Red')), secondary_y=True)

#     fig.add_trace(go.Scatter(x=data.index, y=data['IgnitionStatus [SA: 0C]']*100, name='Ignition Status', line=dict(color='Yellow')), secondary_y=True)
    fig.add_trace(go.Scatter(x=data.index, y=data['speed'], name='Speed', line=dict(color='Red')), secondary_y=True)


    # fig.add_trace(go.Scatter(x=data.index, y=data['Power'], name='DC Power', line=dict(color='Red')), secondary_y=True)
    # fig.add_trace(go.Scatter(x=data.index, y=data['DeltaCellVoltage'], name='DeltaCellVoltage', line=dict(color='Purple')), secondary_y=True)

    fig.update_layout(title='Speed vs Time',
                        xaxis_title='Local localtime',
                        yaxis_title='Speed',
                        yaxis2_title='Speed')

    fig.update_xaxes(tickformat='%H:%M:%S')

    # Save the plot as an HTML file
    os.makedirs(Path, exist_ok=True)
    graph_path = os.path.join(Path, 'Log.html')
    print("graph_path")
    fig.write_html(graph_path)


    # Resetting index to default integer index
    # data.reset_index(inplace=True)

    # data.set_index('DATETIME', inplace=False)


plot_ghps(data,subfolder_path)
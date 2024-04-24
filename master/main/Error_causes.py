import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplcursors  # Import mplcursors
from matplotlib.widgets import CheckButtons  # Import CheckButtons
import numpy as np  # Import numpy for handling NaN values
import threading
import queue

import os

from openai import OpenAI

# OPENAI_API_KEY = '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'

folder_path = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\INPUT_3"
# Global variable to store visibility status of lines
line_visibility = {}
# Get the list of files in the folder
files = os.listdir(folder_path)

# Initialize variables to store file paths
log_file = None
km_file = None



for file in files:
    if file.startswith('log') and file.endswith('.csv'):
        log_file = os.path.join(folder_path, file)
    elif file.startswith('km') and file.endswith('.csv'):
        km_file = os.path.join(folder_path, file)


# Read the CSV file into a pandas DataFrame
data = pd.read_csv(log_file)
# km_data = pd.read_csv(km_file)


# Convert 'localtime' column to datetime format and set it as index
data['localtime'] = pd.to_datetime(data['localtime'])
data.set_index('localtime', inplace=True)

# Define a function to set current to zero if RPM is zero for 10 or more consecutive points
def adjust_current(row):
    adjust_current.zero_count = getattr(adjust_current, 'zero_count', 0)
    if row['MotorSpeed_340920578'] == 0:
        adjust_current.zero_count += 1
    else:
        adjust_current.zero_count = 0
    
    if adjust_current.zero_count >= 10:
        return 0
    else:
        return row['PackCurr_6']

def generate_label(fault_name, max_pack_dc_current, max_ac_current, min_pack_dc_current, fault_timestamp,
                    current_speed, throttle_percentage, relevant_data, max_battery_voltage):
    error_cause = ""
    if max_pack_dc_current < -130:
        error_cause = "battery overcurrent"
    elif max_ac_current > 220:
        error_cause = "motor overcurrent"
    elif max_battery_voltage > 69:
        error_cause = "battery overvoltage"


    scooter_mode_at_fault = relevant_data.loc[relevant_data['localtime'] == fault_timestamp, 'Mode_Ack_408094978'].iloc[0]


    # completion = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "Please provide a summary explaining why the fault occurred along with occurrence time and cause."},
    #         {"role": "system", "content": f"The fault '{fault_name}' was triggered due to {error_cause} at {fault_timestamp}."},
    #         {"role": "user", "content": f"Speed at fault occurrence: {current_speed * 0.016} km/h, Throttle percentage: {throttle_percentage} and scooter was in {scooter_mode_at_fault}."},
    #         {"role": "user", "content": f"{gpt_analyze_data(max_pack_dc_current, max_ac_current,min_pack_dc_current, current_speed, throttle_percentage, relevant_data, fault_name,max_battery_voltage,fault_timestamp,km_data)}"}

    #     ]
    # )

   # generated_messages = completion.choices[0].message.content.split('\n')

    # Print out the generated messages for debugging
   # print("Generated Messages:", generated_messages)

    # Extract content from dictionaries and join into a single string
    return

def gpt_analyze_data(max_pack_dc_current, max_ac_current, min_pack_dc_current, current_speed, throttle_percentage,
                     relevant_data, fault_name, max_battery_voltage,fault_timestamp):
    # Placeholder for GPT-analyzed statements
    analyzed_statements = []

    print(fault_name)


            # Initialize a flag to indicate if the condition is met
    current_exceeded_60A_for_90s = False

    # Iterate through the relevant data to check if current exceeded 60A for 90 seconds
    for index, row in relevant_data.iterrows():
        if row['PackCurr_6'] > 60:
            count = 0
            # Check for 90 consecutive seconds where current exceeded 60A
            for i in range(index, len(relevant_data)):
                if relevant_data.iloc[i]['PackCurr_6'] > 60:
                    count += 1
                else:
                    count = 0
                if count >= 90:
                    current_exceeded_60A_for_90s = True
                    break
        if current_exceeded_60A_for_90s:
            break


    # Add additional check statement
    if current_exceeded_60A_for_90s:
        analyzed_statements.append(
            {"role": "system",
            "content": "The DC current exceeded 60A for 90 seconds, indicating a potential overcurrent condition."})

    # Generate statements based on data analysis
    if fault_name == 'ChgPeakProt_9':
        if min_pack_dc_current > 80:
            analyzed_statements.append(
                {"role": "system",
                 "content": f"The DC Regen current exceeded the limit 60A form battery, the current limit is now {min_pack_dc_current}A."})
            
        

    # Add Motor Over Temperature analysis
    if fault_name == 'Motor_Over_Temeprature_408094978':
        if max(relevant_data['Motor_Temperature_408094979']) > 130:
            analyzed_statements.append(
                {"role": "system",
                "content": f"The motor temperature is {max(relevant_data['Motor_Temperature_408094979'])}°C exceeding 130°C, indicating potential motor overtemperature."})

            # Initialize variables to store timestamps
            t1 = fault_timestamp  # Timestamp when the error occurred
            t2 = None  # Timestamp when motor temperature was less than 90°C before the error

        
            # If t1 is found, find t2
            if t1:
                for index, row in relevant_data[::-1].iterrows():
                    if row['Motor_Temperature_408094979'] < 90 and row['localtime'] < t1:
                        t2 = row['localtime']
                        break  #

            # Print timestamps if found
            if t1 and t2:

            # Calculate the rate of change of temperature of the motor between t1 and t2
                # Find the temperature at t1 and t2
                temp_t1 = relevant_data[relevant_data['localtime'] == t1]['Motor_Temperature_408094979'].iloc[0]
                temp_t2 = relevant_data[relevant_data['localtime'] == t2]['Motor_Temperature_408094979'].iloc[0]

                # Find the time difference between t1 and t2 in seconds
                time_diff_seconds = (t1 - t2).total_seconds()

                # Calculate the rate of change of temperature
                rate_of_change = (temp_t1 - temp_t2) / (time_diff_seconds/60)

                analyzed_statements.append(
            {"role": "system",
            "content": f"the motor temperature rate of change was very high, {rate_of_change}C/m. thats why the temperature was high "})
            
                if rate_of_change > 8:
                                        # Initialize variables to store statistics
                    ac_current_values = []
                    dc_current_values = []

                    # Iterate through relevant_data between t1 and t2
                    for index, row in relevant_data.iterrows():
                        if t2 <= row['localtime'] <= t1:
                            ac_current_values.append(row['AC_Current_340920579'])
                            dc_current_values.append(row['PackCurr_6'])

                    # Calculate peak and average AC current
                    peak_ac_current = max(ac_current_values)
                    average_ac_current = sum(ac_current_values) / len(ac_current_values) if ac_current_values else 0

                    # Calculate peak and average DC current
                    peak_dc_current = min(dc_current_values)
                    average_dc_current = np.nanmean(dc_current_values)
                    # Append analyzed statements
                    analyzed_statements.append(
                        {"role": "system",
                        "content": f"During the period of temerature elevation the peak AC current was {peak_ac_current}A and the average AC current was {average_ac_current}A."})
                    analyzed_statements.append(
                        {"role": "system",
                        "content": f"During the period of temerature elevation the peak DC current was {peak_dc_current}A and the average DC current was {average_dc_current}A."})
                    analyzed_statements.append(
                        {"role": "system",
                        "content": f"If the currents are more then this might be possible that current consumptions are reason for temperature increase. this might happen due to vehcile climbing inclination/or some abstruction in wheel"})
                    

    if fault_name == 'Overcurrent_Fault_408094978' or fault_name=='DchgOverCurrProt_9':        
        print("insde the faulut")
        if max_ac_current > 220:
            analyzed_statements.append(
                {"role": "system", "content": "The AC current exceeded the limit, suggesting a potential motor overcurrent."})
        if current_speed * 0.016 < 10:
            analyzed_statements.append(
                {"role": "system",
                 "content": "The vehicle was moving at a low speed, which may indicate challenging terrain or obstacles."})
        if throttle_percentage > 80:
            analyzed_statements.append(
                {"role": "system", "content": "The throttle percentage was high, indicating high torque demand."})
        if max_ac_current > 220 and throttle_percentage > 80:
            analyzed_statements.append(
                {"role": "system",
                 "content": "The motor overcurrent could be triggered due to high torque demand, possibly caused by obstructions or the wheel being stuck for a prolonged period."})
#### should go on to different catogry 
        if max_pack_dc_current < -60 and continuous_dc_exceeded_limit(max_pack_dc_current, relevant_data):
            print("insdide the max dc current ")
            analyzed_statements.append(
                {"role": "system",
                 "content": f"The DC current exceeded the continuous maximum limit of 60A for 90 seconds, indicating a potential battery overcurrent."})

        if max_pack_dc_current < -120:
            analyzed_statements.append(
                {"role": "system",
                 "content": f"The DC current exceeded the the max current allowed by the battery i.e. 120A, the current is {max_pack_dc_current}"})
   
   
   
    if fault_name == 'DriveError_Controller_OverVoltag_408094978':
        if max_battery_voltage > 70:
            analyzed_statements.append(
                {"role": "user",
                 "content": f"The controller voltage {max_battery_voltage}V exceeded 70V, was actual suggesting potential overvoltage during high regenerative braking."})
                
            # Check if ChgFetStatus_9 has gone to zero and if negative current exceeds -60A
            if 'ChgFetStatus_9' in relevant_data and 'PackCurr_6' in relevant_data:
                chg_fet_status = relevant_data['ChgFetStatus_9']
                pack_dc_current = relevant_data['PackCurr_6']
                
                analyzed_statements.append(
                    {"role": "user",
                    "content": f"Over ovltage error is occured due to ChgFetStatus_9 going to 0 means battery has disconnected."})


                # Check if ChgFetStatus_9 has gone to zero and negative current exceeds -60A
            if (chg_fet_status == 0).any() and (pack_dc_current * -1 < -60).any():
                    analyzed_statements.append(
                        {"role": "user",
                        "content": f"ChgFetStatus_9 went to zero because negative current was {pack_dc_current*-1} exceeding -60A,  suggesting potential Overcurrent during high regenerative braking."})

                    prev_mode_value = None
                    timestamp = None
            
                    # Additional condition to check the rate of change of RPM
                    if 'MotorSpeed_340920578' in relevant_data and 'PackCurr_6' in relevant_data:
                        rpm_series = relevant_data['MotorSpeed_340920578']
                        pack_curr_series = relevant_data['PackCurr_6']
                        timestamp_series = relevant_data['localtime']
                        
                        # Create a DataFrame with RPM values, 'PackCurr_6', and corresponding timestamps
                        df = pd.DataFrame({'MotorSpeed_340920578': rpm_series, 'PackCurr_6': pack_curr_series, 'Timestamp': timestamp_series})
                        
                        # Find the timestamp when 'PackCurr_6' becomes more than 60
                        timestamp_pack_curr_exceed_60 = df.loc[df['PackCurr_6'] > 60, 'Timestamp'].iloc[0]
                        print(timestamp_pack_curr_exceed_60)

                        
                        # Find t2, 1.5 seconds before t1
                        timestamp_t2 = timestamp_pack_curr_exceed_60 - pd.Timedelta(seconds=1.5)
                        print(timestamp_t2)
                        
                        # Find motor speed at t1 and t2 only if DataFrame is not empty
                        if not df.empty:
                            # Find motor speed at t1 when current > 60A
                            motor_speed_t1 = df.loc[df['Timestamp'] == timestamp_pack_curr_exceed_60, 'MotorSpeed_340920578']

                            if not motor_speed_t1.empty:
                                motor_speed_t1 = motor_speed_t1.iloc[0]
                                print("Motor speed at t1 (when current > 60A):", motor_speed_t1)


                            # Find motor speed at t2, 1.5 seconds before t1
                            nearest_timestamp_t2 = df.loc[(df['Timestamp'] <= timestamp_t2), 'Timestamp'].max()
                           # print(nearest_timestamp_t2)

                            motor_speed_t2 = df.loc[df['Timestamp'] == nearest_timestamp_t2, 'MotorSpeed_340920578']    

                            if not motor_speed_t2.empty:
                                motor_speed_t2 = motor_speed_t2.iloc[0]
                                print("Motor speed at t2 (1.5 seconds before t1):", motor_speed_t2)
                                print("cahnge in RPM", motor_speed_t2-motor_speed_t1)



                                                        # Calculate the rate of change of RPM (RPM/s)

                            rate_of_change_rpm = (motor_speed_t2-motor_speed_t1) / 1.5
                            analyzed_statements.append({
                "role": "user",
                "content": f"The rate of decrease of motor speed RPM is {rate_of_change_rpm}RPMs/sec, if exceeds 100 RPMs/SEC, potentially causes high regen current. If not, Rate of cange of RPM is not the cause"
            })

                    # Check if there's a change in Mode_Ack_408094978
                    if 'Mode_Ack_408094978' in relevant_data:
                        mode_ack = relevant_data['Mode_Ack_408094978']
                        unique_values = np.unique(mode_ack)  # Get unique values, handling NaN


                   
                        if len(unique_values) > 2:

                                                                    # Assuming relevant_data['Mode_Ack_408094978'] contains the data
                            mode_ack_series = relevant_data['Mode_Ack_408094978']
                            timestamp_series = relevant_data['localtime']  # Assuming relevant_data['localtime'] contains the timestamps

                            # Create a DataFrame with mode values and corresponding timestamps
                            df = pd.DataFrame({'Mode_Ack_408094978': mode_ack_series, 'Timestamp': timestamp_series})

                            # Filter DataFrame to rows where mode is 1
                            mode_1_df = df[df['Mode_Ack_408094978'] == 1][::-1]

                            # If there are rows where mode is 1, get the first occurrence
                            if not mode_1_df.empty:
                                first_occurrence = mode_1_df.iloc[0]
                                exact_time_mode_1 = first_occurrence['Timestamp']
                            
                                print("Timestamp of mode change:", exact_time_mode_1)
                            analyzed_statements.append({
    "role": "user",
    "content": f"There is a sudden change in mode at ({exact_time_mode_1}) this may cause a high rate of change of motor RPM"
})                    


                                                # Assuming relevant_data['PackCurr_6'] contains the data
                            pack_curr_series = relevant_data['PackCurr_6']
                            timestamp_series = relevant_data['localtime']  # Assuming relevant_data['localtime'] contains the timestamps

                            # Create a DataFrame with 'PackCurr_6' values and corresponding timestamps
                            df = pd.DataFrame({'PackCurr_6': pack_curr_series, 'Timestamp': timestamp_series})

                            # Filter DataFrame to rows where 'PackCurr_6' is less than -60
                            less_than_minus_60_df = df[df['PackCurr_6'] > 60]

                            # If there are rows where 'PackCurr_6' is less than -60, get the first occurrence
                            if not less_than_minus_60_df.empty:
                                first_occurrence = less_than_minus_60_df.iloc[0]
                                timestamp = first_occurrence['Timestamp']
                                print("Timestamp when 'PackCurr_6' goes below -60:", timestamp)
                            
                                                    # Assuming relevant_data['MotorSpeed_340920578'] contains the motor speed data
                            motor_speed_series = relevant_data['MotorSpeed_340920578']
                            timestamp_series = relevant_data['localtime']  # Assuming relevant_data['localtime'] contains the timestamps

                            # Create a DataFrame with motor speed values and corresponding timestamps
                            df = pd.DataFrame({'MotorSpeed': motor_speed_series, 'Timestamp': timestamp_series})

                            # Filter DataFrame to rows where timestamps are between exact_time_mode_1 and timestamp
                            filtered_df = df[(df['Timestamp'] >= exact_time_mode_1) & (df['Timestamp'] <= timestamp)]

                            # Calculate the motor speed drop as the difference between maximum and minimum motor speed within the specified time range
                            motor_speed_drop = filtered_df['MotorSpeed'].max() - filtered_df['MotorSpeed'].min()

                            # Calculate the time difference in seconds and milliseconds
                            time_difference_seconds = (timestamp - exact_time_mode_1).total_seconds()
                            time_difference_milliseconds = time_difference_seconds * 1000

                            print("Motor Speed Drop:", motor_speed_drop)
                            print("Time taken for motor speed drop (seconds):", time_difference_seconds)
                            print("Time taken for motor speed drop (milliseconds):", time_difference_milliseconds)


                            # Calculate the rate of change of RPM (RPM/s)
                            time_difference_seconds = (timestamp_pack_curr_exceed_60 - timestamp_t2).total_seconds()
                            rate_of_change_rpm = motor_speed_drop / time_difference_seconds

                            print("Rate of change of RPM:", rate_of_change_rpm)

    if fault_name == 'Controller_Over_Temeprature_408094978':
            # Initialize variable to store minimum PcbTemp_12 value at the time of error
            min_PcbTemp_12_at_error = float('inf')

            # Iterate over relevant_data to find minimum PcbTemp_12 at error
            for index, row in relevant_data.iterrows():
                if row[fault_name] == 1 and row['PcbTemp_12'] < min_PcbTemp_12_at_error:
                    min_PcbTemp_12_at_error = row['PcbTemp_12']

            # Check for no faults found condition
            if min_PcbTemp_12_at_error == float('inf'):
                print("No faults found for", fault_name)
            else:
                # Print the minimum PcbTemp_12 at error
                print("Minimum PcbTemp_12 at error:", min_PcbTemp_12_at_error)
            pcb_temp_threshold = min_PcbTemp_12_at_error # I got 61 from csv
                # Find the PCB temperature when the error occurred
            pcb_temp_at_error = relevant_data.loc[relevant_data[fault_name] == 1, 'PcbTemp_12'].iloc[0]
            print("PCB Temperature at error:", pcb_temp_at_error)

            # Check if the PCB temperature exceeds the defined overtemperature threshold
            if pcb_temp_at_error >= pcb_temp_threshold:
                analyzed_statements.append({
                    "role": "system",
                    "content": f"The PCB temperature ({pcb_temp_at_error}°C) exceeded the overtemperature threshold of {pcb_temp_threshold}°C, which may be the cause of Controller Over Temperature condition."
                })
                        # Initialize variable to store minimum MCU_Temperature_408094979 value at the time of error
                min_MCU_Temperature_at_error = float('inf')

                # Iterate over relevant_data to find minimum MCU_Temperature_408094979 at error
                for index, row in relevant_data.iterrows():
                    if row[fault_name] == 1 and row['MCU_Temperature_408094979'] < min_MCU_Temperature_at_error:
                        min_MCU_Temperature_at_error = row['MCU_Temperature_408094979']

                # Check for no faults found condition
                if min_MCU_Temperature_at_error == float('inf'):
                    print("No faults found for", fault_name)
                else:
                    # Print the minimum MCU_Temperature_408094979 at error
                    print("Minimum MCU_Temperature_408094979 at error:", min_MCU_Temperature_at_error)
                mcu_temp_threshold = min_MCU_Temperature_at_error # 83 from csv file
                        # Find the MCU temperature when the error occurred
                mcu_temp_at_error = relevant_data.loc[relevant_data[fault_name] == 1, 'MCU_Temperature_408094979'].iloc[0]
                print("MCU Temperature at error:", mcu_temp_at_error)

                # Check if the MCU temperature exceeds the defined overtemperature threshold
                if mcu_temp_at_error >= mcu_temp_threshold:
                    analyzed_statements.append({
                        "role": "system",
                        "content": f"The MCU temperature ({mcu_temp_at_error}°C) exceeded the overtemperature threshold of {mcu_temp_threshold}°C, which may be the cause of PCB over temperature condition."
                    })

    if fault_name == 'CellUnderVolWarn_9':
        # Function to analyze cell voltages
        def analyze_cell_voltages():
            # Extract cell voltages and their corresponding cell numbers
            cell_voltages = {}
            for column in data.columns:
                if column.startswith('CellVol') and len(column) == 11:
                    cell_num = column.split('_')[0][-2:]  # Extract cell number from column name
                    cell_voltages[cell_num] = data[column].min()  # Store the minimum voltage for each cell
            return cell_voltages

        # Analyze cell voltages and get the data
        cell_voltages = analyze_cell_voltages()
        print("Cell voltage: ",cell_voltages)

        # Find the cell with the lowest voltage
        lowest_voltage_cell = min(cell_voltages, key=cell_voltages.get)
        lowest_voltage = cell_voltages[lowest_voltage_cell]
        print(f"Cell {lowest_voltage_cell} has the lowest voltage: {lowest_voltage}")

        if lowest_voltage < 3:
            print("Some Cells has voltage less than the threshold which may be the reason for the cause of CellUnderVolWarn_9.")

                # Add code to retrieve SOC at error
                # SOC_at_error = relevant_data.loc[relevant_data[fault_name] == 1, 'SOC_8'].iloc[-1]
                # print("SOC at error:", SOC_at_error)


        # Call the function to calculate the rate of change of voltage
        calculate_voltage_rate_of_change(data,fault_timestamp)
        print("Continuous high current draw is leading to a decrease in cell voltages, triggering the CellUnderVoltageWarning.")


        
    if fault_name == 'VCU_thermal_runaway':

        print("here")

            #                 if motor_speed_drop > 150:
            #                     analyzed_statements.append({
            #     "role": "user",
            #     "content": f"The rate of change of motor speed (RPM) ({rate_of_change_rpm}) exceeds 150 RPM, potentially causing high current to the battery."
            # })


    print("here",analyzed_statements)
    return analyzed_statements

def continuous_dc_exceeded_limit(max_pack_dc_current, data):
    # Set the threshold for continuous DC current limit
    dc_current_threshold = 60  # Amperes

    # Set the duration for continuous DC current limit in seconds
    duration_threshold_seconds = 90

    # Check if the maximum DC current exceeds the threshold
    if abs(max_pack_dc_current) > dc_current_threshold:
        # Get the index of the first occurrence of the maximum DC current exceeding the threshold
        start_index = data.index[data['PackCurr_6'] < -dc_current_threshold][0]

        # Find the start and end time based on local time
        start_time = data.loc[start_index, 'localtime']
        end_time = start_time + pd.Timedelta(seconds=duration_threshold_seconds)

        # Iterate through the data within the time window
        for index, row in data.iterrows():
            if start_time <= row['localtime'] <= end_time:
                # Check if current is less than -60
                if row['PackCurr_6'] < -60:
                    return True  # Continuous DC current below -60 found within the time window

    return False  # Continuous DC current below -60 not found within the time window


#code for finding the rate of change of each cells voltage
def calculate_voltage_rate_of_change(data,fault_timestamp):
    # Define the time window before the fault occurrence
    time_window = pd.Timedelta(seconds=10)

    # Convert fault_timestamp to Timestamp if not already
    fault_timestamp2 = fault_timestamp
    print("fault_timestamp: ",fault_timestamp2)

    # Calculate the start time of the window
    start_time_window = fault_timestamp2 - time_window
    print("start_time_window: ",start_time_window)

    # Assuming 'data' is your DataFrame and 'start_time_window' and 'fault_timestamp2' are defined
    data_within_window = data[(data.index >= start_time_window) & (data.index <= fault_timestamp2)]
    # print(data_within_window)

    # Selecting columns representing cell voltages
    cell_voltage_columns = [col for col in data_within_window.columns if col.startswith('CellVol')]
    

    # Calculate the time difference between the first and last timestamps in milliseconds
    time_elapsed_ms = (data_within_window.index[-1] - data_within_window.index[0]).total_seconds() * 1000

    # Calculate the rate of change for each cell voltage column
    rate_of_change_cells = {}
    for col in cell_voltage_columns:
        first_value = data_within_window[col].iloc[0]
        last_value = data_within_window[col].iloc[-1]
        rate_of_change_cells[col] = (last_value - first_value) / time_elapsed_ms

    # Print rate of change for each cell
    for col, rate in rate_of_change_cells.items():
        print(f"Cell {col}: Rate of change = {rate} mV/ms")

    # Calculate the average rate of change across all cells
    average_rate_of_change = sum(rate_of_change_cells.values()) / len(rate_of_change_cells)

    # print("Average rate of change across all cells:", average_rate_of_change, "mV/ms")
    if average_rate_of_change < 5.5:
        print("The observed average rate of change in cell voltage suggests a notable decline over time, with an average rate of change of:", average_rate_of_change, "mV/ms")



def analyze_fault(csv_file, fault_name):
    # Load CSV data into a DataFrame
    data = pd.read_csv(csv_file)
    # km_data = pd.read_csv(km_file)

    
    # Convert 'localtime' to datetime
    data['localtime'] = pd.to_datetime(data['localtime'])

    # Check if the column exists in the DataFrame
    if fault_name not in data.columns:
        print(f"Column '{fault_name}' not found in the DataFrame.")
        return

    # Filter rows where fault occurred
    fault_data = data[data[fault_name] == 1]

    if fault_data.empty:
        print(f"No {fault_name} data found.")
        return
    else:
        print(f"{fault_name} data found.")

    # Sort fault data by 'localtime' in ascending order
    fault_data.sort_values(by='localtime', inplace=True)

    # Extract timestamp of the first occurrence of the fault
    fault_timestamp = fault_data.iloc[0]['localtime']

    # Calculate start time (5 minutes before the fault)
    start_time = fault_timestamp - pd.Timedelta(minutes=5)
    # Calculate end time (2 minutes after the fault)
    end_time = fault_timestamp + pd.Timedelta(minutes=2)

    # Filter data for 5 minutes before and after the fault
    relevant_data = data[(data['localtime'] >= start_time) & (data['localtime'] <= end_time)]

    print(relevant_data['localtime'])

    # Find the maximum AC and DC currents before the fault occurrence
    max_ac_current = relevant_data['AC_Current_340920579'].max()
    max_dc_current = relevant_data['BatteryCurrent_340920578'].max()
    max_pack_dc_current = relevant_data['PackCurr_6'].min()
    min_pack_dc_current = relevant_data['PackCurr_6'].max()

    # Find maximum battery voltage
    max_battery_voltage = (relevant_data['BatteryVoltage_340920578'].max())*10

    # Capture current speed and throttle percentage at fault occurrence
    current_speed = fault_data.loc[fault_data['localtime'] == fault_timestamp, 'MotorSpeed_340920578'].values[0]
    throttle_percentage = fault_data.loc[fault_data['localtime'] == fault_timestamp, 'Throttle_408094978'].values[0]


    plot(relevant_data, fault_timestamp)


    print("Occurrence Time:", fault_timestamp)
    print("Maximum AC Current before fault:", max_ac_current, "A")
    print("Maximum DC Current before fault from MCU:", max_dc_current, "A")
    print("Maximum DC Current before fault from Battery:", max_pack_dc_current, "A")
    print("Maximum Battery Voltage:", max_battery_voltage, "V")
    generate_label(fault_name, max_pack_dc_current, max_ac_current, min_pack_dc_current, fault_timestamp,current_speed, throttle_percentage, relevant_data, max_battery_voltage)



def plot(relevant_data, fault_timestamp):
    # Create a figure and axes for plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Define lines to be plotted
    lines = {}

    # Plot 'PackCurr_6' on primary y-axis
    line1, = ax1.plot(relevant_data['localtime'], -relevant_data['PackCurr_6'], color='blue', label='PackCurr_6')
    ax1.set_ylabel('Pack Current (A)', color='blue')
    ax1.yaxis.set_label_coords(-0.1, 0.7)  # Adjust label position
 
    # Create secondary y-axis for 'MotorSpeed_340920578' (RPM)
    ax2 = ax1.twinx()
    line2, = ax2.plot(relevant_data['localtime'], relevant_data['MotorSpeed_340920578'], color='green', label='Motor Speed')
    ax2.set_ylabel('Motor Speed (RPM)', color='green')
 
    # Add 'AC_Current_340920579' to primary y-axis
    line3, = ax1.plot(relevant_data['localtime'], relevant_data['AC_Current_340920579'], color='red', label='AC Current')
 
    # Add 'AC_Voltage_340920580' scaled to 10x to the left side y-axis
    line4, = ax1.plot(relevant_data['localtime'], relevant_data['AC_Voltage_340920580'] * 10, color='orange', label='AC Voltage (x10)')
 
    # Add 'Throttle_408094978' to the left side y-axis
    line5, = ax1.plot(relevant_data['localtime'], relevant_data['Throttle_408094978'], color='lightgray', label='Throttle (%)')
 
    # Add 'DchgFetStatus_9*10' to the left side y-axis
    line6, = ax1.plot(relevant_data['localtime'], relevant_data['DchgFetStatus_9'] * 10, color='purple', label='DchgFetStatus_9 (x10)')
 
    # Add 'ChgFetStatus_9*10' to the left side y-axis
    line7, = ax1.plot(relevant_data['localtime'], relevant_data['ChgFetStatus_9'] * 10, color='brown', label='ChgFetStatus_9 (x10)')
 
    # Add 'BatteryVoltage_340920578*10' to the left side y-axis
    line8, = ax1.plot(relevant_data['localtime'], relevant_data['BatteryVoltage_340920578'] * 10, color='magenta', label='BatteryVoltage_340920578 (x10)')
 
    line9, = ax1.plot(relevant_data['localtime'], relevant_data['SOC_8'] , color='magenta', label='SOC_8 ')
 
    line10, = ax1.plot(relevant_data['localtime'], relevant_data['Mode_Ack_408094978'] *10, color='green', label='Mode_Ack_408094978 ')

    line11, = ax1.plot(relevant_data['localtime'], relevant_data['Controller_Over_Temeprature_408094978'] , color='green', label='Controller_Over_Temperature_408094978 ')
    line12, = ax1.plot(relevant_data['localtime'], relevant_data['PcbTemp_12'] , color='green', label='PcbTemp_12')
    line13, = ax1.plot(relevant_data['localtime'], relevant_data['MCU_Temperature_408094979'] , color='green', label='MCU_Temperature_408094979')
    line14, = ax1.plot(relevant_data['localtime'], relevant_data['Motor_Temperature_408094979'] , color='green', label='Motor_Temperature_408094979')
    
    # Hide the y-axis label for 'AC_Current_340920579'
    ax1.get_yaxis().get_label().set_visible(False)

    # Set x-axis label and legend
    ax1.set_xlabel('Local Time')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # Add a title to the plot
    plt.title('Battery Pack, Motor Data, and Throttle')

    # Format x-axis ticks as hours:minutes:seconds
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    # Set grid lines lighter
    ax1.grid(True, linestyle=':', linewidth=0.5, color='gray')
    ax2.grid(True, linestyle=':', linewidth=0.5, color='gray')

    # Enable cursor for data points
    mplcursors.cursor(hover=True)

    # Create checkboxes
    fig_check, ax_check = plt.subplots(figsize=(8, 6))
    labels = ('PackCurr_6', 'AC_Current_340920579', 'MotorSpeed_340920578', 'AC_Voltage_340920580', 'Throttle_408094978', 'DchgFetStatus_9', 'ChgFetStatus_9', 'BatteryVoltage_340920578','SOC_8','Mode_Ack_408094978','Controller_Over_Temperature_408094978','PcbTemp_12','MCU_Temperature_408094979','Motor_Temperature_408094979')
    lines = [line1, line3, line2, line4, line5, line6, line7, line8, line9, line10,line11, line12,line13,line14]

    visibility = [line.get_visible() for line in lines]
    check = CheckButtons(ax_check, labels, visibility)

    def func(label):
        index = labels.index(label)
        lines[index].set_visible(not lines[index].get_visible())
        print(lines[index].set_visible(not lines[index].get_visible()))
        plt.draw()


    check.on_clicked(func)

    plt.show()

def detect_vcu_error(km_file):



    data = pd.read_csv(km_file)

    data = data.iloc[::-1]

    

        # Convert 'localtime' to datetime
    data['localtime'] = pd.to_datetime(data['localtime'])

    
    anomaly_detected = False 

    error_detected = True  # Initialize error_detected as True by default
   
    anom =0
    for index, row in data.iterrows():
        if row['DriveStatus1_Ride_418513673'] == 0 and row['DchgFetStatus_9'] == 1 and row['IgnitionStatus_12'] == 1 :
          
            t1 = row['localtime']  # Timestamp when DriveStatus transitioned to 0
            
            t2 = t1 - pd.Timedelta(seconds=5)  # 5 seconds before t1
            
            # Find the index corresponding to t2
            t2_index = data[data['localtime'] <= t2].index.min()
            
            # If t2_index is NaN, find the nearest index to t2
            if pd.isna(t2_index):
                nearest_index = (data['localtime'] - t2).abs().idxmin()
                t2 = data.iloc[nearest_index]['localtime']
                t2_index = nearest_index
                        
            ignite_flag = False
            
            # Iterate from t2_index to t1_index
            for i in range(t2_index, -1, -1):
                if data.loc[i, 'localtime'] > t1:
                    ignite_flag = True
                    break
                if data.loc[i, 'Brake_Pulse_408094978'] == 1 and data.loc[i, 'Park_Pulse_408094978'] == 1:
                    break
            
            # If Brake and Park signals were both used within the window, no error detected


            if ignite_flag:

                detected_components = []  # List to store detected temperature components

                error_detected = True
                if ignite_flag:
                    for i in range(t2_index, -1, -1):
                        if data.loc[i, 'localtime'] > t1:
                            break
                        # Case number one: Thermal runaway
                        fet_temp_threshold = 70
                        batt_max_temp_threshold = 65
                        pcb_thresh_temp = 60
                        motor_thresh_temp = 130
                        motor_controller_thresh_temp = 85
                        max_motor_temp = 160
                        max_motor_controller_temp = 100
                        max_pcb_temp = 80
                        max_mosfet_temp = 80
                                                                                    
                                                                    
                        if (data.loc[i, 'FetTemp_8'] > fet_temp_threshold):
                            detected_components.append(f"Fet temperature ({data.loc[i, 'FetTemp_8']}°C > {fet_temp_threshold}°C)")
                        if any(data.loc[i, ['Temp1_10', 'Temp2_10', 'Temp3_10', 'Temp4_10', 'Temp5_10',
                                            'Temp6_10', 'Temp7_10', 'Temp8_10']] > batt_max_temp_threshold):
                            detected_components.append(f"Battery temperature (one or more components > {batt_max_temp_threshold}°C)")
                        if (data.loc[i, 'PcbTemp_12'] > pcb_thresh_temp):
                            detected_components.append(f"PCB temperature ({data.loc[i, 'PcbTemp_12']}°C > {pcb_thresh_temp}°C)")
                        if (data.loc[i, 'MCU_Temperature_408094979'] > motor_controller_thresh_temp):
                            detected_components.append(f"Motor Controller temperature ({data.loc[i, 'MCU_Temperature_408094979']}°C > {motor_controller_thresh_temp}°C)")
                        if (data.loc[i, 'Motor_Temperature_408094979'] > motor_thresh_temp):
                            detected_components.append(f"Motor temperature ({data.loc[i, 'Motor_Temperature_408094979']}°C > {motor_thresh_temp}°C)")
                        if (data.loc[i, 'Motor_Temperature_408094979'] > max_motor_temp):
                            detected_components.append(f"Exceeding maximum Motor temperature ({data.loc[i, 'Motor_Temperature_408094979']}°C > {max_motor_temp}°C)")
                        if (data.loc[i, 'MCU_Temperature_408094979'] > max_motor_controller_temp):
                            detected_components.append(f"Exceeding maximum Motor Controller temperature ({data.loc[i, 'MCU_Temperature_408094979']}°C > {max_motor_controller_temp}°C)")
                        if (data.loc[i, 'PcbTemp_12'] > max_pcb_temp):
                            detected_components.append(f"Exceeding maximum PCB temperature ({data.loc[i, 'PcbTemp_12']}°C > {max_pcb_temp}°C)")
                        if (data.loc[i, 'FetTemp_8'] > max_mosfet_temp):
                            detected_components.append(f"Exceeding maximum MOSFET temperature ({data.loc[i, 'FetTemp_8']}°C > {max_mosfet_temp}°C)")
                            
                        # If any components are detected, print the thermal runaway message
                if detected_components and anomaly_detected == False :
                    thermal_runaway_printed = True
                    detected_components = list(set(detected_components))

                    print("Thermal runaway detected due to the following temperature components:")

                    print(", ".join(detected_components))
                    anomaly_detected = True
                    print("Number of times - ",anom+1,", at ",t1)
        
        elif anomaly_detected and row['DriveStatus1_Ride_418513673'] == 1:
            anomaly_detected = False
            anom = anom + 1






    return error_detected


#client = OpenAI()

# Call the function for 'ChgPeakProt_9'
#analyze_fault(log_file, 'DriveError_Controller_OverVoltag_408094978',km_file)
#analyze_fault(log_file, 'Motor_Over_Temeprature_408094978',km_file)
#analyze_fault(log_file, 'Overcurrent_Fault_408094978',km_file)


# analyze_fault(log_file, 'DchgOverCurrProt_9',km_file)


#analyze_fault(log_file, 'VCU_thermal_runaway',km_file)
#analyze_fault(log_file, 'CellUnderVolWarn_9',km_file)
#analyze_fault(log_file, 'Controller_Over_Temeprature_408094978',km_file)




detect_vcu_error(log_file)

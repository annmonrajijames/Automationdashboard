import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplcursors  # Import mplcursors
from matplotlib.widgets import CheckButtons  # Import CheckButtons
import numpy as np  # Import numpy for handling NaN values
 
import os
 
from openai import OpenAI
 
#OPENAI_API_KEY = 'Enter OpenAPI key'
 
folder_path = r"C:\Work\Git_Projects\Automationdashboard\Automationdashboard"
 
# Get the list of files in the folder
files = os.listdir(folder_path)
 
# Initialize variables to store file paths
log_file = None
 
# Find files starting with 'log' and 'km'
for file in files:
    if file.startswith('log') and file.endswith('.csv'):
        log_file = os.path.join(folder_path, file)
 
# Read the CSV file into a pandas DataFrame
data = pd.read_csv(log_file)
 
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
 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Please provide a summary explaining why the fault occurred along with occurrence time and cause."},
            {"role": "system", "content": f"The fault '{fault_name}' was triggered due to {error_cause} at {fault_timestamp}."},
            {"role": "user", "content": f"Speed at fault occurrence: {current_speed * 0.016} km/h, Throttle percentage: {throttle_percentage}."},
            {"role": "user", "content": f"{gpt_analyze_data(max_pack_dc_current, max_ac_current,min_pack_dc_current, current_speed, throttle_percentage, relevant_data, fault_name,max_battery_voltage)}"}
 
        ]
    )
 
    generated_messages = completion.choices[0].message.content.split('\n')
 
    # Print out the generated messages for debugging
    print("Generated Messages:", generated_messages)
 
    # Extract content from dictionaries and join into a single string
    return
 
def gpt_analyze_data(max_pack_dc_current, max_ac_current, min_pack_dc_current, current_speed, throttle_percentage,
                     relevant_data, fault_name, max_battery_voltage):
    # Placeholder for GPT-analyzed statements
    analyzed_statements = []
 
    print(fault_name)
 
    ###################
    if fault_name == 'Controller_Undervoltage_408094978':
    # Define the threshold voltage for undervoltage
        undervoltage_threshold = 48  # Adjust the threshold as needed

    # Find the voltage when the error occurred and multiply by 10
        voltage_at_error = relevant_data.loc[relevant_data[fault_name] == 1, 'BatteryVoltage_340920578'].iloc[0] * 10
        print("Voltage at error:", voltage_at_error)

        # Check if the maximum battery voltage is less than the threshold
        if voltage_at_error < undervoltage_threshold:
            analyzed_statements.append({
                "role": "system",
                "content": f"The maximum battery voltage ({voltage_at_error}V) is below the undervoltage threshold."
            })

            # Check for Discharge FET status and high pack current if voltage is low
            if 'DchgFetStatus_9' in relevant_data:
                dchg_fet_status = relevant_data['DchgFetStatus_9'].iloc[0]  # Assuming it's a binary status (1 for on, 0 for off)

                if dchg_fet_status == 1:  # Discharge FET is low
                    analyzed_statements.append(
                    # Check if the pack current is too high when Discharge FET is low
                    {
                    "role": "system",
                    "content": "The Discharge FET is low, which is causing the voltage to be low."
                    })

                    if max_pack_dc_current < -120:
                        analyzed_statements.append({
                            "role": "system",
                            "content": f"The DC current exceeded the max current allowed by the battery i.e. 120A, the current is {max_pack_dc_current}. Also, this High current caused the Discharge FET to become low, resulting in low voltage."
                        })

    ###################
            
    # Generate statements based on data analysis
    if fault_name == 'ChgPeakProt_9':
        if min_pack_dc_current > 80:
            analyzed_statements.append(
                {"role": "system",
                 "content": f"The DC Regen current exceeded the limit 60A form battery, the current limit is now {min_pack_dc_current}A."})
 
    if fault_name == 'Overcurrent_Fault_408094978':
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
            analyzed_statements.append(
                {"role": "system",
                 "content": "The DC current exceeded the continuous maximum limit for 90 seconds, indicating a potential battery overcurrent."})
 
        if max_pack_dc_current < -120:
            analyzed_statements.append(
                {"role": "system",
                 "content": f"The DC current exceeded the the max current allowed by the battery i.e. 120A, the current is {max_pack_dc_current}"})
#############################################
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
 
###########################################################################################################################
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
                            print(nearest_timestamp_t2)
 
                            motor_speed_t2 = df.loc[df['Timestamp'] == nearest_timestamp_t2, 'MotorSpeed_340920578']    
 
                            if not motor_speed_t2.empty:
                                motor_speed_t2 = motor_speed_t2.iloc[0]
                                print("Motor speed at t2 (1.5 seconds before t1):", motor_speed_t2)
 
 
                    # Check if there's a change in Mode_Ack_408094978
                    if 'Mode_Ack_408094978' in relevant_data:
                        mode_ack = relevant_data['Mode_Ack_408094978']
                        unique_values = np.unique(mode_ack)  # Get unique values, handling NaN
 
 
                   
                        if len(unique_values) > 1:
 
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
 
                             # Check if SOC is less than 30 at the time of mode change
                            if 'SOC_8' in relevant_data:
                                soc_data = relevant_data['SOC_8']
                                soc_at_mode_change = soc_data[timestamp_series == exact_time_mode_1].iloc[0]
                                if soc_at_mode_change < 30:
                                    analyzed_statements.append({
                                        "role": "user",
                                        "content": f"The mode change at time ({exact_time_mode_1}) was due to SOC being less than 30%."
                                    })
 
                                    # Speak with GPT about the mode change reason
                                    analyzed_statements.append({
                                        "role": "gpt",
                                        "content": f"Mode changed at time ({exact_time_mode_1}) due to low state of charge (SOC < 30%)."
                                    })
 
 
 
#############################
                            #analyzed_statements.append({
    #"role": "user",
    #"content": f"Mode change at time ({exact_time_mode_1}) could be the reason for the sudden reduction in speed and the resulting high current greater than 60A."
#})
#############################                    
 
 
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
 
#################################
                            # Calculate the rate of change of RPM (RPM/s)
                            time_difference_seconds = (timestamp_pack_curr_exceed_60 - timestamp_t2).total_seconds()
                            rate_of_change_rpm = motor_speed_drop / time_difference_seconds
 
                            print("Rate of change of RPM:", rate_of_change_rpm)
 
                            if motor_speed_drop > 150:
                                analyzed_statements.append({
                "role": "user",
                "content": f"The rate of change of motor speed (RPM) ({rate_of_change_rpm}) exceeds 150 RPM, potentially causing high current to the battery."
            })
################################
 
    print("here",analyzed_statements)
    return analyzed_statements
 
 
def continuous_dc_exceeded_limit(max_pack_dc_current, data):
    # Set the threshold for continuous DC current limit
    dc_current_threshold = 60  # Amperes
 
    # Set the duration for continuous DC current limit in seconds
    duration_threshold_seconds = 90
 
    # Check if the maximum DC current exceeds the threshold
    if max_pack_dc_current > dc_current_threshold:
        # Get the index of the first occurrence of the maximum DC current exceeding the threshold
        start_index = data.index[data['PackCurr_6'] > dc_current_threshold][0]
 
        # Calculate the end index considering the duration threshold
        end_index = start_index + pd.Timedelta(seconds=duration_threshold_seconds)
 
        # Check if the DC current exceeds the threshold continuously for the duration threshold
        continuous_exceeded = all(data.loc[start_index:end_index, 'PackCurr_6'] > dc_current_threshold)
 
        return continuous_exceeded
 
    return False
 
 
def analyze_fault(csv_file, fault_name):
    # Load CSV data into a DataFrame
    data = pd.read_csv(csv_file)
   
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
 
 
    generate_label(fault_name, max_pack_dc_current, max_ac_current, min_pack_dc_current, fault_timestamp,current_speed, throttle_percentage, relevant_data, max_battery_voltage)
 
    print("Occurrence Time:", fault_timestamp)
    print("Maximum AC Current before fault:", max_ac_current, "A")
    print("Maximum DC Current before fault from MCU:", max_dc_current, "A")
    print("Maximum DC Current before fault from Battery:", max_pack_dc_current, "A")
    print("Maximum Battery Voltage:", max_battery_voltage, "V")
 
    # Create a figure and axes for plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))
 
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

    line11, = ax1.plot(relevant_data['localtime'], relevant_data['Controller_Over_Temeprature_408094978'] *10, color='green', label='Controller_Over_Temperature_408094978 ')
 
 
 
    # Hide the y-axis label for 'AC_Current_340920579'
    ax1.get_yaxis().get_label().set_visible(False)
 
    # Add vertical line for fault occurrence
    ax1.axvline(x=fault_timestamp, color='gray', linestyle='--', label='Fault Occurrence')
 
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
    rax = plt.axes([0.8, 0.1, 0.15, 0.3])  # Adjust position to the right after the graph
    labels = ('PackCurr_6', 'AC_Current_340920579', 'MotorSpeed_340920578', 'AC_Voltage_340920580', 'Throttle_408094978', 'DchgFetStatus_9', 'ChgFetStatus_9', 'BatteryVoltage_340920578','SOC_8','Mode_Ack_408094978','Controller_Over_Temperature_408094978')
    lines = [line1, line3, line2, line4, line5, line6, line7, line8, line9, line10,line11]
    visibility = [line.get_visible() for line in lines]
    check = CheckButtons(rax, labels, visibility)
 
    def func(label):
        index = labels.index(label)
        lines[index].set_visible(not lines[index].get_visible())
        plt.draw()
 
    check.on_clicked(func)
 
    plt.show()
 
client = OpenAI()
 
# Call the function for 'DriveError_Controller_OverVoltag_408094978'
analyze_fault(log_file, 'Controller_Over_Temeprature_408094978')
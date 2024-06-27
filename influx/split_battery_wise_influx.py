import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplcursors  # Import mplcursors

def adjust_current(row):
    adjust_current.zero_count = getattr(adjust_current, 'zero_count', 0)
    if row['MotorSpeed [SA: 02]'] == 0:
        adjust_current.zero_count += 1
    else:
        adjust_current.zero_count = 0
   
    if adjust_current.zero_count >= 10:
        return 0
    else:
        return row['PackCurr [SA: 06]']

def plot_ghps(data, folder_name, folder_path):
    data['DATETIME'] = pd.to_datetime(data['DATETIME'], unit='s', origin='unix').dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    data['DATETIME'] = pd.to_datetime(data['DATETIME'])
    data.set_index('DATETIME', inplace=True)
    data['PackCurr [SA: 06]'] = data.apply(adjust_current, axis=1)
   
    fig, ax1 = plt.subplots(figsize=(10, 6))
 
    line1, = ax1.plot(data.index, -data['PackCurr [SA: 06]'], color='blue', label='PackCurr [SA: 06]')
    ax1.set_ylabel('Pack Current (A)', color='blue')
    ax1.yaxis.set_label_coords(-0.1, 0.7)  # Adjust label position

    ax2 = ax1.twinx()
    line2, = ax2.plot(data.index, data['MotorSpeed [SA: 02]'], color='green', label='Motor Speed')
    ax2.set_ylabel('Motor Speed (RPM)', color='green')

    line3, = ax1.plot(data.index, data['AC_Current [SA: 03]'], color='lightgray', label='AC Current')
    line4, = ax1.plot(data.index, data['AC_Voltage [SA: 04]'] * 10, color='lightgray', label='AC Voltage (x10)')
    line5, = ax1.plot(data.index, data['Throttle [SA: 02]'], color='lightgray', label='Throttle (%)')
    line6, = ax1.plot(data.index, data['SOC [SA: 08]'], color='red', label='SOC (%)')

    ax1.get_yaxis().get_label().set_visible(False)
    ax1.set_xlabel('Local Time')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.title('Battery Pack, Motor Data, and Throttle')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax1.grid(True, linestyle=':', linewidth=0.5, color='gray')
    ax2.grid(True, linestyle=':', linewidth=0.5, color='gray')
    mplcursors.cursor([line1, line2, line3, line4, line5])
    plt.tight_layout()

    subfolder_path = os.path.join(folder_path, folder_name)
    os.makedirs(subfolder_path, exist_ok=True)
    plt.savefig(os.path.join(subfolder_path, 'graph.png'))
    plt.show()

def process_files(main_folder_path):
    threshold = 35
    
    for subfolder_1 in os.listdir(main_folder_path):
        subfolder_1_path = os.path.join(main_folder_path, subfolder_1)
        
        # Check if subfolder_1 is a directory
        if os.path.isdir(subfolder_1_path):
            
            # Iterate over subfolders within subfolder_1
            for subfolder in os.listdir(subfolder_1_path):
                subfolder_path = os.path.join(subfolder_1_path, subfolder)
                
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
                            df = pd.read_csv(log_file)
                            # Process your data here
                        except Exception as e:
                            print(f"Error processing {log_file}: {e}")
                        
                        # df['DATETIME'] = pd.to_datetime(df['DATETIME'], unit='s', origin='unix').dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-3]
                        # new_csv_path = os.path.join(main_folder_path, subfolder, f'log_file.csv')
                        new_csv_path = os.path.join(subfolder_path, 'log_file.csv')
                        os.makedirs(os.path.join(main_folder_path, subfolder), exist_ok=True)
                        df.to_csv(new_csv_path, index=False)
                        df = pd.read_csv(new_csv_path)

                                # Convert Unix epoch time to datetime, assuming the original timezone is UTC
                        df['DATETIME'] = pd.to_datetime(df['DATETIME'], unit='s', origin='unix', utc=True)
                        # Convert to your desired timezone (e.g., 'Asia/Kolkata')
                        df['DATETIME'] = df['DATETIME'].dt.tz_convert('Asia/Kolkata')  # converting to IST
                        # Format the datetime as string, including milliseconds
                        df['DATETIME'] = df['DATETIME'].dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-3]  # Converting to string

                        # If you need the datetime back as pandas datetime type without timezone info
                        df['DATETIME'] = pd.to_datetime(df['DATETIME'])

                        df = df.dropna(subset=['DATETIME'])


                        
                        #df['DATETIME'] = pd.to_datetime(df['DATETIME'])
                        df['SOC [SA: 08]'] = df['SOC [SA: 08]'].interpolate(method='linear', limit_direction='both')

                        battery_end_index = 0
                        battery_number = 1
                        anomaly_window = 80
                        Time_window = 15
                        i = 2
                        last_battery_change_index = 0
                        excelStartTime_index = 1
                        t2_index = 1
                        start_time = None
                        condition_met = False

                        while i < len(df) and t2_index > 0:
                            t1 = df.iloc[i]['DATETIME']
                            t2 = t1 + pd.Timedelta(seconds=Time_window)
                            t2_index = df[df['DATETIME'] >= t2].index.min()

                            if pd.isna(t2_index):
                                nearest_index = df['DATETIME'].sub(t2).abs().idxmin()
                                t2_index = nearest_index
                            
                            print("t1----------->",i,"t2_index-------------->",t2_index)

                            if t2_index >= len(df) or t2_index < 0:
                                print(f"Invalid t2_index: {t2_index}")
                                ride_path = os.path.join(subfolder_path, 'log.csv')
                                os.makedirs(os.path.join(main_folder_path, subfolder), exist_ok=True)
                                df.to_csv(ride_path, index=False)
                                print("Log file saved(contains single ride)")
                                break

                            print("SOC difference----------------->",df.iloc[i]['SOC [SA: 08]'] - df.iloc[t2_index]['SOC [SA: 08]'])

                            if abs(df.iloc[i]['SOC [SA: 08]'] - df.iloc[t2_index]['SOC [SA: 08]']) > threshold or t2_index >= len(df) - 10:
                                # end_time = df.iloc[t2_index]['DATETIME'] - pd.Timedelta(seconds=anomaly_window)
                                # # end_time_index = df[df['DATETIME'] <= end_time].index.min()
                                # # print("End time index--------------->",end_time_index)
                                # # Find the index of the row with 'DATETIME' equal to 'end_time'
                                # end_time_index = df.index[df['DATETIME'] == end_time]
                                # if not end_time_index.empty:
                                #     end_time_index = end_time_index[0]  # Get the first matching index

                                t2_index= t2_index - 1000
                                
                                # else:
                                #     print(f"End time {end_time} not found in the DataFrame")
                                #     end_time_index = None
                                # print("t2------------->",t2)
                                # print("end time----------------->",end_time)
                                # print("End time index:--------------------->", end_time_index)


                                print("Battery changed at index: ",t2_index)
                                battery_data = df.iloc[excelStartTime_index:t2_index].copy()
                                # battery_folder_name = f'Battery_{battery_number}'
                                # os.makedirs(os.path.join(subfolder_path, battery_folder_name), exist_ok=True)
                                # plot_ghps(battery_data, battery_folder_name, subfolder_path)

                                battery_data.reset_index(inplace=True)
                                # battery_data.to_csv(os.path.join(subfolder_path, battery_folder_name, f'log.csv'), index=False)
                                ride_path = os.path.join(subfolder_path, 'log.csv')
                                os.makedirs(os.path.join(main_folder_path, subfolder), exist_ok=True)
                                battery_data.to_csv(ride_path, index=False)
                                
                                plot_ghps(battery_data, subfolder, subfolder_1_path)

                                battery_end_index = i
                                battery_number += 1
                                print("battery_number--------------->",battery_number)
                                if (battery_number ==2):
                                    break
                                last_battery_change_index = i + 1
                                i = t2_index
                                # start_time = t2 + pd.Timedelta(seconds=anomaly_window)
                                # start_time_index = df[df['DATETIME'] <= start_time].index.max()
                                start_time_index = t2_index +300

                                if pd.isna(start_time_index):
                                    nearest_index = (df['DATETIME'] - start_time).abs().idxmax()
                                    start_time = df.iloc[nearest_index]['DATETIME']
                                    start_time_index = nearest_index
                                excelStartTime_index = start_time_index
                            else:
                                i = t2_index
                            if i == len(df) - 1:
                                break

main_folder_path = r"C:\Users\kamalesh.kb\influx_a1"
process_files(main_folder_path)

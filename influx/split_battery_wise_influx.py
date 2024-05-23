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
    for mar_subfolder in os.listdir(main_folder_path):
        print(mar_subfolder)
        if mar_subfolder.startswith("mar"):
            mar_subfolder_path = os.path.join(main_folder_path, mar_subfolder)
            log_file_path = os.path.join(mar_subfolder_path, 'log.csv')
            print(log_file_path)
            if os.path.isfile(log_file_path):
                df = pd.read_csv(log_file_path)
                df['DATETIME'] = pd.to_datetime(df['DATETIME'], unit='s', origin='unix').dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-3]
                new_csv_path = os.path.join(main_folder_path, mar_subfolder, f'log_file.csv')
                os.makedirs(os.path.join(main_folder_path, mar_subfolder), exist_ok=True)
                df.to_csv(new_csv_path, index=False)
                df = pd.read_csv(new_csv_path)

                threshold = 35
                df['DATETIME'] = pd.to_datetime(df['DATETIME'])
                df['SOC [SA: 08]'] = df['SOC [SA: 08]'].interpolate(method='linear', limit_direction='both')

                battery_end_index = 0
                battery_number = 1
                anomaly_window = 40
                Time_window = 60
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

                    if abs(df.iloc[i]['SOC [SA: 08]'] - df.iloc[t2_index]['SOC [SA: 08]']) > threshold or t2_index == len(df) - 1:
                        end_time = df.iloc[t2_index]['DATETIME'] - pd.Timedelta(seconds=anomaly_window)
                        end_time_index = df[df['DATETIME'] <= end_time].index.max()
                        
                        print("Battery changed at index: ",end_time_index)
                        battery_data = df.iloc[excelStartTime_index:end_time_index].copy()
                        battery_folder_name = f'Battery_{battery_number}'
                        os.makedirs(os.path.join(mar_subfolder_path, battery_folder_name), exist_ok=True)
                        plot_ghps(battery_data, battery_folder_name, mar_subfolder_path)

                        battery_data.reset_index(inplace=True)
                        battery_data.to_csv(os.path.join(mar_subfolder_path, battery_folder_name, f'log.csv'), index=False)

                        battery_end_index = i
                        battery_number += 1
                        last_battery_change_index = i + 1
                        i = t2_index
                        start_time = t2 + pd.Timedelta(seconds=anomaly_window)
                        start_time_index = df[df['DATETIME'] <= start_time].index.max()
                        if pd.isna(start_time_index):
                            nearest_index = (df['DATETIME'] - start_time).abs().idxmax()
                            start_time = df.iloc[nearest_index]['DATETIME']
                            start_time_index = nearest_index
                        excelStartTime_index = start_time_index
                    else:
                        i = t2_index
                    if i == len(df) - 1:
                        break

main_folder_path = r"C:\Users\Kamalesh.kb\Downloads\Daily_analysis_data\influx"
process_files(main_folder_path)

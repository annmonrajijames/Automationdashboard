import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from PIL import Image
import os
import matplotlib.dates as mdates
import mplcursors  # Import mplcursors
from matplotlib.widgets import CheckButtons

def plot_ghps(data, Path):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.yaxis.set_label_coords(-0.1, 0.7)  
    ax2 = ax1.twinx()
    ax2.set_ylabel('Total SOC consumed(%)', color='green')

    # Extracting date and time from the 'Date and Time' column (taking the part after "to")
    datetime_column = pd.to_datetime(data['Date and Time'].apply(lambda x: x.split(" to ")[1]))
    print(datetime_column)

    # Plot lines with respect to 'Date and Time'
    line1, = ax2.plot(datetime_column, data['Total distance covered (km)'], color='blue', label='Distance covered')
    line2, = ax2.plot(datetime_column, data['Total energy consumption(WH/KM)'], color='red', label='Total energy consumption(WH/KM)')
    line3, = ax2.plot(datetime_column, data['Total SOC consumed(%)'], color='black', label='Total SOC consumed(%)')
    line4, = ax1.plot(datetime_column, data['Peak Power(kW)'], color='orange', label='Peak Power(kW)')
    line5, = ax1.plot(datetime_column, data['Average Power(kW)'], color='blue', label='Average Power(kW)')
    line6, = ax2.plot(datetime_column, data['Regenerative Effectiveness(%)'], color='violet', label='Regenerative Effectiveness(%)')
    line7, = ax2.plot(datetime_column, data['Difference in Cell Voltage(V)'], color='green', label='Difference in Cell Voltage(V)')
    line8, = ax2.plot(datetime_column, data['Difference in Temperature(C)'], color='violet', label='Difference in Temperature(C)')
    line9, = ax2.plot(datetime_column, data['Maximum Fet Temperature-BMS(C)'], color='orange', label='Maximum Fet Temperature-BMS(C)')
    line10, = ax2.plot(datetime_column, data['Cycle Count of battery'], color='violet', label='Cycle Count of battery')

    ax1.set_xlabel('Date and Time')  # Set x-axis label to 'Date and Time'
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    ax1.grid(True, linestyle=':', linewidth=0.5, color='gray')
    ax2.grid(True, linestyle=':', linewidth=0.5, color='gray')

    mplcursors.cursor([line1, line2, line3, line4, line5, line6, line7, line8, line9, line10])

    rax = plt.axes([0.72, 0.1, 0.15, 0.3])
    labels = ('Distance covered (km)', 'Energy consumption(WH/KM)', 'SOC consumed(%)', 'Peak Power(kW)', 'Average Power(kW)', 'Regen Effectiveness(%)', 'Diff in Cell Voltage(V)', 'Diff in Temperature(C)', 'Max Fet Temperature(C)', 'Cycle Count')
    lines = [line1, line2, line3, line4, line5, line6, line7, line8, line9, line10]
    visibility = [line.get_visible() for line in lines]
    check = CheckButtons(rax, labels, visibility)

    def func(label):
        index = labels.index(label)
        lines[index].set_visible(not lines[index].get_visible())
        plt.draw()

    check.on_clicked(func)

    plt.tight_layout()

    os.makedirs(Path, exist_ok=True)
    graph_path = os.path.join(Path, 'graph.png')
    plt.savefig(graph_path)
    plt.show()


file_path = r'C:\Users\kamalesh.kb\CodeForAutomation\Graph_analysis\BB3\analysis_monthly.xlsx'
df = pd.read_excel(file_path)
specific_rows = ['File name', 'Total distance covered (km)', 'Total energy consumption(WH/KM)', 'Total SOC consumed(%)', 'Mode', 'Peak Power(kW)', 'Average Power(kW)', 'Regenerative Effectiveness(%)', 'Difference in Cell Voltage(V)', 'Difference in Temperature(C)', 'Maximum Fet Temperature-BMS(C)', 'Cycle Count of battery','Date and Time']
filtered_df = df[df['File name'].isin(specific_rows)]
transposed_df = filtered_df.T
transposed_output_file_path = r'C:\Users\kamalesh.kb\CodeForAutomation\Graph_analysis\BB3\Graph_analysis.csv'
path = r"C:\Users\kamalesh.kb\CodeForAutomation\Graph_analysis\BB3"
transposed_df.to_csv(transposed_output_file_path, header=False, index=False)
transposed_df = pd.read_csv(transposed_output_file_path)
plot_ghps(transposed_df, path)

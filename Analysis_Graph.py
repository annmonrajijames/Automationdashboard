import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from PIL import Image
import os
import matplotlib.dates as mdates
import mplcursors  # Import mplcursors
from matplotlib.widgets import CheckButtons


def plot_ghps(data,Path):

    # Create a figure and axes for plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))

 
    # Plot 'PackCurr_6' on primary y-axis
    # line1, = ax1.plot(data.index, data['Total distance covered (km)'], color='blue', label='Distance covered')
    # ax1.set_ylabel('Peak Power(kW)')

    ax1.yaxis.set_label_coords(-0.1, 0.7)  # Adjust label position
    ax2 = ax1.twinx()
    ax2.set_ylabel('Total SOC consumed(%)', color='green')

    line1, = ax2.plot(data.index, data['Total distance covered (km)'], color='blue', label='Distance covered')
    

    line2, = ax2.plot(data.index, data['Total energy consumption(WH/KM)'], color='red', label='Total energy consumption(WH/KM)')


    line3, = ax2.plot(data.index, data['Total SOC consumed(%)'], color='black', label='Total SOC consumed(%)')
   
 
    line4, = ax1.plot(data.index, data['Peak Power(kW)'], color='orange', label='Peak Power(kW)')

    line5, = ax1.plot(data.index, data['Average Power(kW)'], color='pink', label='Average Power(kW)')

    line6, = ax2.plot(data.index, data['Regenerative Effectiveness(%)'], color='violet', label='Regenerative Effectiveness(%)')

    # Add 'AC_Voltage_340920580' scaled to 10x to the left side y-axis
    line7, = ax2.plot(data.index, data['Difference in Cell Voltage(V)'] , color='green', label='Difference in Cell Voltage(V)')
 
    line8, = ax2.plot(data.index, data['Difference in Temperature(C)'], color='violet', label='Difference in Temperature(C)')


    line9, = ax2.plot(data.index, data['Maximum Fet Temperature-BMS(C)'], color='orange', label='Maximum Fet Temperature-BMS(C)')

    line10, = ax2.plot(data.index, data['Cycle Count of battery'], color='violet', label='Cycle Count of battery')
    
 

    # Hide the y-axis label for 'AC_Current_340920579'
    ax1.get_yaxis().get_label().set_visible(False)
 
    # Set x-axis label and legend
    ax1.set_xlabel('Index')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
 
    # Add a title to the plot
    plt.title('Monthly Analysis')
 
    # Format x-axis ticks as hours:minutes:seconds
    # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S')) #for adding time in x axis
    # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M:%S'))
    ax1.set_xticks(range(-2,len(transposed_df)-2))
    print(range(-2,len(transposed_df)-2))
    ax1.set_xticklabels(transposed_df.index)


    # Set grid lines lighter
    ax1.grid(True, linestyle=':', linewidth=0.5, color='gray')
    ax2.grid(True, linestyle=':', linewidth=0.5, color='gray')
    
 
    # Enable cursor to display values on graphs
    mplcursors.cursor([ line1, line2, line3,line4, line5,line6,line7,line8,line9,line10])
    
    
    # Enable cursor for data points
    # mplcursors.cursor(hover=True)


    # Create checkboxes
    rax = plt.axes([0.8, 0.1, 0.15, 0.3])  # Adjust position to the right after the graph
    labels = ('Total distance covered (km)','Total energy consumption(WH/KM)','Total SOC consumed(%)','Peak Power(kW)','Average Power(kW)','Regenerative Effectiveness(%)','Difference in Cell Voltage(V)','Difference in Temperature(C)','Maximum Fet Temperature-BMS(C)','Cycle Count of battery')
    lines = [line1,line2, line3, line4, line5, line6, line7, line8,line9,line10]
    visibility = [line.get_visible() for line in lines]
    check = CheckButtons(rax, labels, visibility)

    def func(label):
        index = labels.index(label)
        lines[index].set_visible(not lines[index].get_visible())
        plt.draw()
 
    check.on_clicked(func)

 
    # Save the plot as an image or display it
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    # plt.savefig('graph.png')  # Save the plot as an image

    os.makedirs(Path, exist_ok=True)
    graph_path = os.path.join(Path, 'graph.png')
    print("graph_path---------->",graph_path)
    plt.savefig(graph_path)  # Save the plot as an image in the specified directory"
    

    plt.show()
   
    # return graph_path # Return the path of the saved graph image
 


# Full file path of the original Excel file
file_path = r'C:\Users\kamalesh.kb\CodeForAutomation\Graph_analysis\BB3\analysis_monthly.xlsx'

# Read the original Excel file
df = pd.read_excel(file_path)

# Define the specific rows you want to extract
specific_rows = ['File name','Total distance covered (km)','Total energy consumption(WH/KM)','Total SOC consumed(%)','Mode','Peak Power(kW)','Average Power(kW)','Regenerative Effectiveness(%)','Difference in Cell Voltage(V)','Difference in Temperature(C)','Maximum Fet Temperature-BMS(C)','Cycle Count of battery']

# Filter the DataFrame to keep only the rows that match the specified criteria
filtered_df = df[df['File name'].isin(specific_rows)]

# Transpose the DataFrame
transposed_df = filtered_df.T

# Full file path of the new transposed CSV file
transposed_output_file_path = r'C:\Users\kamalesh.kb\CodeForAutomation\Graph_analysis\BB3\Graph_analysis.csv'
path=r"C:\Users\kamalesh.kb\CodeForAutomation\Graph_analysis\BB3"


# Write the transposed DataFrame to a new CSV file without including the index
transposed_df.to_csv(transposed_output_file_path, header=False, index=False)  # Don't write column names as header and exclude the index

# Read the transposed DataFrame from the CSV file, skipping the first row
transposed_df = pd.read_csv(transposed_output_file_path)

# Call the function to plot the transposed DataFrame
plot_ghps(transposed_df,path)

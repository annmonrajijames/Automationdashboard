import pandas as pd
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots

main_folder_path = r"C:\Users\kamalesh.kb\Dyno_analysis"
print("main",main_folder_path)



def plot_ghps(data,Path):

    data.set_index('Time', inplace=True)  # Setting DATETIME as index


    fig = make_subplots()

    

    fig.add_trace(go.Scatter(x=data.index, y=data['Idc4'], name='Idc4', line=dict(color='Orange')), secondary_y=False)


    fig.update_layout(title='Analysis',
                        xaxis_title='Time',
                        yaxis_title='Values')

    fig.update_xaxes(tickformat='%H:%M:%S')

    # Save the plot as an HTML file
    os.makedirs(Path, exist_ok=True)
    graph_path = os.path.join(Path, 'Log.html')
    print("graph_Generated")
    fig.write_html(graph_path)



for subfolder in os.listdir(main_folder_path):
    subfolder_path = os.path.join(main_folder_path, subfolder)
    print(subfolder_path)

    # Check if subfolder starts with "Battery" and is a directory
    if os.path.isdir(subfolder_path):                
        log_file = None
        log_found = False

        # Iterate through files in the subfolder
        for file in os.listdir(subfolder_path):
            if file.startswith('NDURO') and file.endswith('.csv'):
                log_file = os.path.join(subfolder_path, file)
                print("file:",log_file)
                log_found = True
                break  # Stop searching once the log file is found
        
        # Process the log file if found
        if log_found:
            try:
                data = pd.read_csv(log_file)
                plot_ghps(data,subfolder_path)
                column_names = data.columns.tolist()
                print("Columns available for plotting:", column_names)
                
                # Process your data here
            except Exception as e:
                print(f"Error processing {log_file}: {e}")
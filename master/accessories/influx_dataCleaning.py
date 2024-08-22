import os
import pandas as pd

def process_data(file_path):
    # Read the first line to get the date and time from the header
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
    date_time = first_line.split(':', 1)[1].strip() if ':' in first_line else first_line

    # Load the data using a chunk size
    chunk_size = 50000  # Adjust chunk size based on your system's memory
    chunks = pd.read_csv(file_path, skiprows=1, chunksize=chunk_size)
    data_frames = []
    
    for chunk in chunks:
        # Insert the date and time as a new column
        chunk.insert(0, 'Creation Time', date_time)
        data_frames.append(chunk)

    # Concatenate all chunks into one DataFrame
    data = pd.concat(data_frames, ignore_index=True)

    # Drop the first three rows which were initially 2nd, 3rd, and 4th in the original code
    data = data.drop([0, 1, 2])

    # Output file path set to the same folder as input file
    output_file_path = os.path.join(os.path.dirname(file_path), f"processed_{os.path.basename(file_path)}")

    # Save the processed data to the specified output file path
    data.to_csv(output_file_path, index=False)
    
    return output_file_path

def process_files_in_directory(root_directory):
    # Walk through all directories starting from the root
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.csv'):
                file_path = os.path.join(dirpath, filename)
                processed_file_path = process_data(file_path)
                print(f"Processed file saved to: {processed_file_path}")

# Set the root directory path
root_directory = r"C:\Users\annmon.james\Downloads\supriya\test"  # Update this path to your root folder path
process_files_in_directory(root_directory)

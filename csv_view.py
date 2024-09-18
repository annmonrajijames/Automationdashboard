import requests
import pandas as pd
from io import BytesIO

# Replace with your direct download link
url = 'YOUR_DIRECT_DOWNLOAD_LINK'

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Read the content as a BytesIO object
    file_content = BytesIO(response.content)
    
    # Load the Excel file into a Pandas DataFrame
    df = pd.read_excel(file_content)
    
    # Display the first few rows of the DataFrame
    print(df.head())
else:
    print(f"Failed to download the file. Status code: {response.status_code}")

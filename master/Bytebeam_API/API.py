import requests
import pandas as pd

# Define API details outside the function
url = "https://cloud.bytebeam.io/api/v1/panel-data"
headers = {
    "x-bytebeam-tenant": "lectrix",
    "content-type": "application/json",
    "x-bytebeam-api-key": "82e9b8c1-98ab-4128-bfcf-2ae9e0cbe323"
}
data = {
    "startTime": 1721714472168,
    "endTime": 1724392872168,
    "filterBys": {"id": ["9"]},
    "groupBys": [],
    "panels": [{
        "type": "timeseries_table",
        "table": "can_parsed_joined",
        "columns": [
            "CellUnderVolWarn_9", "percentage_of_can_ids", "Dchg_Accumulative_Ah_14",
            "CellOverVolProt_9", "ChargerType_12", "CellVol02_1", "AC_Current_340920579",
            # Add other columns as needed
        ],
        "sortOrder": "desc",
        "rowsPerPage": 1000,
        "page": 1
    }]
}

def fetch_and_export_data():
    # To avoid scope issues, re-declare 'data' as global if needed (usually not necessary)
    global data

    try:
        # Send the POST request
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Check for HTTP errors

        # Parse JSON response
        json_data = response.json()
        if not json_data or not json_data[0] or not json_data[0]['data'] or not json_data[0]['data']['data']:
            raise ValueError("Unexpected API response structure")

        # Convert to DataFrame
        rows = json_data[0]['data']['data']
        df = pd.DataFrame(rows)

        # Export to Excel
        with pd.ExcelWriter('can_parsed_joined_data.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='can_parsed_joined_Data')
        
        print("Data exported to can_parsed_joined_data.xlsx")

    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except ValueError as e:
        print(f"Data processing error: {e}")

# Run the function
fetch_and_export_data()

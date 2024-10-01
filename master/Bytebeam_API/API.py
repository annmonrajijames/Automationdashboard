import requests
import pandas as pd
import time

# Define API details outside the function
url = "https://cloud.bytebeam.io/api/v1/panel-data"
headers = {
    "x-bytebeam-tenant": "lectrix",
    "content-type": "application/json",
    "x-bytebeam-api-key": "82e9b8c1-98ab-4128-bfcf-2ae9e0cbe323"
}

columns = [
    "timestamp", "id", "CellUnderVolWarn_9", "percentage_of_can_ids", "Dchg_Accumulative_Ah_14", "CellOverVolProt_9",
    "ChargerType_12", "CellVol02_1", "AC_Current_340920579", "PcbTemp_12", "Reverse_Pulse_408094978",
    "MotorSpeed_340920578", "LatchProtection_12", "Temp6_10", "Temp3_10", "ForwardParking_Mode_Ack_408094978"
]

def fetch_and_export_data(column_pair):
    data = {
        "startTime": 1721714472168,
        "endTime": 1724392872168,
        "filterBys": {"id": ["9"]},
        "groupBys": [],
        "panels": [{
            "type": "timeseries_table",
            "table": "can_parsed_joined",
            "columns": column_pair,
            "sortOrder": "desc",
            "rowsPerPage": 1000,
            "page": 1
        }]
    }

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

        return df

    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except ValueError as e:
        print(f"Data processing error: {e}")
    return pd.DataFrame()  # Return empty DataFrame on failure


def split_and_fetch_data():
    combined_df = pd.DataFrame()

    # Split columns into pairs, starting from index 2 to skip 'timestamp' and 'id'
    for i in range(2, len(columns), 2):
        column_pair = columns[i:i + 2]
        print(f"Fetching data for columns: {column_pair}")

        # Fetch data for the current pair of columns
        df = fetch_and_export_data(column_pair)

        # Append to the combined dataframe, avoiding duplicate columns
        if combined_df.empty:
            combined_df = df
        else:
            # Keep only new columns
            df = df[df.columns.difference(combined_df.columns)]
            combined_df = pd.concat([combined_df, df], axis=1)

        # Delay of 2 seconds between calls
        time.sleep(2)

    # Reorder columns to ensure 'timestamp' and 'id' are first
    final_columns = ['timestamp', 'id'] + [col for col in combined_df.columns if col not in ['timestamp', 'id']]
    combined_df = combined_df[final_columns]

    # Export combined DataFrame to Excel
    with pd.ExcelWriter('can_parsed_joined_data.xlsx', engine='openpyxl') as writer:
        combined_df.to_excel(writer, index=False, sheet_name='can_parsed_joined_Data')

    print("Data exported to can_parsed_joined_data.xlsx")


# Run the function
split_and_fetch_data()

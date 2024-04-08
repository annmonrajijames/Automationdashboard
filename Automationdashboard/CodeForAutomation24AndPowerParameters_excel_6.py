import os
from openpyxl import load_workbook, Workbook

def prepare_sheet_in_memory(file_path):
    workbook = load_workbook(filename=file_path)
    sheet = workbook.active
    file_name = os.path.basename(file_path)
    sheet.insert_rows(1)
    sheet['A1'] = 'file name'
    sheet['B1'] = file_name
    return sheet, file_name

def sheet_to_dict(sheet):
    data_dict = {}
    for row in sheet.iter_rows(min_row=2, values_only=True):
        key, *values = row
        data_dict[key] = values
    return data_dict

def merge_dicts(dict1, dict2):
    for key, values in dict2.items():
        if key in dict1:
            # Assuming that values is a list of values
            dict1[key].extend(values)
        else:
            dict1[key] = values
    return dict1

def process_directory(directory):
    merged_data = {}
    file_names = []
    for root, dirs, files in os.walk(directory):
        for name in dirs:
            if name.startswith("B4"):
                subdir_path = os.path.join(root, name)
                for file_name in os.listdir(subdir_path):
                    if file_name.endswith(".xlsx"):
                        file_path = os.path.join(subdir_path, file_name)
                        sheet, extracted_file_name = prepare_sheet_in_memory(file_path)
                        data_dict = sheet_to_dict(sheet)
                        merged_data = merge_dicts(merged_data, data_dict)
                        if extracted_file_name not in file_names:
                            file_names.append(extracted_file_name)
    return merged_data, file_names

def main():
    directory = r"C:\Lectrix_company\work\Git_Projects\Automationdashboard\Automationdashboard\MAIN_FOLDER\Automation_Dashboard_Batterywise\V4\D11_03_2024"
    merged_data, file_names = process_directory(directory)

    merged_workbook = Workbook()
    merged_sheet = merged_workbook.active

    # Use the extracted file names for headers
    headers = ['File name'] + file_names
    merged_sheet.append(headers)

    for key, values in merged_data.items():
        merged_sheet.append([key] + values)

    merged_file_path = os.path.join(directory, 'merged_analysis.xlsx')
    merged_workbook.save(filename=merged_file_path)

if __name__ == '__main__':
    main()
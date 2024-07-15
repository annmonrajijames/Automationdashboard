Welcome to main folder

How to use this software
Step 1: Choose the analysis by clicking the drop down menu button. 
Step 2: Click on "Choose Folder" button 
Step 3: After selecting the associated input folder to be run, it will show the directory of the input folder in the GUI to be run so Click on "Run" button. After the process is completed the output files will be saved in the respective folders- (menu_1_Daily_Analysis, menu_2_Battery_Analysis, menu_3_Error_Causes) 

Structure of Input Folder (Folder to be uploaded)

1. Input folder structure for "Daily Analysis" (All day's folder has to be inside one main folder and that particular folder has to be chosen (while running the "Daily analysis")
Root_folder/                                           # Main root directory 
│
├── Mar-13/                                           # A date folder (can be any date)
│   ├── Battery_1/                                    # A battery folder (can be any battery number)
│   │   ├── log_file.csv                              # Log file for Battery 1
│   │   └── merged_analysis.xlsx                      # Merged analysis file for Battery 1
│   │
│   ├── Battery_2/                                    # A battery folder (can be any battery number)
│   │   ├── log_file.csv                              # Log file for Battery 2
│   │   └── merged_analysis.xlsx                      # Merged analysis file for Battery 2
│   │
│   └── ...                                           # Additional batteries as required
│
├── Mar-14/                                           # A date folder (can be any date)
│   ├── Battery_1/                                    # A battery folder (can be any battery number)
│   │   ├── log_file.csv
│   │   └── merged_analysis.xls
│   │
│   ├── Battery_2/                                    # A battery folder (can be any battery number)
│   │   ├── log_file.csv
│   │   └── merged_analysis.xlsx
│   │
│   └── ...                                           # Additional batteries as required
│
└── ...                                               # Additional dates as required

OUTPUT

Root_folder/                                          # Main root directory
│
├── merged_analysis.xlsx                              OUTPUT
│
├── Mar-13/                                           
│   ├── Battery_1/                                    
│   │   ├── log_file.csv                              
│   │   ├── analysis_Battery_1.pptx                   OUTPUT
│   │   ├── analysis_Battery_1.xlsx                   OUTPUT
│   │   └── graph.png                                 OUTPUT
│   │
│   ├── Battery_2/                                    
│   │   ├── log_file.csv                              
│   │   ├── analysis_Battery_2.pptx                   OUTPUT
│   │   ├── analysis_Battery_2.xlsx                   OUTPUT
│   │   └── graph.png                                 OUTPUT
│   │
│   ├── merged_analysis.xlsx                          
│   └── ...                                           
│\
├── Mar-14/                                           
│   ├── Battery_1/                                    
│   │   ├── log_file.csv
│   │   ├── analysis_Battery_1.pptx                  OUTPUT
│   │   ├── analysis_Battery_1.xlsx                  OUTPUT
│   │   └── graph.png                                OUTPUT
│   │\
│   ├── Battery_2/                                    
│   │   ├── log_file.csv
│   │   ├── analysis_Battery_2.pptx                 OUTPUT
│   │   ├── analysis_Battery_2.xlsx                 OUTPUT
│   │   └── graph.png                               OUTPUT
│   │
│   ├── merged_analysis.xlsx                          
│   └── ...                                           # Additional batteries as required
│
└── ...                                               # Additional dates as required


2. Input folder structure for "Battery Analysis"

Root_folder/                                     # Main root directory
│
└── B2/                                          # Sub-folder inside Root_folder (Can be any number)
    ├── B4_B02_06.55_07.43/                      # Example sub-folder for a specific time slot
    │   ├── analysis_B4_B02_06.55_07.43.pptx     # PowerPoint analysis for the time slot
    │   ├── analysis_B4_B02_06.55_07.43.xlsx     # Excel analysis for the time slot
    │   ├── km_file.csv                          # Kilometer file for the time slot
    │   └── log_file.csv                         # Log file for the time slot
    │\
    ├── B4_B02_09.56_10.40/                      # Another example sub-folder for a different time slot
    │   ├── analysis_B4_B02_09.56_10.40.pptx     # PowerPoint analysis for the time slot
    │   ├── analysis_B4_B02_09.56_10.40.xlsx     # Excel analysis for the time slot
    │   ├── km_file.csv                          # Kilometer file for the time slot
    │   └── log_file.csv                         # Log file for the time slot
    │
    └── ...                                      # Additional time-slot folders as needed


OUTPUT
Root_folder/                                     # Main root directory
│
└── B2/                                          
    ├── BatteryAnalysis.xlsx                     # OUTPUT                                     
    ├── B4_B02_06.55_07.43/                      
    │   ├── analysis_B4_B02_06.55_07.43.pptx     
    │   ├── analysis_B4_B02_06.55_07.43.xlsx     
    │   ├── km_file.csv                          
    │   └── log_file.csv                         
    │
    ├── B4_B02_09.56_10.40/                      
    │   ├── analysis_B4_B02_09.56_10.40.pptx     
    │   ├── analysis_B4_B02_09.56_10.40.xlsx     
    │   ├── km_file.csv                          
    │   └── log_file.csv                         
    │
    └── ...                                      # Additional time-slot folders as needed\


3. Input folder structure for "Battery Analysis"

Root_folder/                                     # Main root directory
│
└── log.csv

OUTPUT
Will come in terminal

Files
1. main.py 
It provides graphical user interface (GUI) for managing and running different data analysis scripts using drop down menu. The GUI allows users to select a folder containing data, choose a specific type of analysis, and execute the corresponding script.

2. Daily_Analysis.py 
It is designed to analyze vehicle telemetry data for daily operations. It includes a series of data processing, calculation, and visualization tasks that culminate in generating various analytical outputs, including graphs and PowerPoint presentations.

3. Battery_Analysis.py 
It is designed to compile battery-related data from various Excel files located in specific subfolders. The script focuses on extracting and summarizing key battery performance metrics across different sessions or cycles.

4. Error_causes.py 
It is designed to analyze vehicle telemetry data to detect and diagnose various error states or faults within the vehicle's systems. It identifies conditions leading to faults, analyzes contributing factors, and visualizes these parameters over time to help diagnose the issues effectively.

5. README.txt
You are reading me now


Folders
1. menu_1_Daily_Analysis 
2. menu_2_Battery_Analysis
3. menu_3_Error_Causes
   
These folders are used for saving input files and folders after clicking and saving it using "Choose Folder" button and the output files will be saved in these folders after the software is ran. 
Each folder corresponds to a each analysis menu within the  analysis software system, and they are used to store input data, and give output data relevant to each type of analysis in respective folders. 

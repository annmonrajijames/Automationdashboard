Master Folder structure

Welcome to Lectrix's data analysis software, the 'main' folder contains the complete software necessary for running the full data analysis suite and the 'accessories' folder contains individual scripts that perform specific tasks, allowing users to run standalone functions without operating the full system.

Lectrix Data Analysis software(Master)/
│
├── main/                                # Main software
│   ├── menu_1_Daily_Analysis/           # Daily analysis folder which contains Daily Analysis output
│   ├── menu_2_Battery_Analysis/         # Battery analysis folder which contains Battery Analysis output
│   ├── menu_3_Error_Causes/             # Error cause analysis folder which contains Error Causes output
│   ├── Battery_Analysis.py              # Script for battery analysis
│   ├── Daily_Analysis.py                # Script for daily analysis
│   ├── Error_Causes.py                  # Script for analyzing error causes
│   ├── main.py                          # Main script to run the software
│   └── README.md                        # Documentation file for the software
│
├── accessories/                         # Accessory tools for specific tasks
│   ├── code_to_corp.py                  # Selective data extraction 
│   ├── Correlation.py                   # Find correlation between two parameters (in columns)
│   ├── KD_Tree.py                       # Merge two data files based on time by finding the closest time
│   ├── KD_Tree_Mergefiles_across_directories.py  # After merging using KDTree, it will stitch multiple excel files across different directories.
│   ├── merge_battery_month.py           # Merge multiple excel files across directories based on first common column
│   ├── README.md                        # Documentation file for the individual task scripts
│   ├── split_battery_wise.py            # Cutting data battery-wise based on Threshold set
│
└── README.txt                           # You are reading me now


Developers
Sanjith Gowda
Dhulipudi Abhilash
Adarsh
Kamalesh Kumar Balamurugan
Annmon James
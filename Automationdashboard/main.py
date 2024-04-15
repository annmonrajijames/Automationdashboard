input=int(input("Enter input :"))
if input == 1:
    filename = 'CellUnderVoltageWarning.py'
    with open(filename, 'r') as file:
        exec(file.read())
if input == 2:
    filename = 'CodeForAutomation24AndPowerParameters_excel.py'
    with open(filename, 'r') as file:
        exec(file.read())
import subprocess
 
def run_script(script_name):
    """Runs a Python script using subprocess and waits for it to complete."""
    print(f"Running {script_name}...")
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    print(f"Finished running {script_name}.")
    if result.stdout:
        print("Output:", result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
 
# List of scripts to run in order
scripts = [
    "KD_Tree_Mergefiles_across_directories.py",
    "code_to_crop.py",
    "Daily_Analysis.py"
]
 
for script in scripts:
    run_script(script)
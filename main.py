import os
from run_etl import run_etl

# Folder containing raw CSV files
input_folder = "data"
output_folder = "data/cleaned"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all CSV files in input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        input_file = os.path.join(input_folder, filename)
        output_file = os.path.join(output_folder, f"cleaned_{filename}")
        print(f"\nProcessing file: {filename}")
        run_etl(input_file, output_file)

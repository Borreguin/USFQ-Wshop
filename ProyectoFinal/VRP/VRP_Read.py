# read VRP data from CSV files

import os
from ProyectoFinal.VRP.VRP_Gen import plot_vrp

script_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_path, "data")

folder = "large-vrp"
file_name = "vrp.csv"

file_path = os.path.join(data_path, folder, file_name)
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File {file_name} not found in {folder} directory.")

# Function to read VRP data from CSV
plot_vrp(file_path)


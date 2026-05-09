import pandas as pd

lb_timestamp = "timestamp"
lb_V005_vent01_CO2 = "V005_vent01_CO2"
lb_V022_vent02_CO2 = "V022_vent02_CO2"
lb_V006_vent01_temp_out = "V006_vent01_temp_out"
lb_V023_vent02_temp_out = "V023_vent02_temp_out"

columns = [lb_timestamp, lb_V005_vent01_CO2, lb_V022_vent02_CO2, lb_V006_vent01_temp_out, lb_V023_vent02_temp_out]
alias = {
    lb_timestamp: "timestamp",
    lb_V005_vent01_CO2: "CO2 Ventilation NE",
    lb_V022_vent02_CO2: "CO2 Ventilation SW",
    lb_V006_vent01_temp_out: "Temp. Vent. NE Out",
    lb_V023_vent02_temp_out: "Temp. Vent. SW Out"
}
def read_csv_file(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"Error reading file: {file_path}")
        print(e)
        return pd.DataFrame()

import h5py
import pandas as pd
import numpy as np

# File paths
input_file = r"C:\Users\ak2pa\OneDrive\Documents\CSU\Fall 2026\ECE 401\Demand Script\historic_load_hourly_2016_2023_county.h5"
output_file = r"C:\Users\ak2pa\OneDrive\Documents\CSU\Fall 2026\ECE 401\Demand Script\Larimer_demand.csv"

county_column = "p08069"

# Open HDF5 file
with h5py.File(input_file, "r") as f:

    # Read column names
    columns = [
        name.decode("utf-8")
        for name in f["data/axis0"][:]
    ]

    # Find Larimer County column
    if county_column not in columns:
        raise ValueError(f"{county_column} was not found in the dataset.")

    column_index = columns.index(county_column)

    print(f"Found {county_column} at column index {column_index}")

    # Extract only Larimer County demand
    demand = f["data/block0_values"][:, column_index]

    # Read time index
    timestamps = f["data/axis1"][:]

# Convert timestamps
# Pandas HDF5 datetime indexes are commonly stored as nanoseconds.
time_index = pd.to_datetime(timestamps, unit="ns", utc=True)

# Create output DataFrame
df = pd.DataFrame({
    "UTC_Time": time_index,
    "Larimer_County_Demand": demand
})

# Export to CSV
df.to_csv(output_file, index=False)

print(f"Export complete: {output_file}")
print(df.head())
print(f"Total records: {len(df)}")

# Week 1 deliverble : Data concatenation
# Author : Yoora Choi

# import libraries
import pandas as pd
import glob as g

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Import files and sort them alphabetically
csv_files = sorted(g.glob("./*.csv")) # enter the path 

# Read all files once
dfs = [pd.read_csv(f, low_memory=False) for f in csv_files]

# Check row counts in each csv file and total number of rows
total = 0
for f, df in zip(csv_files, dfs):
    rows = len(df)
    total += rows
    print(f"{f}: {rows:,}rows")

# Concatenate csv files
df_merge = pd.concat(dfs, ignore_index=True)

# Filter PropertyType == Residential using the appending file
df_filtered = df_merge[df_merge["PropertyType"] == "Residential"]

# Check row numbers
print(f"\nTotal number of rows before concatenation: {total:,}rows")
print(f"Total number of rows after concatenation : {len(df_merge):,}rows")
print(f"Total number of rows after filtering     : {len(df_filtered):,}rows")

# Export csv file
df_filtered.to_csv("merged_(dataset name).csv", index=False) # enter the file name to export csv.

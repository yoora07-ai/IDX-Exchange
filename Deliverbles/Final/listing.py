# ============================================================
# Import Library
# ============================================================
import pandas as pd
import numpy as np
import glob as g

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# ============================================================
# Week 1 : Data Concatenation & Filter PropertyType == Residential
# ============================================================ 

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
# df_filtered.to_csv("merged_(dataset name).csv", index=False) # enter the file name to export csv.


# ============================================================
# week 2 : EDA
# ============================================================
# Please refer to Week2 deliverble

# ============================================================
# Week 3-1 : Drop Columns with Over 90% Null Count
# ============================================================

# Load concatenated MLS listing data
# isting = pd.read_csv("*/CRMLSListing_merged.csv")


# Calculate missing % per column
list_missing_pct = df_filtered.isnull().mean()*100

# Print columns with >90% missing values
list_col_drop = list_missing_pct[list_missing_pct > 90].index.tolist()
print("========== MLS listing ==========")
print("Columns to drop(>90% missing value):")
print(list_col_drop)
print()

# Drop columns having over 90% null count
list_droped = df_filtered.drop(columns=list_col_drop)

print(f"\n Column count before drop: {df_filtered.shape[1]}")
print(f"Column count after drop: {list_droped.shape[1]}")
print()

# export .csv
# list_droped.to_csv("*/CRMLSListing_null_droped.csv", index= False)



# ============================================================
# Week 3-2 : Add the Mortgage Rate Column to Listing Data
# ============================================================

# Step 1 – Fetch the mortgage rate data from FRED

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

# Step 2 – Resample weekly rates to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)

# Step 3 – Create a matching year_month key on the MLS datasets

# Import CRML sold & s listing data
sold = pd.read_csv("./CRMLSSold_null_droped.csv", low_memory=False)
listings = list_droped

# Sold dataset — key off CloseDate
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')

# Listings dataset — key off ListingContractDate
listings['year_month'] = pd.to_datetime(
    listings['ListingContractDate']
).dt.to_period('M')

# Step 4 – Merge
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')

# Step 5 – Validate the merge

# Check for any unmatched rows (rate should not be null)
print(sold_with_rates['rate_30yr_fixed'].isnull().sum())
print(listings_with_rates['rate_30yr_fixed'].isnull().sum())

# Preview

print(
    sold_with_rates[
        ['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']
    ].head()
)

# Step 6 - Export csv file
#sold_with_rates.to_csv("CRMLSSold_with_rates.csv", index= False)
#listings_with_rates.to_csv("CRMLSListing_with_rates.csv", index= False)


# ============================================================
# Week 4 : Data Cleaning and Preparation
# ============================================================

# Step 1. Convert date fields to datetime format 
def convert_date_colums(df):
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    print(f"Total {len(date_cols)} date fields : {date_cols}")

    
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors = 'coerce')
        print (f"{col} : successfully converted to datetime")
      
    print()
    return df


#Step 2-1. Remove unnecessary or redundant columns    
def drop_duplicate_columns(df, threshold=0.9):
    
    # Auto-detect columns ending with '.1'
    dup_cols = [col for col in df.columns if col.endswith('.1')]
    pairs = [(col.replace('.1', ''), col) for col in dup_cols]
    
    print(f"Duplicate pairs found ({len(pairs)}): {pairs}")
    
    cols_to_drop = []
    
    for base, dup in pairs:
        if base in df.columns and dup in df.columns:
            same_ratio = (df[base] == df[dup]).mean()
            
            if same_ratio >= threshold:
                print(f"DROP COMPELETED {base} vs {dup}: {same_ratio:.2f} → dropping '{dup}'")
                cols_to_drop.append(dup)
            else:
                print(f"DROP FAILED {base} vs {dup}: {same_ratio:.2f} → kept (values differ)")
    
    df = df.drop(columns=cols_to_drop)
    
    print(f"\n Columns dropped: {len(cols_to_drop)}")
    print(f"   Final column count: {df.shape[1]}")
    
    return df



# Step 2.2  Remove duplicate rows
def drop_duplicate_rows(df, dataset_name='dataset'):
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    
    print(f"  [{dataset_name}]")
    print(f"   Before : {before:,} rows")
    print(f"   After  : {after:,} rows")
    print(f"   Removed: {before - after:,} duplicate rows")
    
    return df

#Step 3. Handle missing values appropriately by data type
def handle_missing_values(df):
    
    numeric_cols     = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()
    datetime_cols    = df.select_dtypes(include='datetime').columns.tolist()

    # Numeric → median
    for col in numeric_cols:
        missing = df[col].isnull().sum()
        if missing > 0:
            df[col] = df[col].fillna(df[col].median())
            print(f" {col}: {missing} missing → filled with median")

    # Categorical → 'Unknown'
    for col in categorical_cols:
        missing = df[col].isnull().sum()
        if missing > 0:
            df[col] = df[col].fillna('Unknown')
            print(f"{col}: {missing} missing → filled with 'Unknown'")

    # Datetime → keep NaT
    for col in datetime_cols:
        missing = df[col].isnull().sum()
        if missing > 0:
            print(f"{col}: {missing} missing → kept as NaT")

    print(f"\nMissing value handling complete!")
    print()
    return df

# Step 4. Ensure numeric fields are properly typed : find out all numeric fields are appropriate typed
print(df.select_dtypes(include='object').dtypes)

# Step 5. Remove or flag invalid numeric values
def flag_invalid_numeric_value(df):
    
    rules = {
        'ClosePrice' : ('<=', 0),
        'LivingArea' : ('<=', 0),
        'DaysOnMarket' : ('<', 0),
        'BathroomsTotalInteger': ('<', 0),
        'BedroomsTotal' : ('<', 0)
    }
    
    for col, (operator, threshold) in rules.items():
        if col in df.columns:
            if operator == '<=':
                mask = df[col] <= threshold
            elif operator == '<':
                mask = df[col] < threshold

            flag_col = f'flag_invalid_{col}'
            df[flag_col] = mask
            print(f"{col}: {mask.sum()} invalid values flagged : '{flag_col}'")
        else:
            print(f"{col}: column not found, skipped")

    return df
    
# Run 
    
def run_cleaning_pipeline(df, dataset_name='dataset'):
    print(f"{'='*50}")
    print(f" Starting Cleaning Pipeline : [{dataset_name}]")
    print(f"{'='*50}\n")

    print("Step 1. Convert date columns")
    print("-"*40)
    df = convert_date_colums(df)

    print("Step 2-1. Drop duplicate columns")
    print("-"*40)
    df = drop_duplicate_columns(df)

    print("\nStep 2-2. Drop duplicate rows")
    print("-"*40)
    df = drop_duplicate_rows(df, dataset_name=dataset_name)

    print("\nStep 3. Handle missing values")
    print("-"*40)
    df = handle_missing_values(df)

    print("\nStep 5. Flag invalid numeric values")
    print("-"*40)
    df = flag_invalid_numeric_value(df)

    print(f"\n{'='*50}")
    print(f" Pipeline Complete! [{dataset_name}]")
    print(f" Final shape: {df.shape}")
    print(f"{'='*50}\n")

    return df


# Run
listing = run_cleaning_pipeline(listings_with_rates, dataset_name='Listing')
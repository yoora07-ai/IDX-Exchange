# ============================================================
# Import Library
# ============================================================
import pandas as pd
import numpy as np
import glob as g

# ============================================================
# Settings
# ============================================================

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


# ============================================================
# Week 1 : Data Concatenation & Filter PropertyType == Residential
# ============================================================

def week1_load_and_filter(path="./*.csv"):

    # Import files and sort them alphabetically
    csv_files = sorted(g.glob(path))

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

    return df_filtered


# ============================================================
# Week 3-1 : Drop Columns with Over 90% Null Count
# ============================================================

def week3_1_drop_null_columns(df_filtered):

    # Calculate missing % per column
    listing_missing_pct = df_filtered.isnull().mean()*100

    # Print columns with >90% missing values
    listing_col_drop = listing_missing_pct[listing_missing_pct>90].index.tolist()
    print("========== MLS listing ==========")
    print("Columns to drop(>90% missing value):")
    print(listing_col_drop)
    print()

    # Drop Columns having over 90% null count
    listing_drop = df_filtered.drop(columns=listing_col_drop)
    print(f"\n Column count before drop: {df_filtered.shape[1]}")
    print(f"Column count after drop: {listing_drop.shape[1]}")
    print()

    return listing_drop


# ============================================================
# Week 3-2 : Add the Mortgage Rate Column to li Data
# ============================================================

def week3_2_add_mortgage_rate(listing_drop):

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

    # Import CRML sold & listing data
    #listings = pd.read_csv(listings_path, low_memory=False)
    
    # Listings dataset — key off ListingContractDate
    listing_drop['year_month'] = pd.to_datetime(
        listing_drop['ListingContractDate']
    ).dt.to_period('M')

    # Step 4 – Merge
    listings_with_rates = listing_drop.merge(mortgage_monthly, on='year_month', how='left')

    # Step 5 – Validate the merge

    # Check for any unmatched rows (rate should not be null)
    print(listings_with_rates['rate_30yr_fixed'].isnull().sum())

    # Preview
    print(
        listings_with_rates[
            ['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']
        ].head()
    )

    return listings_with_rates


# ============================================================
# Week 4 : Data Cleaning and Preparation
# ============================================================

# Step 1. Convert date fields to datetime format
def convert_date_colums(df):
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    print(f"Total {len(date_cols)} date fields : {date_cols}")

    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        print(f"{col} : successfully converted to datetime")

    print()
    return df


# Step 2-1. Remove unnecessary or redundant columns
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


# Step 3. Handle missing values appropriately by data type
def handle_missing_values(df):

    categorical_cols = df.select_dtypes(include='object').columns.tolist()
    datetime_cols    = df.select_dtypes(include='datetime').columns.tolist()

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


# Step 5. flag invalid numeric values
def flag_invalid_numeric_value(df):

    rules = {
        'ClosePrice'           : ('<=', 0),
        'LivingArea'           : ('<=', 0),
        'DaysOnMarket'         : ('<',  0),
        'BathroomsTotalInteger': ('<',  0),
        'BedroomsTotal'        : ('<',  0)
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


# ============================================================
# Week 5 : Data Cleaning and Preparation(2)
# ============================================================

# Date Consistency Checks
def check_date_consistency(df):
    if 'ListingContractDate' in df.columns and 'CloseDate' in df.columns:
        df['listing_after_close_flag'] = df['ListingContractDate'] > df['CloseDate']
        print(f"listing_after_close_flag   : {df['listing_after_close_flag'].sum()} records")

    if 'PurchaseContractDate' in df.columns and 'CloseDate' in df.columns:
        df['purchase_after_close_flag'] = df['PurchaseContractDate'] > df['CloseDate']
        print(f"purchase_after_close_flag  : {df['purchase_after_close_flag'].sum()} records")

    if 'ListingContractDate' in df.columns and 'PurchaseContractDate' in df.columns:
        df['negative_timeline_flag'] = df['ListingContractDate'] > df['PurchaseContractDate']
        print(f"negative_timeline_flag     : {df['negative_timeline_flag'].sum()} records")

    return df


# Geographic Data Checks
def check_geographic_data(df):
    CA_LAT_MIN, CA_LAT_MAX =  32.5,  42.0
    CA_LON_MIN, CA_LON_MAX = -124.5, -114.0

    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df['flag_missing_coordinates'] = df['Latitude'].isnull() | df['Longitude'].isnull()
        print(f"flag_missing_coordinates   : {df['flag_missing_coordinates'].sum()} records")

        df['flag_zero_coordinates'] = (df['Latitude'] == 0) | (df['Longitude'] == 0)
        print(f"flag_zero_coordinates      : {df['flag_zero_coordinates'].sum()} records")

        df['flag_positive_longitude'] = df['Longitude'] > 0
        print(f"flag_positive_longitude    : {df['flag_positive_longitude'].sum()} records")

        df['flag_out_of_state'] = (
            (df['Latitude']  < CA_LAT_MIN) | (df['Latitude']  > CA_LAT_MAX) |
            (df['Longitude'] < CA_LON_MIN) | (df['Longitude'] > CA_LON_MAX)
        )
        print(f"flag_out_of_state          : {df['flag_out_of_state'].sum()} records")

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

    print("\nStep 6. Date Consistency Checks")
    print("-"*40)
    df = check_date_consistency(df)

    print("\nStep 7. Geographic Data Checks")
    print("-"*40)
    df = check_geographic_data(df)

    print(f"\n{'='*50}")
    print(f" Pipeline Complete! [{dataset_name}]")
    print(f" Final shape: {df.shape}")
    print(f"{'='*50}\n")

    return df


# ============================================================
# Week 6 : Feature Engineering & Segmentation
# ============================================================

# key metrics functions
def key_metrics(df):

    # Price ratio : ClosePrice / OriginalListPrice
    if 'ClosePrice' in df.columns and 'OriginalListPrice' in df.columns:
        df['price_ratio'] = df['ClosePrice']/df['OriginalListPrice']
        print("price_ratio created")

    # Price Per Sq Ft : ClosePrice / LivingArea
    if 'ClosePrice' in df.columns and 'LivingArea' in df.columns:
        df['price_Per_Sq_Ft'] = df['ClosePrice']/df['LivingArea']
        print("price_Per_Sq_Ft created")

    # Days on Market : DaysOnMarket (raw field)
    if 'DaysOnMarket' in df.columns:
        print("DaysOnMarket already exists.")

    # Year / Month / YrMo : Derived from CloseDate
    if 'CloseDate' in df.columns:
        df['close_year']  = df['CloseDate'].dt.year
        df['close_month'] = df['CloseDate'].dt.month
        df['close_yrmo']  = df['CloseDate'].dt.to_period('M')
        print("close_year, close_month, and close_yrmo created")

    # Close to Original List Ratio : ClosePrice / OriginalListPrice
    if 'ClosePrice' in df.columns and 'OriginalListPrice' in df.columns:
        df['close_to_original_list_ratio'] = df['ClosePrice']/df['OriginalListPrice']
        print("close_to_original_list_ratio created")

    # Listing to Contract Days : PurchaseContractDate - ListingContractDate
    if 'PurchaseContractDate' in df.columns and 'ListingContractDate' in df.columns:
        df['listing_to_contract_days'] = (df['PurchaseContractDate'] - df['ListingContractDate']).dt.days
        print("listing_to_contract_days created")

    # Contract to Close Days : CloseDate - PurchaseContractDate
    if 'CloseDate' in df.columns and 'PurchaseContractDate' in df.columns:
        df['contract_to_close_days'] = (df['CloseDate'] - df['PurchaseContractDate']).dt.days
        print("contract_to_close_days created\n")

    return df


# remove flags
def filter_clean_data(df):
    """
    Remove flagged records before segment analysis.
    """
    flag_cols = [col for col in df.columns if col.endswith('_flag')]

    before = len(df)

    # Remove the row that has at least one flag equal true
    clean_df = df[~df[flag_cols].any(axis=1)]

    after = len(clean_df)

    print(f"Before : {before:,} rows")
    print(f"After  : {after:,} rows")
    print(f"Removed: {before - after:,} flagged rows")
    print()

    # Print the count of each flag
    print("=== Flag Summary ===")
    print(df[flag_cols].sum().sort_values(ascending=False))

    return clean_df


# segmentation analysis
def segment_summary(df, dataset_name='dataset'):

    # Key metrics only
    key_metrics_cols = [m for m in [
        'price_ratio',
        'price_Per_Sq_Ft',
        'DaysOnMarket',
        'close_to_original_list_ratio',
        'listing_to_contract_days',
        'contract_to_close_days'
    ] if m in df.columns]

    group_cols = ['PropertyType', 'PropertySubType',
                  'CountyOrParish', 'MLSAreaMajor',
                  'ListOfficeName', 'BuyerOfficeName']

    results = {}

    for group_col in group_cols:
        if group_col in df.columns:
            summary = df.groupby(group_col)[key_metrics_cols].agg(
                sales                       = ('price_ratio',                'count'),
                avg_price_ratio             = ('price_ratio',                'median'),
                avg_price_per_sqft          = ('price_Per_Sq_Ft',            'median'),
                avg_days_on_market          = ('DaysOnMarket',               'median'),
                avg_close_to_original_ratio = ('close_to_original_list_ratio','median'),
                avg_listing_to_contract     = ('listing_to_contract_days',   'median'),
                avg_contract_to_close       = ('contract_to_close_days',     'median'),
            ).round(2).sort_values('sales', ascending=False)

            results[group_col] = summary

            print(f"\n{'='*60}")
            print(f"  [{dataset_name}] Grouped by {group_col}")
            print(f"{'='*60}")
            print(summary.to_string())

        else:
            print(f" {group_col}: column not found, skipped")

    return results

# ============================================================
# Week 7 : Outlier Detection and Data Quality
# ============================================================

def detect_outliers_iqr(df, cols, multiplier=1.5):
    """
    Flag outliers using IQR method.
    
    Parameters:
        df         : pandas DataFrame
        cols       : list of numeric columns to check
        multiplier : IQR multiplier (default 1.5)
    """
    df = df.copy()
    
    print(f"{'='*60}")
    print(f"  IQR Outlier Detection (multiplier={multiplier})")
    print(f"{'='*60}\n")

    for col in cols:
        if col not in df.columns:
            print(f"{col}: column not found, skipped")
            continue

        Q1    = df[col].quantile(0.25)
        Q3    = df[col].quantile(0.75)
        IQR   = Q3 - Q1
        lower = Q1 - multiplier * IQR
        upper = Q3 + multiplier * IQR

        flag_col      = f'flag_outlier_{col}'
        df[flag_col]  = (df[col] < lower) | (df[col] > upper)

        print(f"  {col}")
        print(f"    Q1={Q1:,.2f}  Q3={Q3:,.2f}  IQR={IQR:,.2f}")
        print(f"    Lower={lower:,.2f}  Upper={upper:,.2f}")
        print(f"    Outliers flagged: {df[flag_col].sum():,} records")
        print()

    return df

def compare_before_after(df_full, df_clean, cols):
    """
    Compare dataset size and median values before and after filtering.
    """
    print(f"{'='*60}")
    print(f"  Before vs After Comparison")
    print(f"{'='*60}\n")

    print(f"  Total rows")
    print(f"    Before : {len(df_full):,}")
    print(f"    After  : {len(df_clean):,}")
    print(f"    Removed: {len(df_full) - len(df_clean):,} ({(len(df_full) - len(df_clean)) / len(df_full) * 100:.1f}%)\n")

    print(f"  Median values")
    print(f"  {'Column':<30} {'Before':>12} {'After':>12} {'Change':>10}")
    print(f"  {'-'*65}")

    for col in cols:
        if col in df_full.columns and col in df_clean.columns:
            before = df_full[col].median()
            after  = df_clean[col].median()
            change = after - before
            print(f"  {col:<30} {before:>12,.2f} {after:>12,.2f} {change:>+10,.2f}")
  

target_cols = ['ClosePrice', 'LivingArea', 'DaysOnMarket']





# ============================================================
# Run Full Pipeline
# ============================================================

# Week 1
df_filtered = week1_load_and_filter(path="/Users/yoorachoi/Python/IDX/Listing/data/CRMLSListing20*.csv")

# Week 3-1
listing_drop = week3_1_drop_null_columns(df_filtered)

# Week 3-2
listings_with_rates = week3_2_add_mortgage_rate(
    listing_drop
)

# Week 4-5
listing= run_cleaning_pipeline(listings_with_rates, dataset_name='listing')

# Week 6
listing         = key_metrics(listing)
listing_clean   = filter_clean_data(listing)
listing_summary = segment_summary(listing_clean, dataset_name='listing')

# Segmentation analysis
print("PropertyType and PropertySubType")
print(listing_summary['PropertyType'])
print(listing_summary['PropertySubType'])
print()

print("CountyOrParish and MLSAreaMajor")
print(listing_summary['CountyOrParish'])
print(listing_summary['MLSAreaMajor'])
print()

print("ListOfficeName and BuyerOfficeName")
print(listing_summary['ListOfficeName'])
print(listing_summary['BuyerOfficeName'])

# Week 7
# Step 1. Flag outliers
print("[Listing]")
listing_flagged = detect_outliers_iqr(listing_clean, cols=target_cols)

# Step 2. Create clean filtered dataset (filtered outlier)
outlier_flag_cols = [f'flag_outlier_{col}' for col in target_cols]
listing_filtered = listing_flagged[~listing_flagged[outlier_flag_cols].any(axis=1)].copy()

# Step 3. Before vs After
print("\n[Listing]")
compare_before_after(listing_clean, listing_filtered, cols=target_cols)

# Step 4. Save both datasets
listing_flagged.to_csv('/Users/yoorachoi/Python/IDX/Listing/data/listing_flagged.csv', index=False)
listing_filtered.to_csv('/Users/yoorachoi/Python/IDX/Listing/data/listing_filtered.csv', index=False)


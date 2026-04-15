# Week 3 deliverble: Drop columns with over 90% null count in CRML Sold & listing data

import pandas as pd
import numpy as np

def drop_null_columns(input_path, output_path, label ,pct =90):
    # load csv file
    df = pd.read_csv(input_path)
    
    # calculate missing % per column
    missing_pct = df.isnull().mean()* 100
    
    # identify columns with missing % above threhold
    cols_to_drop = missing_pct[missing_pct > pct].index.tolist()
    
    # print
    print(f"============={label}============")
    print(f"Column to drop (>{pct}% missing value):")
    print(cols_to_drop)
    print(f"\nColumn count before drop:{df.shape[1]}\n")
    
    # Column drop
    df_cleaned = df.drop(columns= cols_to_drop)
    
    print(f"Column count after drop: {df_cleaned.shape[1]}")
    print()
    
    # Export csv
    df_cleaned.to_csv(output_path, index= False)
    
    return df_cleaned


# == Run : CRML Listing . Sold

listing_cleaned =drop_null_columns(
    input_path="./CRMLSListing_merged.csv",
    output_path="CRMLSListing_null_droped.csv",
    label= "CRML listing",
    pct = 90 
)

sold_cleaned = drop_null_columns(
    input_path="./CRMLSSold_merge.csv",
    output_path="CRMLSSold_null_droped.csv",
    label= "CRML Sold",
    pct = 90 
)
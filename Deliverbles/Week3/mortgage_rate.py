# Step 1 – Fetch the mortgage rate data from FRED
import pandas as pd

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
listings = pd.read_csv("./CRMLSListing_null_droped.csv", low_memory=False)

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
sold_with_rates.to_csv("CRMLSSold_with_rates.csv", index= False)
listings_with_rates.to_csv("CRMLSListing_with_rates.csv", index= False)

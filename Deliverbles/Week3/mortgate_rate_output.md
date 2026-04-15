
## Mortgage Rate Integration with MLS Data

### Step 1: Fetch Mortgage Rate Data from FRED  
Retrieved the **30-year fixed mortgage rate (MORTGAGE30US)** from the Federal Reserve Economic Data (FRED) using a CSV endpoint.  
The orginal dataset has 2 columns(Observation_date, MORTGAGE30US), and  Observation_date column is parsed into a structured format(Month).
In order to process data easily, rename the columns as below:
- `date`
- `rate_30yr_fixed`

---

### Step 2: Convert Weekly Data to Monthly Averages  
To align with the MLS datasets, I aggregated the weekly mortgage rates into **monthly averages**:
- Created a `year_month` variable using `date.to_period('M')`
- Grouped by `year_month` and calculated the mean rate  

This produced a monthly-level mortgage rate dataset.

---

### Step 3: Create Matching Keys in MLS Datasets  

Created a consistent `year_month` key in both datasets:

**Sold dataset**
- Based on `CloseDate`
- Converted to monthly period

**Listings dataset**
- Based on `ListingContractDate`
- Converted to monthly period

---

### Step 4: Merge Datasets  

Merged the mortgage rate data into both datasets using a **left join on `year_month`**:
- `sold_with_rates`
- `listings_with_rates`

---

### Step 5: Validation  

Verified that the merge was successful by checking for missing values in the mortgage rate column:

- Sold dataset missing rates: `0`  
- Listings dataset missing rates: `0`  

This confirms that **all records were successfully matched with a mortgage rate**.

---

###  Output  

| CloseDate  | year_month | ClosePrice | rate_30yr_fixed |
|------------|-----------|------------|-----------------|
| 2024-01-26 | 2024-01   | 240000.0   | 6.6425          |
| 2024-01-05 | 2024-01   | 815000.0   | 6.6425          |
| 2024-01-05 | 2024-01   | 810000.0   | 6.6425          |
| 2024-01-30 | 2024-01   | 858000.0   | 6.6425          |
| 2024-01-29 | 2024-01   | 1890500.0  | 6.6425          |


---

### Export csv file
I export listing and sold dataset with csv format.

---

### Key Takeaway  
The mortgage rate data was successfully integrated into both MLS datasets at the monthly level, with **no missing values after the merge**, ensuring the dataset is ready for further analysis.
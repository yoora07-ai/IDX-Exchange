# CRML Data Preprocessing Summary

## Criteria
- **Drop condition**: Columns with **more than 90% missing values** are removed

---

## 1. CRML Listing

### Dropped Columns (13)

| # | Column Name |
|---|-------------|
| 1 | FireplacesTotal |
| 2 | AboveGradeFinishedArea |
| 3 | TaxAnnualAmount |
| 4 | BuilderName |
| 5 | TaxYear |
| 6 | BuildingAreaTotal |
| 7 | ElementarySchoolDistrict |
| 8 | CoBuyerAgentFirstName |
| 9 | BelowGradeFinishedArea |
| 10 | BusinessType |
| 11 | CoveredSpaces |
| 12 | LotSizeDimensions |
| 13 | MiddleOrJuniorSchoolDistrict |

### Column Count Change

| | Count |
|---|-------|
| Before drop | 84 |
| After drop | **71** |
| Reduced by | -13 |

---

## 2. CRML Sold

### Dropped Columns (17)

| # | Column Name | Note |
|---|-------------|------|
| 1 | WaterfrontYN | Sold only |
| 2 | BasementYN | Sold only |
| 3 | FireplacesTotal | |
| 4 | AboveGradeFinishedArea | |
| 5 | TaxAnnualAmount | |
| 6 | BuilderName | |
| 7 | TaxYear | |
| 8 | BuildingAreaTotal | |
| 9 | ElementarySchoolDistrict | |
| 10 | CoBuyerAgentFirstName | |
| 11 | BelowGradeFinishedArea | |
| 12 | BusinessType | |
| 13 | CoveredSpaces | |
| 14 | LotSizeDimensions | |
| 15 | MiddleOrJuniorSchoolDistrict | |
| 16 | OriginatingSystemName | Sold only |
| 17 | OriginatingSystemSubName | Sold only |

### Column Count Change

| | Count |
|---|-------|
| Before drop | 84 |
| After drop | **67** |
| Reduced by | -17 |

---

## Comparison Summary

| | Listing | Sold |
|---|---------|------|
| Original column count | 84 | 84 |
| Dropped columns | 13 | 17 |
| Final column count | **71** | **67** |
| Columns dropped in Sold only | — | WaterfrontYN, BasementYN, OriginatingSystemName, OriginatingSystemSubName |

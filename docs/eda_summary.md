# Python EDA Summary

Python/SQLite profiling was used to validate the dashboard metrics and generate business findings before documenting insights.

## Checks Performed

- Row count and distinct order count.
- Date range validation.
- Total sales, total profit, and average discount reconciliation.
- Category, segment, and region profitability summaries.
- Loss-making state identification.
- High-sales / non-positive-profit product identification.
- Discount-band profitability analysis.
- Average shipping days by region.

## Key EDA Outputs

| Area | Finding |
|---|---|
| Overall | 9,994 order lines, 5,009 distinct orders, $2.30M sales, $286.4K profit |
| Category risk | Furniture has $742.0K sales but only 2.5% margin |
| Region risk | Central region has the weakest regional margin at 7.9% |
| Discount risk | 40%+ discount band has -77.4% margin |
| State risk | Texas is the largest loss-making state at -$25.7K profit |
| Shipping | Regional average ship days range only from 3.91 to 4.06 days |

## Interpretation

The data points to discounting and product/state mix as the main business issues. Shipping duration varies only slightly across regions, so it is less likely to explain the major profitability gaps in this dataset.

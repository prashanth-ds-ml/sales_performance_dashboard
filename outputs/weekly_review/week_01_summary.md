# Weekly Review - Sales Profitability Exceptions

## What Changed

- Added validated business findings from the SQLite dashboard database.
- Identified discounting, Furniture margin, and specific states/products as the main profitability concerns.

## Top Exceptions

| Exception | Evidence | Priority |
|---|---|---|
| Heavy discounts | 40%+ discount band has -77.4% margin | High |
| Furniture margin | $742.0K sales but only 2.5% margin | High |
| Texas losses | -$25.7K profit with 37% average discount | High |
| High-sales loss products | Multiple products above $10K sales have non-positive profit | Medium |

## Recommended Actions

- Review discount approval thresholds above 20%.
- Create a recurring loss-making state review.
- Track high-sales / low-profit products as a separate exception table.
- Review Furniture pricing and discount strategy.

# Data Quality Report

The project uses `scripts/create_sqlite_db.py` to normalize headers, coerce date fields, coerce numeric fields, write the SQLite `sales` table, and create indexes for common dashboard filters.

## Source Coverage

| Check | Result |
|---|---:|
| Order-line rows | 9,994 |
| Distinct orders | 5,009 |
| Date range | 2014-01-03 to 2017-12-30 |
| Total sales | $2,297,200.86 |
| Total profit | $286,397.02 |
| Average discount | 15.62% |

## Validation Checks

| Check | Purpose | Current Handling |
|---|---|---|
| Date parsing | Required for time-series dashboard filters | `order_date` and `ship_date` are parsed before SQLite load |
| Numeric coercion | Required for reliable KPIs | `sales`, `quantity`, `discount`, and `profit` are coerced to numeric |
| Column normalization | Prevents inconsistent SQL references | headers are converted to snake_case |
| Filter dimensions | Required for dashboard slicers | segment, region, state, and category are indexed |
| Negative profit records | Business exception detection | surfaced through loss-making states/products queries |
| High discount records | Profitability risk detection | analyzed through discount-band margin queries |

## Known Limitations

- The dataset is a sample retail dataset, not a live operational system.
- Profit is accepted as provided; the project does not recompute cost components.
- Shipping analysis uses ship date minus order date and does not include carrier, SLA, or fulfillment-cost fields.

# Insights

These findings are based on the committed Superstore SQLite database and the SQL logic used by the dashboard.

## Executive Summary

- The dataset contains 9,994 order lines and 5,009 distinct orders from 2014-01-03 through 2017-12-30.
- Total sales are $2.30M with $286.4K profit, giving an overall profit margin of about 12.5%.
- Discounting is the clearest profitability risk: orders with discounts above 40% generated $128.6K sales but lost $99.6K.

## Category and Segment Findings

- Technology is the strongest category by both sales and profit, with $836.2K sales and $145.5K profit at a 17.4% margin.
- Furniture generated $742.0K sales but only $18.5K profit, a 2.5% margin. This is the biggest revenue-to-profit conversion issue in the dashboard.
- Office Supplies is close to Technology in margin efficiency, with $719.0K sales and a 17.0% margin.
- Consumer is the largest segment by revenue at $1.16M, but Home Office has the strongest margin among segments at 14.0%.

## Regional and State Findings

- West is the strongest region, contributing $725.5K sales and $108.4K profit at a 14.9% margin.
- Central has weaker profitability than other regions, with $501.2K sales and a 7.9% margin.
- Texas, Ohio, Pennsylvania, and Illinois are the largest loss-making states by profit impact. Texas alone lost $25.7K with an average discount of 37%.

## Product and Discount Findings

- Several high-sales products are unprofitable, including Cisco TelePresence System EX90, GBC DocuBind P400, Lexmark MX611dhe, and Cubify CubeX 3D Printer Double Head Print.
- Orders without discounts produced $321.0K profit at a 29.5% margin.
- Discount bands above 20% are loss-making overall: 20-40% discounts produced a -15.3% margin, while 40%+ discounts produced a -77.4% margin.

## Operations Finding

- Average shipping time is tightly clustered by region, ranging from 3.91 to 4.06 days. This suggests profit issues are more strongly tied to pricing/discounting and product mix than shipping duration in this dataset.

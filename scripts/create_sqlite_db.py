#!/usr/bin/env python3
"""
Builds data/superstore.db from data/superstore_clean.csv (or a CSV you pass with --csv).
- Auto: snake_case columns, parse dates (order_date, ship_date), numeric coercion
- Creates table `sales`
- Adds indexes for fast filtering
- Prints a tiny health report at the end
"""

import os
import argparse
import sqlite3
import pandas as pd

# ---- sensible defaults for your repo layout ----
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR  = os.path.join(REPO_ROOT, "data")
DEFAULT_CSV = os.path.join(DATA_DIR, "superstore_clean.csv")
DEFAULT_DB  = os.path.join(DATA_DIR, "superstore.db")

DATE_CANDIDATES = {"order_date", "ship_date"}
NUMERIC_CANDIDATES = {"sales", "quantity", "discount", "profit"}

def snake(s: str) -> str:
    return (
        s.strip()
         .replace("/", "_")
         .replace("\\", "_")
         .replace("-", "_")
         .replace(" ", "_")
         .replace("%", "pct")
         .lower()
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=DEFAULT_CSV, help="Path to source CSV")
    ap.add_argument("--db",  default=DEFAULT_DB,  help="Path to output SQLite DB")
    ap.add_argument("--table", default="sales",   help="Destination table name")
    ap.add_argument("--if_exists", default="replace", choices=["replace","append","fail"])
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.db), exist_ok=True)

    print(f"📄 CSV: {args.csv}")
    print(f"🗄️  DB : {args.db}")
    print(f"🧮 Table: {args.table}")

    # 1) Load CSV
    df = pd.read_csv(args.csv)

    # 2) Normalize columns
    df.columns = [snake(c) for c in df.columns]

    # 3) Coerce dtypes
    # date columns
    for c in DATE_CANDIDATES:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce").dt.date

    # numeric columns
    for c in NUMERIC_CANDIDATES:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # 4) Write to SQLite
    conn = sqlite3.connect(args.db)
    df.to_sql(args.table, conn, if_exists=args.if_exists, index=False)

    # 5) Indexes (only create if columns exist)
    existing_cols = set(df.columns)
    indexes = [
        ("idx_sales_order_date", "order_date"),
        ("idx_sales_segment",    "segment"),
        ("idx_sales_region",     "region"),
        ("idx_sales_state",      "state"),
        ("idx_sales_category",   "category"),
    ]
    with conn:
        for idx_name, col in indexes:
            if col in existing_cols:
                conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {args.table}({col});")

    # 6) Quick health check
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {args.table}")
    n_rows = cur.fetchone()[0]

    date_min = date_max = None
    if "order_date" in existing_cols:
        cur.execute(f"SELECT MIN(order_date), MAX(order_date) FROM {args.table}")
        date_min, date_max = cur.fetchone()

    conn.close()

    print("✅ Done.")
    print(f"   Rows: {n_rows:,}")
    if date_min and date_max:
        print(f"   Order date range: {date_min} → {date_max}")

if __name__ == "__main__":
    main()

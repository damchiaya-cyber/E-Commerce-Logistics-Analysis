"""
Data-quality and loading step of the pipeline.

Reads the three CSVs, validates them against a set of explicit rules,
writes a human-readable data-quality report, quarantines the rows that
fail validation instead of silently dropping them, and loads only the
clean data into a SQLite database (ecommerce.db) using sql/schema.sql.

Run: python load_to_db.py
"""
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd

DB_PATH = "ecommerce.db"
SCHEMA_PATH = Path("sql/schema.sql")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def load_csvs():
    customers = pd.read_csv("Dim_Customers.csv")
    products = pd.read_csv("Dim_Products.csv")
    orders = pd.read_csv("Fact_Orders.csv", parse_dates=["OrderDate", "DeliveryDate"])
    return customers, products, orders


def check_customers(customers: pd.DataFrame):
    issues = {}
    # De-dup on CustomerID (the primary key), not the full row: two distinct
    # customers can legitimately share PLZ/City/State, but never CustomerID.
    issues["duplicate_customer_ids"] = customers.duplicated(subset=["CustomerID"]).sum()
    issues["missing_plz"] = customers["PLZ"].isna().sum()
    quarantined = customers[customers.duplicated(subset=["CustomerID"], keep="first")]
    clean = customers.drop_duplicates(subset=["CustomerID"], keep="first").copy()
    return clean, quarantined, issues


def check_products(products: pd.DataFrame):
    issues = {}
    issues["duplicate_product_rows"] = products.duplicated().sum()
    issues["negative_or_zero_price"] = (products["Price_EUR"] <= 0).sum()
    issues["cost_exceeds_price"] = (products["Cost_EUR"] >= products["Price_EUR"]).sum()
    clean = products.drop_duplicates().copy()
    return clean, issues


def check_orders(orders: pd.DataFrame, valid_customer_ids, valid_product_ids):
    issues = {}
    issues["duplicate_order_rows"] = orders.duplicated().sum()
    issues["negative_shipping_cost"] = (orders["ShippingCost_EUR"] < 0).sum()
    issues["delivery_before_order"] = (orders["DeliveryDate"] < orders["OrderDate"]).sum()
    issues["orphaned_customer_id"] = (~orders["CustomerID"].isin(valid_customer_ids)).sum()
    issues["orphaned_product_id"] = (~orders["ProductID"].isin(valid_product_ids)).sum()

    bad_mask = (
        orders.duplicated()
        | (orders["ShippingCost_EUR"] < 0)
        | (orders["DeliveryDate"] < orders["OrderDate"])
        | (~orders["CustomerID"].isin(valid_customer_ids))
        | (~orders["ProductID"].isin(valid_product_ids))
    )
    quarantined = orders[bad_mask].copy()
    clean = orders[~bad_mask].copy()
    return clean, quarantined, issues


def write_report(customer_issues, product_issues, order_issues, n_before, n_after):
    lines = [
        "# Data Quality Report",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Dim_Customers",
    ]
    for k, v in customer_issues.items():
        lines.append(f"- {k}: {v}")

    lines += ["", "## Dim_Products"]
    for k, v in product_issues.items():
        lines.append(f"- {k}: {v}")

    lines += ["", "## Fact_Orders"]
    for k, v in order_issues.items():
        lines.append(f"- {k}: {v}")

    lines += [
        "",
        "## Summary",
        f"- Orders before cleaning: {n_before}",
        f"- Orders after cleaning: {n_after}",
        f"- Orders quarantined: {n_before - n_after} "
        f"({round(100 * (n_before - n_after) / n_before, 2)}% of raw rows)",
        "",
        "Quarantined rows are kept in reports/quarantined_orders.csv "
        "and reports/quarantined_customers.csv for traceability instead of "
        "being silently discarded.",
    ]

    (REPORT_DIR / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")


def load_into_sqlite(customers, products, orders):
    conn = sqlite3.connect(DB_PATH)
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    customers.to_sql("Dim_Customers", conn, if_exists="append", index=False)
    products.to_sql("Dim_Products", conn, if_exists="append", index=False)
    orders.to_sql("Fact_Orders", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()


def main():
    print("Loading raw CSVs...")
    customers, products, orders = load_csvs()

    print("Running data-quality checks...")
    clean_customers, quarantined_customers, customer_issues = check_customers(customers)
    clean_products, product_issues = check_products(products)
    clean_orders, quarantined_orders, order_issues = check_orders(
        orders,
        valid_customer_ids=set(clean_customers["CustomerID"]),
        valid_product_ids=set(clean_products["ProductID"]),
    )

    quarantined_customers.to_csv(REPORT_DIR / "quarantined_customers.csv", index=False)
    quarantined_orders.to_csv(REPORT_DIR / "quarantined_orders.csv", index=False)

    write_report(
        customer_issues,
        product_issues,
        order_issues,
        n_before=len(orders),
        n_after=len(clean_orders),
    )

    print("Loading clean data into SQLite (ecommerce.db)...")
    load_into_sqlite(clean_customers, clean_products, clean_orders)

    print("Done. See reports/data_quality_report.md for the full findings.")


if __name__ == "__main__":
    main()

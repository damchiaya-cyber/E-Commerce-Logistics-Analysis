# Data Quality Report
Generated: 2026-09-14T22:56:53

## Dim_Customers
- duplicate_customer_ids: 21
- missing_plz: 15

## Dim_Products
- duplicate_product_rows: 0
- negative_or_zero_price: 0
- cost_exceeds_price: 0

## Fact_Orders
- duplicate_order_rows: 50
- negative_shipping_cost: 26
- delivery_before_order: 15
- orphaned_customer_id: 0
- orphaned_product_id: 0

## Summary
- Orders before cleaning: 5050
- Orders after cleaning: 4961
- Orders quarantined: 89 (1.76% of raw rows)

Quarantined rows are kept in reports/quarantined_orders.csv and reports/quarantined_customers.csv for traceability instead of being silently discarded.
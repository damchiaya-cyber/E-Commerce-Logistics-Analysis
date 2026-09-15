-- Business queries answering the process-analysis questions from the README.
-- Run against ecommerce.db (see run_queries.py).

-- Q1: Average delivery time (days) and return rate per logistics provider.
-- Confirms the Hermes delay finding directly from data instead of Power BI.
SELECT
    LogisticsProvider,
    ROUND(AVG(JULIANDAY(DeliveryDate) - JULIANDAY(OrderDate)), 2) AS avg_delivery_days,
    ROUND(100.0 * SUM(IsReturned) / COUNT(*), 2) AS return_rate_pct,
    COUNT(*) AS num_orders
FROM Fact_Orders
GROUP BY LogisticsProvider
ORDER BY avg_delivery_days DESC;

-- Q2: Return rate by reason, isolated for orders delayed 5+ days.
-- Quantifies "late delivery -> return" causality mentioned in the README.
SELECT
    ReturnReason,
    COUNT(*) AS num_returns
FROM Fact_Orders
WHERE IsReturned = 1
  AND (JULIANDAY(DeliveryDate) - JULIANDAY(OrderDate)) >= 5
GROUP BY ReturnReason
ORDER BY num_returns DESC;

-- Q3: Return rate by product category, joined against Dim_Products.
SELECT
    p.Category,
    ROUND(100.0 * SUM(f.IsReturned) / COUNT(*), 2) AS return_rate_pct,
    COUNT(*) AS num_orders
FROM Fact_Orders f
JOIN Dim_Products p ON f.ProductID = p.ProductID
GROUP BY p.Category
ORDER BY return_rate_pct DESC;

-- Q4: Estimated shipping cost exposure per provider (business-ROI angle).
SELECT
    LogisticsProvider,
    ROUND(SUM(ShippingCost_EUR), 2) AS total_shipping_cost_eur,
    ROUND(AVG(ShippingCost_EUR), 2) AS avg_shipping_cost_eur
FROM Fact_Orders
GROUP BY LogisticsProvider
ORDER BY total_shipping_cost_eur DESC;

-- Q5: Monthly return rate trend across 2023.
SELECT
    strftime('%Y-%m', OrderDate) AS order_month,
    ROUND(100.0 * SUM(IsReturned) / COUNT(*), 2) AS return_rate_pct,
    COUNT(*) AS num_orders
FROM Fact_Orders
GROUP BY order_month
ORDER BY order_month;

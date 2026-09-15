# SQL Findings

## Q1: Average delivery time (days) and return rate per logistics provider.
| LogisticsProvider   |   avg_delivery_days |   return_rate_pct |   num_orders |
|:--------------------|--------------------:|------------------:|-------------:|
| Hermes              |                4.35 |             27.07 |         1644 |
| DPD                 |                1.97 |             23    |         1661 |
| DHL                 |                1.97 |             21.2  |         1656 |

## Q2: Return rate by reason, isolated for orders delayed 5+ days.
| ReturnReason      |   num_returns |
|:------------------|--------------:|
| Zu spät geliefert |           201 |
| Gefällt nicht     |            16 |
| Passt nicht       |            15 |
| Falscher Artikel  |             2 |
| Beschädigt        |             1 |

## Q3: Return rate by product category, joined against Dim_Products.
| Category   |   return_rate_pct |   num_orders |
|:-----------|------------------:|-------------:|
| Bekleidung |             38.73 |         1970 |
| Haushalt   |             15.46 |         1255 |
| Elektronik |             12.99 |          901 |
| Sport      |             12.46 |          835 |

## Q4: Estimated shipping cost exposure per provider (business-ROI angle).
| LogisticsProvider   |   total_shipping_cost_eur |   avg_shipping_cost_eur |
|:--------------------|--------------------------:|------------------------:|
| DHL                 |                   9114.39 |                    5.5  |
| DPD                 |                   9110.62 |                    5.49 |
| Hermes              |                   9020.07 |                    5.49 |

## Q5: Monthly return rate trend across 2023.
| order_month   |   return_rate_pct |   num_orders |
|:--------------|------------------:|-------------:|
| 2023-01       |             24.33 |          448 |
| 2023-02       |             24.26 |          371 |
| 2023-03       |             18.97 |          427 |
| 2023-04       |             21.96 |          428 |
| 2023-05       |             24.75 |          396 |
| 2023-06       |             23.95 |          430 |
| 2023-07       |             26.12 |          402 |
| 2023-08       |             21.44 |          443 |
| 2023-09       |             25.37 |          406 |
| 2023-10       |             26.24 |          404 |
| 2023-11       |             24.94 |          405 |
| 2023-12       |             23.19 |          401 |

import pandas as pd
import numpy as np
from faker import Faker
import random
import hashlib
from datetime import timedelta

fake = Faker('de_DE')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 50
NUM_ORDERS = 5000
LOGISTICS_PROVIDERS = ['DHL', 'Hermes', 'DPD']

# Share of rows where we deliberately inject realistic raw-data problems.
# This simulates what a real CRM/order export looks like before cleaning,
# so the data-quality step in load_to_db.py has real issues to find.
DUPLICATE_CUSTOMER_RATE = 0.02
MISSING_PLZ_RATE = 0.015
DUPLICATE_ORDER_RATE = 0.01
NEGATIVE_SHIPPING_COST_RATE = 0.005
INVALID_DATE_RATE = 0.003

print("Starting Phase 1: Data Generation & DSGVO Anonymization...")

categories = {
    'Bekleidung': (20, 150),
    'Elektronik': (100, 800),
    'Haushalt': (30, 250),
    'Sport': (15, 100)
}

products = []
for i in range(1, NUM_PRODUCTS + 1):
    category = random.choice(list(categories.keys()))
    price = round(random.uniform(*categories[category]), 2)
    margin = random.uniform(0.3, 0.6)  # 30% to 60% margin
    cost = round(price * (1 - margin), 2)

    products.append({
        'ProductID': f'PRD-{i:04d}',
        'Category': category,
        'ProductName': f'{category} Artikel {i}',
        'Price_EUR': price,
        'Cost_EUR': cost
    })

df_products = pd.DataFrame(products)

# --- Raw customers (simulates an unclean CRM export) ---
raw_customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    raw_customers.append({
        'Raw_ID': i,
        'Name': fake.name(),
        'Email': fake.email(),
        'Address': fake.street_address(),
        'PLZ': fake.postcode(),
        'City': fake.city(),
        'State': fake.state()
    })

df_raw_customers = pd.DataFrame(raw_customers)

# Inject missing PLZ values (common real-world CRM gap)
missing_idx = df_raw_customers.sample(frac=MISSING_PLZ_RATE, random_state=42).index
df_raw_customers.loc[missing_idx, 'PLZ'] = None

# Inject duplicate customer rows (e.g. double sign-up / re-import)
n_dupes = int(len(df_raw_customers) * DUPLICATE_CUSTOMER_RATE)
dupe_rows = df_raw_customers.sample(n=n_dupes, random_state=7)
df_raw_customers = pd.concat([df_raw_customers, dupe_rows], ignore_index=True)


def hash_pii(email):
    return hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]


df_customers = df_raw_customers.copy()
df_customers['CustomerID'] = df_customers['Email'].apply(hash_pii)
df_customers = df_customers[['CustomerID', 'PLZ', 'City', 'State']]

# --- Orders ---
orders = []
start_date = pd.to_datetime('2023-01-01')
end_date = pd.to_datetime('2023-12-31')
customer_ids = df_customers['CustomerID'].tolist()

for i in range(1, NUM_ORDERS + 1):
    order_date = fake.date_between(start_date=start_date, end_date=end_date)
    customer_id = random.choice(customer_ids)

    product = random.choice(products)
    product_id = product['ProductID']
    category = product['Category']

    provider = random.choice(LOGISTICS_PROVIDERS)

    base_shipping_days = random.randint(1, 3)
    if provider == 'Hermes' and random.random() < 0.4:
        delay = random.randint(4, 8)
    else:
        delay = 0

    actual_delivery_days = base_shipping_days + delay
    delivery_date = order_date + timedelta(days=actual_delivery_days)

    return_reasons = ['Passt nicht', 'Gefällt nicht', 'Beschädigt', 'Zu spät geliefert', 'Falscher Artikel']
    is_returned = False
    return_reason = None

    return_prob = 0.35 if category == 'Bekleidung' else 0.12
    if delay >= 5:
        return_prob += 0.20

    if random.random() < return_prob:
        is_returned = True
        if delay >= 5:
            return_reason = 'Zu spät geliefert'
        elif category == 'Bekleidung':
            return_reason = random.choice(['Passt nicht', 'Gefällt nicht'])
        else:
            return_reason = random.choice(return_reasons)

    shipping_cost = round(random.uniform(3.50, 7.50), 2)

    orders.append({
        'OrderID': f'ORD-{i:06d}',
        'OrderDate': order_date,
        'DeliveryDate': delivery_date,
        'CustomerID': customer_id,
        'ProductID': product_id,
        'LogisticsProvider': provider,
        'ShippingCost_EUR': shipping_cost,
        'IsReturned': 1 if is_returned else 0,
        'ReturnReason': return_reason
    })

df_orders = pd.DataFrame(orders)

# Inject negative shipping costs (data-entry / refund-sign errors happen in real systems)
neg_idx = df_orders.sample(frac=NEGATIVE_SHIPPING_COST_RATE, random_state=11).index
df_orders.loc[neg_idx, 'ShippingCost_EUR'] = -df_orders.loc[neg_idx, 'ShippingCost_EUR']

# Inject invalid dates: delivery date before order date (impossible, but happens
# when systems record dates in the wrong timezone/field order)
invalid_idx = df_orders.sample(frac=INVALID_DATE_RATE, random_state=13).index
df_orders.loc[invalid_idx, 'DeliveryDate'] = df_orders.loc[invalid_idx, 'OrderDate'] - timedelta(days=2)

# Inject duplicate order rows (simulates a double-write during ingestion)
n_order_dupes = int(len(df_orders) * DUPLICATE_ORDER_RATE)
dupe_orders = df_orders.sample(n=n_order_dupes, random_state=17)
df_orders = pd.concat([df_orders, dupe_orders], ignore_index=True)

df_products.to_csv('Dim_Products.csv', index=False)
df_customers.to_csv('Dim_Customers.csv', index=False)
df_orders.to_csv('Fact_Orders.csv', index=False)

print("Success! Three CSV files generated:")
print("- Dim_Products.csv")
print("- Dim_Customers.csv (Anonymized for DSGVO, contains intentional raw-data issues)")
print("- Fact_Orders.csv (Contains engineered logistics delays, returns, and raw-data issues)")

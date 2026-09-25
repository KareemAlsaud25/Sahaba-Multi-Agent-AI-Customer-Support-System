import os
import pandas as pd

ORDERS_PATH = "data/orders.csv"

def load_orders():
    target_path = ORDERS_PATH if os.path.exists(ORDERS_PATH) else "orders.csv"
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Could not find orders CSV at {ORDERS_PATH} or orders.csv")
    return pd.read_csv(target_path)

def get_order_status(order_id: str) -> str:
    orders = load_orders()
    order_id = order_id.strip().upper()

    match = orders[orders["order_id"].astype(str).str.upper() == order_id]

    if match.empty:
        return f"No order found with ID {order_id}."

    row = match.iloc[0]

    return (
        f"Order {row['order_id']}: status is '{row['status']}'. "
        f"Product ID: {row['product_id']}, quantity: {row['quantity']}, "
        f"order date: {row['order_date']}, delivery date: {row['delivery_date']}, "
        f"total amount: ${row['total_amount']}."
    )

def get_orders_by_customer(customer_id: str) -> str:
    orders = load_orders()
    customer_id = customer_id.strip().upper()

    matches = orders[orders["customer_id"].astype(str).str.upper() == customer_id]

    if matches.empty:
        return f"No orders found for customer {customer_id}."

    lines = []
    for _, row in matches.iterrows():
        lines.append(
            f"Order {row['order_id']}: status '{row['status']}', "
            f"product {row['product_id']}, quantity {row['quantity']}, "
            f"total ${row['total_amount']}, ordered on {row['order_date']}."
        )

    return "\n".join(lines)

if __name__ == "__main__":
    print(get_order_status("O0001"))
    print(get_order_status("O9999"))
    print(get_orders_by_customer("C096"))

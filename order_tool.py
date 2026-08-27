import pandas as pd

ORDERS_PATH = "data/orders.csv"

def load_orders():
    return pd.read_csv(ORDERS_PATH)

def get_order_status(order_id: str) -> str:
    orders = load_orders()
    order_id = order_id.strip().upper()

    match = orders[orders["order_id"].str.upper() == order_id]

    if match.empty:
        return f"No order found with ID {order_id}."

    row = match.iloc[0]

    return (
        f"Order {row['order_id']}: status is '{row['status']}'. "
        f"Product ID: {row['product_id']}, quantity: {row['quantity']}, "
        f"order date: {row['order_date']}, delivery date: {row['delivery_date']}, "
        f"total amount: {row['total_amount']}."
    )

def get_orders_by_customer(customer_id: str) -> str:
    orders = load_orders()
    customer_id = customer_id.strip().upper()

    matches = orders[orders["customer_id"].str.upper() == customer_id]

    if matches.empty:
        return f"No orders found for customer {customer_id}."

    lines = []
    for _, row in matches.iterrows():
        lines.append(
            f"Order {row['order_id']}: status '{row['status']}', "
            f"total {row['total_amount']}, ordered on {row['order_date']}."
        )

    return "\n".join(lines)

if __name__ == "__main__":
    print(get_order_status("O0001"))
    print(get_order_status("O9999"))
    print(get_orders_by_customer("C096"))

from database import query_df

def get_kpis(start_date=None, end_date=None):
    where = ""
    params = []
    if start_date and end_date:
        where = "WHERE o.order_date BETWEEN ? AND ?"
        params = [str(start_date), str(end_date)]
    sales = query_df(f"""
        SELECT
            COALESCE(SUM(oi.quantity * oi.unit_price),0) AS revenue,
            COALESCE(SUM(oi.quantity * oi.unit_cost),0) AS cost,
            COUNT(DISTINCT o.order_id) AS orders,
            COALESCE(SUM(oi.quantity),0) AS units
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id=oi.order_id
        {where}
    """, params)
    exp_where = ""
    exp_params = []
    if start_date and end_date:
        exp_where = "WHERE expense_date BETWEEN ? AND ?"
        exp_params = [str(start_date), str(end_date)]
    expenses = query_df(
        f"SELECT COALESCE(SUM(amount),0) AS total FROM expenses {exp_where}",
        exp_params
    )["total"].iloc[0]
    revenue = float(sales["revenue"].iloc[0])
    cost = float(sales["cost"].iloc[0])
    gross_profit = revenue - cost
    return {
        "revenue": revenue,
        "cost": cost,
        "gross_profit": gross_profit,
        "expenses": float(expenses),
        "net_profit": gross_profit - float(expenses),
        "orders": int(sales["orders"].iloc[0]),
        "units": int(sales["units"].iloc[0])
    }

def monthly_sales():
    return query_df("""
        SELECT strftime('%Y-%m',o.order_date) AS month,
               SUM(oi.quantity*oi.unit_price) AS revenue,
               SUM(oi.quantity*(oi.unit_price-oi.unit_cost)) AS gross_profit
        FROM orders o JOIN order_items oi ON o.order_id=oi.order_id
        GROUP BY strftime('%Y-%m',o.order_date)
        ORDER BY month
    """)

def product_performance():
    return query_df("""
        SELECT p.name AS product,
               SUM(oi.quantity) AS units_sold,
               SUM(oi.quantity*oi.unit_price) AS revenue,
               SUM(oi.quantity*(oi.unit_price-oi.unit_cost)) AS gross_profit
        FROM products p JOIN order_items oi ON p.product_id=oi.product_id
        GROUP BY p.product_id,p.name
        ORDER BY revenue DESC
    """)

def category_performance():
    return query_df("""
        SELECT c.category_name AS category,
               SUM(oi.quantity*oi.unit_price) AS revenue
        FROM categories c
        JOIN products p ON c.category_id=p.category_id
        JOIN order_items oi ON p.product_id=oi.product_id
        GROUP BY c.category_id,c.category_name
        ORDER BY revenue DESC
    """)

def recent_orders():
    return query_df("""
        SELECT o.order_id, o.order_date, cu.name AS customer,
               GROUP_CONCAT(p.name, ', ') AS products,
               SUM(oi.quantity) AS units,
               SUM(oi.quantity*oi.unit_price) AS amount,
               SUM(oi.quantity*(oi.unit_price-oi.unit_cost)) AS gross_profit
        FROM orders o
        JOIN customers cu ON o.customer_id=cu.customer_id
        JOIN order_items oi ON o.order_id=oi.order_id
        JOIN products p ON oi.product_id=p.product_id
        GROUP BY o.order_id
        ORDER BY o.order_date DESC,o.order_id DESC
    """)

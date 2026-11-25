from database import get_connection, execute

def add_customer(name, email, phone, city):
    return execute(
        "INSERT INTO customers(name,email,phone,city) VALUES (?,?,?,?)",
        (name.strip(), email.strip() or None, phone.strip(), city.strip())
    )

def add_product(category_id, name, cost, price, stock):
    return execute(
        """INSERT INTO products(category_id,name,cost_price,selling_price,stock)
           VALUES (?,?,?,?,?)""",
        (category_id, name.strip(), cost, price, stock)
    )

def update_product(product_id, category_id, name, cost, price, stock):
    execute(
        """UPDATE products SET category_id=?,name=?,cost_price=?,selling_price=?,stock=?
           WHERE product_id=?""",
        (category_id, name.strip(), cost, price, stock, product_id)
    )

def delete_product(product_id):
    with get_connection() as conn:
        used = conn.execute(
            "SELECT COUNT(*) FROM order_items WHERE product_id=?", (product_id,)
        ).fetchone()[0]
        if used:
            raise ValueError("This product is linked to previous sales and cannot be deleted. Set its stock to 0 instead.")
        conn.execute("DELETE FROM products WHERE product_id=?", (product_id,))
        conn.commit()

def add_sale(customer_id, product_id, quantity, order_date):
    with get_connection() as conn:
        product = conn.execute(
            "SELECT selling_price,cost_price,stock FROM products WHERE product_id=?",
            (product_id,)
        ).fetchone()
        if product is None:
            raise ValueError("Product not found.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if product["stock"] < quantity:
            raise ValueError(f"Only {product['stock']} units are currently in stock.")
        cur = conn.execute(
            "INSERT INTO orders(customer_id,order_date,status) VALUES (?,?,?)",
            (customer_id, order_date, "Completed")
        )
        order_id = cur.lastrowid
        conn.execute(
            """INSERT INTO order_items(order_id,product_id,quantity,unit_price,unit_cost)
               VALUES (?,?,?,?,?)""",
            (order_id, product_id, quantity, product["selling_price"], product["cost_price"])
        )
        conn.execute(
            "UPDATE products SET stock=stock-? WHERE product_id=?",
            (quantity, product_id)
        )
        conn.commit()
        return order_id

def add_expense(name, category, amount, expense_date, notes):
    return execute(
        """INSERT INTO expenses(expense_name,category,amount,expense_date,notes)
           VALUES (?,?,?,?,?)""",
        (name.strip(), category, amount, expense_date, notes.strip())
    )

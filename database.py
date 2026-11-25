import sqlite3
from pathlib import Path
from datetime import date, timedelta
import random

DB_PATH = Path(__file__).with_name("sales.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            city TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            cost_price REAL NOT NULL CHECK(cost_price >= 0),
            selling_price REAL NOT NULL CHECK(selling_price >= 0),
            stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
            FOREIGN KEY(category_id) REFERENCES categories(category_id)
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT DEFAULT 'Completed',
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL,
            unit_cost REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        );

        CREATE TABLE IF NOT EXISTS expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_name TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount >= 0),
            expense_date TEXT NOT NULL,
            notes TEXT
        );
        """)
        conn.commit()
    seed_demo_data()

def seed_demo_data():
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count:
            return

        category_names = ["Electronics", "Fashion", "Home & Living", "Beauty", "Sports"]
        for name in category_names:
            conn.execute("INSERT OR IGNORE INTO categories(category_name) VALUES (?)", (name,))

        customers = [
            ("Aarav Mehta", "aarav@example.com", "9876543210", "Bengaluru"),
            ("Diya Sharma", "diya@example.com", "9876543211", "Mysuru"),
            ("Ishaan Rao", "ishaan@example.com", "9876543212", "Bengaluru"),
            ("Meera Nair", "meera@example.com", "9876543213", "Chennai"),
            ("Kabir Shah", "kabir@example.com", "9876543214", "Hyderabad"),
            ("Ananya Das", "ananya@example.com", "9876543215", "Bengaluru"),
        ]
        conn.executemany(
            "INSERT INTO customers(name,email,phone,city) VALUES (?,?,?,?)", customers
        )

        category_map = {
            r["category_name"]: r["category_id"]
            for r in conn.execute("SELECT * FROM categories").fetchall()
        }
        products = [
            (category_map["Electronics"], "Wireless Headphones", 850, 1499, 38),
            (category_map["Electronics"], "Smart Watch", 1600, 2799, 24),
            (category_map["Fashion"], "Everyday Tote Bag", 320, 799, 65),
            (category_map["Fashion"], "Classic Sneakers", 1100, 2199, 31),
            (category_map["Home & Living"], "Ceramic Coffee Set", 450, 999, 42),
            (category_map["Home & Living"], "Desk Lamp", 520, 1199, 27),
            (category_map["Beauty"], "Glow Skincare Kit", 600, 1299, 50),
            (category_map["Sports"], "Yoga Mat", 280, 699, 70),
        ]
        conn.executemany(
            "INSERT INTO products(category_id,name,cost_price,selling_price,stock) VALUES (?,?,?,?,?)",
            products
        )

        customer_ids = [r["customer_id"] for r in conn.execute("SELECT customer_id FROM customers")]
        product_rows = conn.execute("SELECT product_id,selling_price,cost_price FROM products").fetchall()
        today = date.today()
        random.seed(17)
        for offset in range(44):
            order_day = today - timedelta(days=random.randint(0, 150))
            customer_id = random.choice(customer_ids)
            cur = conn.execute(
                "INSERT INTO orders(customer_id,order_date,status) VALUES (?,?,?)",
                (customer_id, order_day.isoformat(), "Completed")
            )
            order_id = cur.lastrowid
            for _ in range(random.randint(1, 3)):
                product = random.choice(product_rows)
                qty = random.randint(1, 3)
                conn.execute(
                    """INSERT INTO order_items(order_id,product_id,quantity,unit_price,unit_cost)
                       VALUES (?,?,?,?,?)""",
                    (order_id, product["product_id"], qty, product["selling_price"], product["cost_price"])
                )
                conn.execute(
                    "UPDATE products SET stock = MAX(0, stock - ?) WHERE product_id = ?",
                    (qty, product["product_id"])
                )

        expense_categories = ["Marketing", "Rent", "Packaging", "Delivery", "Utilities"]
        for i in range(24):
            expense_day = today - timedelta(days=random.randint(0, 150))
            cat = random.choice(expense_categories)
            amount = random.choice([450, 800, 1200, 1750, 2200, 3000])
            conn.execute(
                """INSERT INTO expenses(expense_name,category,amount,expense_date,notes)
                   VALUES (?,?,?,?,?)""",
                (f"{cat} expense", cat, amount, expense_day.isoformat(), "Demo transaction")
            )
        conn.commit()

def query_df(sql, params=()):
    import pandas as pd
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def execute(sql, params=()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid

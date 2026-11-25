# NOVA — Business Sales and Profit Analytics System

A college mini-project combining **DBMS** and **Full Stack Development** using Python, Streamlit, SQLite, Pandas and Plotly.

## Features

- Business overview dashboard with revenue, gross profit, net profit and order KPIs
- Product catalogue: add, edit, delete and view products
- Customer management
- Sales entry with automatic stock deduction
- Expense tracking
- Interactive charts and product performance insights
- CSV exports
- DBMS Explorer to inspect relational tables and example SQL queries
- Automatically generated demo data on first run

## Requirements

- Python 3.9 or newer
- VS Code (recommended)

## Run in VS Code

1. Extract the ZIP file.
2. Open the extracted `Business_Sales_Analytics` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

5. Activate it on Windows:

   ```bash
   venv\Scripts\activate
   ```

   If using PowerShell and activation is blocked, run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```

6. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

7. Start the app:

   ```bash
   streamlit run app.py
   ```

8. The app opens at `http://localhost:8501`.

## Project structure

```text
Business_Sales_Analytics/
│
├── app.py             # Streamlit frontend and page navigation
├── database.py        # SQLite connection, schema and demo data
├── operations.py      # CRUD and sales business logic
├── analytics.py       # SQL-based analytics functions
├── requirements.txt   # Python dependencies
├── README.md          # Setup guide
└── sales.db           # Created automatically on first run
```

## Database schema

- `customers(customer_id PK, name, email, phone, city)`
- `categories(category_id PK, category_name)`
- `products(product_id PK, category_id FK, name, cost_price, selling_price, stock)`
- `orders(order_id PK, customer_id FK, order_date, status)`
- `order_items(item_id PK, order_id FK, product_id FK, quantity, unit_price, unit_cost)`
- `expenses(expense_id PK, expense_name, category, amount, expense_date, notes)`

### Relationships

- One customer can place many orders (1:M).
- One order can contain many order items (1:M).
- One product can appear in many order items (1:M).
- One category can contain many products (1:M).

## Profit calculations

- Revenue = quantity × unit selling price
- Cost of goods sold = quantity × unit cost
- Gross profit = revenue − cost of goods sold
- Net profit = gross profit − recorded operating expenses

The sale-time `unit_cost` and `unit_price` are stored in `order_items` to preserve historical sale values if a product's price changes later.

## DBMS concepts demonstrated

- Relational database design
- Primary keys and foreign keys
- NOT NULL, UNIQUE and CHECK constraints
- INSERT, SELECT, UPDATE and DELETE
- JOIN, GROUP BY, ORDER BY and aggregate functions
- Data integrity and referential integrity
- One-to-many relationships

## Notes

- The application creates `sales.db` automatically beside `database.py`.
- First launch inserts sample/demo records so the dashboard is not empty.
- This is an educational local demo. It does not include user login, cloud hosting, payment processing or production-grade access controls.
- The demo data is randomly generated once. Deleting `sales.db` and restarting the app recreates the sample database.

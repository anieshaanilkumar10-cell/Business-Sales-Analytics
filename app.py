import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from database import init_db, query_df, get_connection
from operations import (
    add_customer, add_product, update_product, delete_product,
    add_sale, add_expense
)
from analytics import (
    get_kpis, monthly_sales, product_performance,
    category_performance, recent_orders
)

st.set_page_config(
    page_title="NOVA | Business Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# ---------- Visual identity ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0b1020; color: #eef2ff; }
[data-testid="stHeader"] { background: rgba(11,16,32,0.85); }
[data-testid="stSidebar"] { background: #11182b; border-right: 1px solid #25304a; }
[data-testid="stSidebar"] * { color: #e8edff; }
h1,h2,h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -0.5px; }
h1 { color: #f4f6ff; font-weight: 800 !important; }
h2,h3 { color: #e5eaff; }
p, label, .stMarkdown { color: #c4cce0; }
div[data-testid="stMetric"] {
 background: linear-gradient(145deg,#18233c,#121a2d);
 border: 1px solid #2a3857; padding: 18px 20px; border-radius: 16px;
}
div[data-testid="stMetricLabel"] { color: #aab8d5; }
div[data-testid="stMetricValue"] { color: #f4f7ff; font-family: 'Manrope'; }
.stButton>button, .stFormSubmitButton>button {
 background: linear-gradient(90deg,#7c5cff,#35c6c8); color: white;
 border: 0; border-radius: 10px; font-weight: 700; padding: 0.55rem 1rem;
}
.stButton>button:hover, .stFormSubmitButton>button:hover { border: 1px solid #a99aff; color: white; }
div[data-testid="stDataFrame"] { border: 1px solid #283653; border-radius: 12px; }
.hero {
 background: radial-gradient(circle at 85% 20%,rgba(53,198,200,.22),transparent 30%),
             linear-gradient(120deg,#1a2450,#171d36 55%,#182b42);
 border: 1px solid #34466d; padding: 30px 32px; border-radius: 22px; margin-bottom: 22px;
}
.hero-kicker { color:#8fe4df; text-transform:uppercase; letter-spacing:2px; font-size:11px; font-weight:800; }
.hero-title { color:#fff; font-family:'Manrope'; font-size:34px; font-weight:800; margin:8px 0 5px; }
.hero-copy { color:#c1cce5; font-size:14px; margin:0; }
.section-label { color:#91a2c7; text-transform:uppercase; letter-spacing:1.7px; font-size:11px; font-weight:700; margin: 18px 0 8px; }
.pill { display:inline-block; padding:5px 10px; border-radius:30px; background:#1c3650; color:#85e5d6; font-size:11px; font-weight:700; }
.small-note { color:#8795b3; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("<div style='font-size:12px;letter-spacing:3px;color:#8ce1dc;font-weight:800'>✦ NOVA BUSINESS</div>", unsafe_allow_html=True)
    st.markdown("## Control room")
    st.caption("Sales • Profit • Performance")
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Sales", "Products", "Customers", "Expenses", "Insights", "Database"],
        label_visibility="visible"
    )
    st.markdown("---")
    st.markdown("<span class='pill'>● SYSTEM ONLINE</span>", unsafe_allow_html=True)
    st.caption("Demo workspace · SQLite database")
    st.caption("Built with Streamlit + Python + SQL")

# ---------- Helpers ----------
def money(value):
    return f"₹{value:,.0f}"

def page_header(kicker, title, subtitle):
    st.markdown(
        f"""<div class="hero">
        <div class="hero-kicker">{kicker}</div>
        <div class="hero-title">{title}</div>
        <p class="hero-copy">{subtitle}</p>
        </div>""",
        unsafe_allow_html=True
    )

def get_options(sql, label_col, id_col):
    df = query_df(sql)
    return {str(row[label_col]): int(row[id_col]) for _, row in df.iterrows()}

# ---------- Overview ----------
if page == "Overview":
    page_header("BUSINESS INTELLIGENCE / LIVE SNAPSHOT", "Make every sale count.", "A clear view of what your business earns, spends and keeps.")
    c1, c2 = st.columns([1, 2])
    with c1:
        period = st.selectbox("Reporting period", ["All time", "Last 30 days", "Last 90 days", "This year"])
    today = date.today()
    if period == "Last 30 days":
        start, end = today - timedelta(days=29), today
    elif period == "Last 90 days":
        start, end = today - timedelta(days=89), today
    elif period == "This year":
        start, end = date(today.year, 1, 1), today
    else:
        start = end = None

    k = get_kpis(start, end)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total revenue", money(k["revenue"]), help="Sales value before expenses")
    m2.metric("Gross profit", money(k["gross_profit"]), help="Revenue minus product cost")
    m3.metric("Net profit", money(k["net_profit"]), help="Gross profit minus recorded expenses")
    m4.metric("Orders", f'{k["orders"]:,}')
    st.markdown("<div class='section-label'>PERFORMANCE PULSE</div>", unsafe_allow_html=True)
    left, right = st.columns([1.55, 1])
    with left:
        monthly = monthly_sales()
        if not monthly.empty:
            fig = px.area(monthly, x="month", y="revenue", title="Revenue momentum",
                          markers=True, color_discrete_sequence=["#55d6cf"])
            fig.update_traces(line=dict(width=3), fillcolor="rgba(85,214,207,.13)")
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)", font_color="#dce5ff",
                              margin=dict(l=10,r=10,t=55,b=10), yaxis_title="Revenue (₹)", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add sales to see revenue trends.")
    with right:
        cats = category_performance()
        if not cats.empty:
            fig = px.pie(cats, names="category", values="revenue", hole=.62,
                         title="Revenue by category",
                         color_discrete_sequence=["#7c5cff","#35c6c8","#f5b85c","#f17c9a","#83a8ff"])
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                              font_color="#dce5ff", margin=dict(l=5,r=5,t=55,b=5),
                              legend=dict(orientation="h", y=-.15))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category insights will appear here.")
    st.markdown("<div class='section-label'>LATEST TRANSACTIONS</div>", unsafe_allow_html=True)
    recent = recent_orders().head(7)
    if not recent.empty:
        view = recent[["order_id","order_date","customer","products","units","amount"]].copy()
        view.columns = ["Order ID","Date","Customer","Items","Units","Amount (₹)"]
        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Add your first sale from the Sales page.")

# ---------- Sales ----------
elif page == "Sales":
    page_header("TRANSACTION CENTRE", "Record a sale.", "Create an order, update stock automatically and preserve the sale-time cost for accurate profit.")
    customers = get_options("SELECT customer_id,name FROM customers ORDER BY name", "name", "customer_id")
    products = query_df("SELECT product_id,name,selling_price,cost_price,stock FROM products ORDER BY name")
    if not customers or products.empty:
        st.warning("Add at least one customer and one product before recording a sale.")
    else:
        product_labels = {f'{r["name"]} · {money(r["selling_price"])} · {r["stock"]} in stock': int(r["product_id"]) for _,r in products.iterrows()}
        with st.form("sale_form"):
            a,b = st.columns(2)
            customer_name = a.selectbox("Customer", list(customers.keys()))
            product_label = b.selectbox("Product", list(product_labels.keys()))
            c,d = st.columns(2)
            quantity = c.number_input("Quantity", min_value=1, max_value=1000, value=1, step=1)
            order_date = d.date_input("Order date", value=date.today())
            selected = products[products.product_id == product_labels[product_label]].iloc[0]
            st.caption(f"Unit selling price: {money(selected.selling_price)}  ·  Estimated gross profit per unit: {money(selected.selling_price-selected.cost_price)}")
            submitted = st.form_submit_button("＋ Save sale", use_container_width=True)
            if submitted:
                try:
                    oid = add_sale(customers[customer_name], product_labels[product_label], int(quantity), order_date.isoformat())
                    st.success(f"Sale #{oid} recorded. Stock has been updated.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    st.markdown("<div class='section-label'>ORDER HISTORY</div>", unsafe_allow_html=True)
    orders = recent_orders()
    st.dataframe(orders, use_container_width=True, hide_index=True)

# ---------- Products ----------
elif page == "Products":
    page_header("CATALOGUE MANAGEMENT", "Your products, organised.", "Manage pricing, inventory and categories from one place.")
    cats = get_options("SELECT category_id,category_name FROM categories ORDER BY category_name", "category_name", "category_id")
    tab1, tab2, tab3 = st.tabs(["＋ Add product", "✎ Edit product", "▤ Product catalogue"])
    with tab1:
        with st.form("add_product"):
            name = st.text_input("Product name")
            category = st.selectbox("Category", list(cats.keys()))
            a,b,c = st.columns(3)
            cost = a.number_input("Cost price (₹)", min_value=0.0, value=100.0, step=50.0)
            price = b.number_input("Selling price (₹)", min_value=0.0, value=199.0, step=50.0)
            stock = c.number_input("Opening stock", min_value=0, value=10, step=1)
            if st.form_submit_button("Add to catalogue"):
                if not name.strip():
                    st.error("Please enter a product name.")
                elif price < cost:
                    st.error("Selling price is below cost price. Please verify.")
                else:
                    try:
                        add_product(cats[category], name, cost, price, int(stock))
                        st.success("Product added successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not add product: {e}")
    with tab2:
        product_df = query_df("SELECT product_id,name,category_id,cost_price,selling_price,stock FROM products ORDER BY name")
        if not product_df.empty:
            ids = product_df.product_id.tolist()
            chosen = st.selectbox("Choose product", ids, format_func=lambda x: product_df.loc[product_df.product_id==x,"name"].iloc[0])
            row = product_df[product_df.product_id==chosen].iloc[0]
            cat_names = list(cats.keys())
            current_cat = next((n for n,i in cats.items() if i == row.category_id), cat_names[0])
            with st.form("edit_product"):
                new_name = st.text_input("Product name", value=row["name"])
                new_cat = st.selectbox("Category", cat_names, index=cat_names.index(current_cat))
                a,b,c = st.columns(3)
                new_cost = a.number_input("Cost price", min_value=0.0, value=float(row.cost_price))
                new_price = b.number_input("Selling price", min_value=0.0, value=float(row.selling_price))
                new_stock = c.number_input("Stock", min_value=0, value=int(row.stock))
                if st.form_submit_button("Save changes"):
                    if new_price < new_cost:
                        st.error("Selling price should be equal to or greater than cost price.")
                    else:
                        update_product(int(chosen), cats[new_cat], new_name, new_cost, new_price, int(new_stock))
                        st.success("Product updated.")
                        st.rerun()
            with st.expander("Delete product"):
                st.warning("Products already used in sales cannot be deleted, to protect transaction history.")
                if st.button("Delete selected product", type="secondary"):
                    try:
                        delete_product(int(chosen))
                        st.success("Product deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        else:
            st.info("No products available.")
    with tab3:
        catalog = query_df("""
            SELECT p.product_id,p.name,c.category_name,p.cost_price,p.selling_price,
                   (p.selling_price-p.cost_price) AS unit_margin,p.stock
            FROM products p JOIN categories c ON p.category_id=c.category_id
            ORDER BY p.name
        """)
        st.dataframe(catalog, use_container_width=True, hide_index=True)
        st.download_button("Download product catalogue CSV", catalog.to_csv(index=False), "product_catalogue.csv", "text/csv")

# ---------- Customers ----------
elif page == "Customers":
    page_header("CUSTOMER RELATIONSHIPS", "Know your customers.", "Keep customer details tidy and understand who is buying from your business.")
    with st.expander("＋ Add a customer", expanded=True):
        with st.form("customer_form"):
            a,b = st.columns(2)
            name = a.text_input("Full name")
            email = b.text_input("Email address")
            c,d = st.columns(2)
            phone = c.text_input("Phone number")
            city = d.text_input("City")
            if st.form_submit_button("Save customer"):
                if not name.strip():
                    st.error("Customer name is required.")
                else:
                    try:
                        add_customer(name,email,phone,city)
                        st.success("Customer added.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not add customer. Check whether the email already exists. Details: {e}")
    customer_df = query_df("""
        SELECT c.customer_id,c.name,c.email,c.phone,c.city,
               COUNT(DISTINCT o.order_id) AS orders,
               COALESCE(SUM(oi.quantity*oi.unit_price),0) AS lifetime_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id=o.customer_id
        LEFT JOIN order_items oi ON o.order_id=oi.order_id
        GROUP BY c.customer_id
        ORDER BY lifetime_value DESC
    """)
    st.dataframe(customer_df, use_container_width=True, hide_index=True)
    st.download_button("Download customers CSV", customer_df.to_csv(index=False), "customers.csv", "text/csv")

# ---------- Expenses ----------
elif page == "Expenses":
    page_header("COST CONTROL", "Track what it takes.", "Record operating expenses to move from revenue to a more meaningful net-profit picture.")
    with st.form("expense_form"):
        a,b = st.columns(2)
        name = a.text_input("Expense name", placeholder="e.g. Instagram campaign")
        category = b.selectbox("Category", ["Marketing","Rent","Packaging","Delivery","Utilities","Salaries","Other"])
        c,d = st.columns(2)
        amount = c.number_input("Amount (₹)", min_value=0.0, value=500.0, step=100.0)
        expense_date = d.date_input("Expense date", value=date.today())
        notes = st.text_input("Notes (optional)")
        if st.form_submit_button("＋ Add expense"):
            if not name.strip():
                st.error("Please enter an expense name.")
            else:
                add_expense(name,category,amount,expense_date.isoformat(),notes)
                st.success("Expense recorded.")
                st.rerun()
    expense_df = query_df("SELECT expense_id,expense_name,category,amount,expense_date,notes FROM expenses ORDER BY expense_date DESC")
    st.markdown("<div class='section-label'>EXPENSE LEDGER</div>", unsafe_allow_html=True)
    st.dataframe(expense_df, use_container_width=True, hide_index=True)
    st.download_button("Download expenses CSV", expense_df.to_csv(index=False), "expenses.csv", "text/csv")

# ---------- Insights ----------
elif page == "Insights":
    page_header("DISCOVER THE SIGNAL", "Turn numbers into decisions.", "Explore product winners, category mix and monthly performance.")
    products = product_performance()
    categories = category_performance()
    monthly = monthly_sales()
    if not products.empty:
        a,b = st.columns(2)
        with a:
            fig = px.bar(products.sort_values("revenue"), x="revenue", y="product", orientation="h",
                         title="Products ranked by revenue", color="revenue",
                         color_continuous_scale=["#263b65","#35c6c8"])
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font_color="#dce5ff", coloraxis_showscale=False, xaxis_title="Revenue (₹)", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with b:
            fig = px.bar(products.sort_values("gross_profit"), x="gross_profit", y="product", orientation="h",
                         title="Products ranked by gross profit", color="gross_profit",
                         color_continuous_scale=["#49345f","#a88bff"])
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font_color="#dce5ff", coloraxis_showscale=False, xaxis_title="Gross profit (₹)", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("<div class='section-label'>PRODUCT SCORECARD</div>", unsafe_allow_html=True)
        st.dataframe(products, use_container_width=True, hide_index=True)
    if not monthly.empty:
        fig = px.line(monthly, x="month", y=["revenue","gross_profit"], markers=True,
                      title="Monthly revenue vs gross profit")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#dce5ff", yaxis_title="Amount (₹)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    if not categories.empty:
        st.dataframe(categories, use_container_width=True, hide_index=True)

# ---------- Database ----------
elif page == "Database":
    page_header("DBMS EXPLORER", "See the data behind the dashboard.", "A live look at the relational tables powering NOVA. Primary and foreign keys connect the records.")
    table_info = {
        "Customers": "customers",
        "Categories": "categories",
        "Products": "products",
        "Orders": "orders",
        "Order items": "order_items",
        "Expenses": "expenses"
    }
    selected_table = st.selectbox("Select database table", list(table_info.keys()))
    table_name = table_info[selected_table]
    data = query_df(f"SELECT * FROM {table_name} ORDER BY 1 DESC")
    st.dataframe(data, use_container_width=True, hide_index=True)
    st.caption(f"Table: {table_name} · Records: {len(data)}")
    with st.expander("Explore example SQL queries"):
        st.code("""-- 1. Total revenue
SELECT SUM(quantity * unit_price) AS revenue
FROM order_items;

-- 2. Product-wise sales using JOIN
SELECT p.name, SUM(oi.quantity) AS units_sold
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name;

-- 3. Customers with more than one order
SELECT c.name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
HAVING COUNT(o.order_id) > 1;

-- 4. Gross profit
SELECT SUM(quantity * (unit_price - unit_cost)) AS gross_profit
FROM order_items;""", language="sql")
    st.info("The Database page is useful during your DBMS demonstration: show the tables, relationships and SQL queries.")

st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:15px;">
    <h3 style="color:#8fe4df; margin-bottom:5px;">NOVA</h3>
    <p style="color:#aab8d5; letter-spacing:2px;">
        BUSINESS INTELLIGENCE
    </p>
    <p style="color:#657493; font-size:12px;">
        Smarter insights. Better business decisions.
    </p>
    <p style="color:#657493; font-size:11px;">
        © 2026 NOVA. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)
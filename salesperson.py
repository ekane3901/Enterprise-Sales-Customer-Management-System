import sqlite3
import datetime

def salesperson(uid, conn):
    while True:
        print("\nSALESPERSON MENU")
        print("1. Check or update a product")
        print("2. Generate weekly sales report")
        print("3. View top-selling products")
        print("4. Logout")

        choice = input("Enter choice (1/2/3/4): ").strip()

        if choice == "1":
            check_update_product(conn)
        elif choice == "2":
            gen_weekly_report(conn)
        elif choice == "3":
            see_top_products(conn)
        elif choice == "4":
            print("Logging user out...")
            break
        else:
            print("Invalid choice. Try again.")


def check_update_product(conn):
    pid = input("Enter product ID to view or update: ").strip()

    query = """
        SELECT pid, name, category, price, stock_count, descr
        FROM products
        WHERE pid = ?
    """
    cur = conn.execute(query, (pid,))
    product = cur.fetchone()

    if not product:
        print("No product found with that ID.")
        return

    print("\n--- PRODUCT DETAILS ---")
    print(f"Product ID: {product[0]}")
    print(f"Name: {product[1]}")
    print(f"Category: {product[2]}")
    print(f"Price: ${product[3]:.2f}")
    print(f"Stock count: {product[4]}")
    print(f"Description: {product[5]}")

    ans = input("\nWould you like to update the price or stock count? (y/n): ").lower()
    if ans == 'y':
        try:
            new_price = float(input("Enter new price: ").strip())
            new_stock = int(input("Enter new stock count: ").strip())

            update_query = """
                UPDATE products
                SET price = ?, stock_count = ?
                WHERE pid = ?
            """
            conn.execute(update_query, (new_price, new_stock, pid))
            conn.commit()

            print("Product updated successfully!")
        except ValueError:
            print("Invalid input. No changes made.")
    else:
        print("No update to products made.")


def gen_weekly_report(conn):
    print("\n---- WEEKLY SALES REPORT ----")

    query = """
        SELECT o.ono, o.cid, ol.pid, ol.qty, ol.uprice
        FROM orders o
        JOIN orderlines ol ON o.ono = ol.ono
        WHERE date(o.odate) >= date('now', '-7 day')
    """
    cur = conn.execute(query)
    rows = cur.fetchall()

    if not rows:
        print("No sales in the past 7 days.")
        return

    distinct_orders = set()
    distinct_products = set()
    distinct_customers = set()
    customer_spending = {}

    total_sales = 0

    for ono, cid, pid, qty, uprice in rows:
        distinct_orders.add(ono)
        distinct_products.add(pid)
        distinct_customers.add(cid)

        total = qty * uprice
        total_sales += total
        customer_spending[cid] = customer_spending.get(cid, 0) + total

    avg_spent = sum(customer_spending.values()) / len(distinct_customers)

    print(f"\nNumber of distinct orders: {len(distinct_orders)}")
    print(f"Number of distinct products sold: {len(distinct_products)}")
    print(f"Number of distinct customers: {len(distinct_customers)}")
    print(f"Average amount spent per customer: ${avg_spent:.2f}")
    print(f"Total sales amount: ${total_sales:.2f}")


def see_top_products(conn):
    print("\n---- TOP PRODUCTS ----")

    # top 3 by number of distinct orders
    query_orders = """
        SELECT pid, name, order_count
        FROM (
        SELECT p.pid, p.name, COUNT(DISTINCT ol.ono) AS order_count, DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT ol.ono) DESC) AS rnk
        FROM products p
        JOIN orderlines ol ON p.pid = ol.pid
        GROUP BY p.pid, p.name
        ) ranked
        WHERE rnk <= 3
        ORDER BY order_count DESC;
    """

    cur = conn.execute(query_orders)
    top_orders = cur.fetchall()

    if top_orders:
        print("\nTop 3 Products by Number of Orders:")
        for pid, name, count in top_orders:
            print(f"  {pid}: {name} — in {count} distinct orders")
    else:
        print("\nNo order data available.")

    # top 3 by total views
    query_views = """
        SELECT p.pid, p.name, COUNT(*) AS view_count
        FROM products p
        JOIN viewedProduct v ON p.pid = v.pid
        GROUP BY p.pid, p.name
        ORDER BY view_count DESC
        LIMIT 3
    """
    cur = conn.execute(query_views)
    top_views = cur.fetchall()

    if top_views:
        print("\nTop 3 Products by Views:")
        for pid, name, views in top_views:
            print(f"  {pid}: {name} — viewed {views} times")
    else:
        print("\nNo product view data available.")

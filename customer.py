from accounts import clear
import sqlite3
import datetime

def customer_menu(cid, sessionNo, conn):
    while True:
        print("\nCUSTOMER MENU")
        print("1. Search for products")
        print("2. View/Manage cart")
        print("3. Checkout")
        print("4. View past orders")
        print("5. Logout")

        choice = input("Enter choice (1/2/3/4/5): ").strip()

        if choice == "1": # Search for products
            clear()
            search_products(cid, sessionNo, conn)

        elif choice == "2": # Manage Cart
            clear()
            view_cart(cid, sessionNo, conn)
        
        elif choice == "3": # Checkout
            clear()
            checkout(cid, sessionNo, conn)
        
        elif choice == "4": # View past orders
            clear()
            view_past_orders(cid, conn)
        
        elif choice == "5": # Logout
            clear()
            print("Logging out..")
            break

        else:
            clear()
            print("Not a valid choice. Try again..")

def search_products(cid, sessionNo, conn):
    cursor = conn.cursor()
    keyword = input("Enter keyword: ").strip()
    
    
    if not keyword:
        print("Please enter at least one keyword.")
        return
    
    ts = datetime.datetime.now()

    # Log the search
    cursor.execute('''
                   INSERT INTO search (cid, sessionNo, ts, query)
                   VALUES (?, ?, ?, ?)''', (cid, sessionNo, ts, keyword))
    conn.commit()

    # AND semantics for multiple keywords 
    words = keyword.lower().split()
    # For each keyword, we build (name LIKE ? OR descr LIKE ?)
    conditions = " AND ".join(["(lower(name) LIKE ? OR lower(descr) LIKE ?)"] * len(words))
    params = []

    for w in words:
        like = f"%{w}%"
        params.extend([like, like])


    sql = f"SELECT * FROM products WHERE {conditions}"
    cursor.execute(sql, params)
    products = cursor.fetchall()

    if not products:
        print("\nNo products found")
        return

    # 5 products per page
    page = 0
    per_page = 5
    total_pages = (len(products) + per_page - 1) // (per_page)

    while True:
        start = page * per_page
        end = start + per_page
        subset = products[start:end]

        print(f"\nSearch Results (Page {page + 1}/{total_pages})")
        for i, j in enumerate(subset, start=1):
            print(f"{i}. {j['name']} (${j['price']:.2f})  Stock: {j['stock_count']}")

        print("\nNext(N), Prev(P), View Product(V), Quit(Q)")
        action = input("Action: ").lower()

        if action == "n" and page < total_pages - 1:
            page += 1
        
        elif action == "p" and page > 0:
            page -= 1
        
        elif action == "v":
            try: 
                idx = int(input("Enter number to view the details: ")) - 1
                if 0 <= idx < len(subset):
                    view_product(cid, sessionNo, conn, subset[idx]["pid"])
                else:
                    print("Not a valid selection")
            except ValueError:
                print("Please enter a valid number")

        elif action == "q":
            break

        else:
             print("Not a valid input")


def view_product(cid, sessionNo, conn, pid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE pid = ?", (pid,))   
    product = cursor.fetchone()

    if not product:
        print("Product not found")
        return


    # Display product details
    print("\nProduct Details:")
    print(f"Name: {product['name']}")
    print(f"Category: {product['category']}")
    print(f"Price: ${product['price']:.2f}")
    print(f"Stock Available: {product['stock_count']}")
    print(f"Description: {product['descr']}")
    print("\n")



    # Log the view
    ts = datetime.datetime.now()
    cursor.execute('''INSERT INTO viewedProduct (cid, sessionNo, ts, pid)
                      VALUES (?, ?, ?, ?)''', (cid, sessionNo, ts, pid))
    conn.commit()

    # Add to cart option
    if product["stock_count"] <= 0:
        print("This product is currently out of stock")
        return 
    
    choice = input("Would you like to add this product to your cart? (y/n): ").strip().lower()
    if choice == 'y':
        try:
            add_to_cart(cid, sessionNo, conn, pid)
            conn.commit()  
            # print(f"'{product['name']}' added to your cart.")
        except Exception as e:
            print(f"Could not add to cart")
    else:
        clear()
        print("Returning to search results...")
    



def add_to_cart(cid, sessionNo, conn, pid):
    cursor = conn.cursor()

    # Get current stock for this product
    cursor.execute("SELECT stock_count, name FROM products WHERE pid = ?", (pid,))
    product = cursor.fetchone()

    if not product:
        print("Product not found.")
        return

    stock = product["stock_count"]
    pname = product["name"]

    if stock <= 0:
        print(f"'{pname}' is out of stock.")
        return

    # check if item already in cart:
    cursor.execute('''SELECT qty FROM cart
                      WHERE cid = ? AND sessionNo = ? 
                      AND pid = ?''', (cid, sessionNo, pid))
    row = cursor.fetchone()

    # Determine new quantity
    new_qty = 1 if not row else row["qty"] + 1

    # Stock validation
    if new_qty > stock:
        print(f"Not enough stock to add another '{pname}'. Available: {stock}")
        return
    
    try:
        if row:
            cursor.execute("""
                UPDATE cart SET qty = ?
                WHERE cid = ? AND sessionNo = ? AND pid = ?
            """, (new_qty, cid, sessionNo, pid))
        else:
            cursor.execute("""
                INSERT INTO cart (cid, sessionNo, pid, qty)
                VALUES (?, ?, ?, 1)
            """, (cid, sessionNo, pid))

        conn.commit()
        print(f"'{pname}' added to cart (Quantity: {new_qty})")

    except Exception as e:
        print(f"Could not update cart")


def view_cart(cid, sessionNo, conn):
    cursor = conn.cursor()
    cursor.execute('''SELECT c.pid, p.name, p.price, c.qty, p.stock_count
                      FROM cart c
                      JOIN products p ON c.pid = p.pid
                      WHERE c.cid = ? AND c.sessionNo = ?''', (cid, sessionNo))
    
    items = cursor.fetchall()
    '''if not items:
        print("\nCart is empty")
        return
    '''
    while True:
        cursor.execute('''SELECT c.pid, p.name, p.price, c.qty, p.stock_count
                      FROM cart c
                      JOIN products p ON c.pid = p.pid
                      WHERE c.cid = ? ''', (cid,))
    
        items = cursor.fetchall()
        print("\nCart: ")
        for i, item in enumerate(items, start=1):
            print(f"{i}. {item['name']}, Price: ${item['price']:.2f}, Qty: {item['qty']}, Stock: {item['stock_count']}, Line Total: ${item['price']*item['qty']:.2f}")

        total = sum(item['price']*item['qty'] for item in items)
        print(f"\nCart Total: ${total:.2f}")

        print("\nOptions: Update quantity(U), Remove product(R), Quit(Q)")
        action = input("Action: ").strip().lower()

        if action == 'u':
            try:
                    
                idx = int(input("Enter item number to update: ")) - 1
                if 0 <= idx < len(items):
                    new_qty = int(input(f"Enter new quantity for {items[idx]['name']}: "))
                    if 0 < new_qty <= items[idx]['stock_count']:
                        cursor.execute('''UPDATE cart SET qty = ?
                                        WHERE cid = ? AND sessionNo = ?
                                        AND pid = ?''', (new_qty, cid, sessionNo, items[idx]['pid']))
                        conn.commit()
                        print("Quantity was updated")
                    else:
                        print("Not a valid quantity")
                else:
                    print("Not a valid selection")
            except ValueError:
                print("Please enter a valid number")


        elif action == 'r':
            try:

                idx = int(input("Enter item number to remove: ")) - 1

                if 0 <= idx < len(items):
                    pid_to_remove = items[idx]['pid']
                    cursor.execute('''DELETE FROM cart
                                    WHERE cid = ? AND sessionNo = ?
                                    AND pid = ?''', (cid, sessionNo, pid_to_remove))
                    conn.commit()
                    print(f"Removed {items[idx]['name']} from cart")

                    cursor.execute('''SELECT c.pid, p.name, p.price, c.qty, p.stock_count
                                    FROM cart c
                                    JOIN products p ON c.pid = p.pid
                                    WHERE c.cid = ? AND c.sessionNo = ?''', (cid, sessionNo))
                    items = cursor.fetchall()

                else:
                    print("not a valid selection")
            except ValueError:
                print("Please enter a valid number.")

        elif action == 'q':
            break

        else:
            print("Not a valid input. Choose U, R, or Q")


def checkout(cid, sessionNo, conn):
    cursor = conn.cursor()

    # Get cart items
    cursor.execute('''SELECT c.pid, p.name, p.price, c.qty, p.stock_count
                      FROM cart c
                      JOIN products p ON c.pid = p.pid
                      WHERE c.cid = ? AND c.sessionNo = ?''', (cid, sessionNo))
    items = cursor.fetchall()
    
    if not items:
        print("\nCart is empty, can't checkout!!!")
        return


    # Validate stock before proceeding
    for item in items:
        if item["qty"] > item["stock_count"]:
            print(f"Not enough stock for '{item['name']}'. "
                  f"Available: {item['stock_count']}, In cart: {item['qty']}")
            print("Please update your cart before checking out.")
            return

    # Display summary
    total = sum(item['price']*item['qty'] for item in items)
    print("\nCheckout Summary:")
    for item in items:
        print(f"{item['name']}: Qty {item['qty']} × ${item['price']:.2f} = ${item['price'] * item['qty']:.2f}")
    print(f"\nOrder Total: ${total:.2f}")
    print("\n")

    confirm = input("\nDo you want to place the order? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Checkout cancelled!!!")
        return
    
    # Ask for shipping address
    shipping_address = input("Enter shipping address: ").strip()
    while not shipping_address:
        print("Shipping address cannot be blank.")
        shipping_address = input("Enter shipping address: ").strip()

    try:
        # begin the transaction
        cursor.execute("BEGIN IMMEDIATE")


        # New order number
        cursor.execute("SELECT MAX(ono) FROM orders")
        max_ono = cursor.fetchone()[0]
        ono = 1 if max_ono is None else max_ono + 1 
        odate = datetime.datetime.now().date()

        # Insert the order record
        cursor.execute('''INSERT INTO orders (ono, cid, sessionNo, odate, shipping_address)
                        VALUES (?, ?, ?, ?, ?)''', (ono, cid, sessionNo, odate, shipping_address))
        
        # Record order lines and update stock
        for lineNo, item in enumerate(items, start=1):
            cursor.execute('''INSERT INTO orderlines (ono, lineNo, pid, qty, uprice)
                            VALUES (?, ?, ?, ?, ?)''', (ono, lineNo, item['pid'], item['qty'], item['price']))
            
            cursor.execute('''UPDATE products SET stock_count = stock_count - ?
                            WHERE pid = ? AND stock_count >= ?''', (item['qty'], item['pid'], item['qty']))

            if cursor.rowcount == 0:
                raise RuntimeError(f"Insufficient stock for '{item['name']}' during checkout.")

        """
        # update product stock
        new_stock = item['stock_count'] - item['qty']
        cursor.execute('''UPDATE products SET stock_count = ? WHERE pid = ?''', (new_stock, item['pid']))
        """
    # Empty the cart
        cursor.execute('''DELETE FROM cart WHERE cid = ? AND sessionNo = ?''', (cid, sessionNo))

        conn.commit()
        print(f"\nOrder {ono} placed successfully!!!")

    except Exception:
        conn.rollback()
        print(f"\nCould not complete checkout")

def view_past_orders(cid, conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.ono, o.odate, o.shipping_address, 
               SUM(ol.qty * ol.uprice) AS total
        FROM orders o
        JOIN orderlines ol ON o.ono = ol.ono
        WHERE o.cid = ?
        GROUP BY o.ono
        ORDER BY o.odate DESC
    ''', (cid,))
    orders = cursor.fetchall()

    if not orders:
        print("\nNo past orders found.")
        return

    page = 0
    per_page = 5
    total_pages = (len(orders) + per_page - 1) // per_page

    while True:
        start = page * per_page
        end = start + per_page
        subset = orders[start:end]

        print(f"\nPast Orders (Page {page + 1}/{total_pages})")
        for i, order in enumerate(subset, start=1):
            print(f"{i}. Order #{order['ono']} | Date: {order['odate']} | "
                  f"Address: {order['shipping_address']} | Total: ${order['total']:.2f}")

        print("\nNext(N), Prev(P), View Order(V), Quit(Q)")
        action = input("Action: ").lower()

        if action == 'n' and page < total_pages - 1:
            page += 1

        elif action == 'p' and page > 0:
            page -= 1

        elif action == 'v':
            try: 
                    
                idx = int(input("Enter order number to view details: ")) - 1
                if 0 <= idx < len(subset):
                    view_order_details(conn, subset[idx]['ono'])
                else:
                    print("Not a valid selection.")
            except ValueError:
                print("Please enter a valid number.")

        elif action == 'q':
            break
        else:
            print("Not a valid input.")


def view_order_details(conn, ono):
    cursor = conn.cursor()

    # Get order header (order number, date, address)
    cursor.execute("""
        SELECT o.ono, o.odate, o.shipping_address
        FROM orders o
        WHERE o.ono = ?
    """, (ono,))
    order = cursor.fetchone()

    if not order:
        print("Order not found.")
        return

    # Get line items for this order
    cursor.execute("""
        SELECT p.name AS pname, p.category, ol.qty, ol.uprice, (ol.qty * ol.uprice) AS line_total
        FROM orderlines ol
        JOIN products p ON ol.pid = p.pid
        WHERE ol.ono = ?
        ORDER BY ol.lineNo
    """, (ono,))
    lines = cursor.fetchall()

    if not lines:
        print("\nNo items found for this order.")
        return

    grand_total = sum(line["line_total"] for line in lines)

    # Header
    print("\n==============================")
    print(f"Order #{order['ono']}")
    print(f"Date: {order['odate']}")
    print(f"Shipping Address: {order['shipping_address']}")
    print("------------------------------")

    # Line items
    for line in lines:
        print(f"{line['pname']} ({line['category']})")
        print(f"  Qty: {line['qty']}  Unit Price: ${line['uprice']:.2f}  "
              f"Line Total: ${line['line_total']:.2f}")
        print()

    # Grand total Footer
    print("------------------------------")
    print(f"Grand Total: ${grand_total:.2f}")
    print("\n")
    
    

    

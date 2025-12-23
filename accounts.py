import sqlite3
import getpass
import datetime
import os

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def init_db(db_file: str):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row 
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def generate_next_id(cursor, table: str, id_column: str) -> int:
    cursor.execute(f"SELECT MAX({id_column}) FROM {table}")
    row = cursor.fetchone()
    max_id = row[0] if row else None
    return 1 if max_id is None else max_id + 1
    
def start_session(conn, cid: int) -> int:
    cur = conn.cursor()
    # Next sessionNo for this cid
    cur.execute("SELECT MAX(sessionNo) AS maxs FROM sessions WHERE cid=?", (cid,))
    maxs = cur.fetchone()["maxs"]
    session_no = 1 if maxs is None else maxs + 1
    cur.execute("""
        INSERT INTO sessions (cid, sessionNo, start_time, end_time)
        VALUES (?, ?, ?, NULL)
    """, (cid, session_no, datetime.datetime.now()))
    conn.commit()
    return session_no

def end_session(conn, cid: int, session_no: int) -> None:
    cur = conn.cursor()
    cur.execute("""
        UPDATE sessions SET end_time = ?
        WHERE cid = ? AND sessionNo = ? AND end_time IS NULL
    """, (datetime.datetime.now(), cid, session_no))
    conn.commit()

# ---------- Signup ----------
def signup(conn):
    clear()
    print("=== SIGN UP ===\n")
    cursor = conn.cursor()

    name = input("Enter your name: ").strip()
    while not name:
        print('Field Cannot be blank. Please enter a valid name.')
        name = input("Enter your name: ").strip()
    
    email = input("Enter your email: ").strip().lower()
    while not email:
        print('Field Cannot be blank. Please enter a valid email.')
        email = input("Enter your email: ").strip()

    password = getpass.getpass("Choose a password: ")
    while not password.strip():
        print('Field Cannot be blank. Please enter a valid password.')
        password = getpass.getpass("Choose a password: ")

    confirm = getpass.getpass("Confirm password: ")
    while not confirm.strip():
        print('Field Cannot be blank. Please enter a valid password.')
        confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("\n❌ Passwords do not match.")
        input("\nPress Enter to continue...")
        return

    # Check if email already exists
    cursor.execute("SELECT cid FROM customers WHERE lower(email)=lower(?)", (email,))
    if cursor.fetchone():
        print("\n❌ This email is already registered.")
        input("\nPress Enter to continue...")
        return

    try:
        # One id is used for both tables (customers cid should reference users uid)
        uid = generate_next_id(cursor, "users", "uid")
        cid = uid

        # Insert into users and customers tables
        cursor.execute("INSERT INTO users (uid, pwd, role) VALUES (?, ?, ?)", (uid, confirm, "customer"))
        cursor.execute("INSERT INTO customers (cid, name, email) VALUES (?, ?, ?)", (cid, name, email))
        conn.commit()
        print(f"\n✅ Account created successfully! User ID/Customer ID: {uid}")
    except sqlite3.Error as e:
        print("\n❌ Database error:", e)

    input("\nPress Enter to continue...")

# ---------- Login ----------
def login(conn):
    clear()
    print("=== LOGIN ===\n")
    try:
        uid = int(input("User ID: ").strip())
    except ValueError:
        print("\n❌ Invalid User ID.")
        input("\nPress Enter to continue...")
        return None, None,  None # uid, role, sessionNo

    password = getpass.getpass("Password: ")

    cursor = conn.cursor()
    cursor.execute("SELECT pwd, role FROM users WHERE uid=?", (uid,))
    row = cursor.fetchone()

    if not row:
        print("\n❌ User ID not found.")
        input("\nPress Enter to continue...")
        return None, None, None
    
    stored_pass, role = row["pwd"], row["role"]
    if password != stored_pass:
        print("\n❌ Invalid password.")
        input("\nPress Enter to continue...")
        return None, None, None
    
    # If customer, cid == uid. Start a session
    session_no = None
    if role == "customer":
        cid = uid
        session_no = start_session(conn, cid)
        print(f"\n✅ Login successful! Role: {role}  (Session #{session_no})")
        input("\nPress Enter to continue...")
        return cid, role, session_no
    else:
        # for salesperson, no session row needed for customer tables
        print(f"\n✅ Login successful! Role: {role}")
        input("\nPress Enter to continue...")
        return uid, role, None

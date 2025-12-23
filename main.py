from accounts import init_db, signup, login, end_session, clear
from customer import customer_menu
from salesperson import salesperson

# from salesperson import salesperson_menu
import sys

def main():

    if len(sys.argv) != 2:
        print("Usage: python test1.py <database_file>")
        sys.exit(1)
    
    db_file = sys.argv[1]

    conn = init_db(db_file)
    while True:
        clear()
        print("1) Login")
        print("2) Sign up")
        print("3) Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            who, role, session_no = login(conn)
            
            if role == "customer" and who is not None:
                try:
                    customer_menu(who, session_no, conn)
                finally:
                    if session_no is not None:
                        end_session(conn, who, session_no)

            elif role == "sales" and who is not None:
                try:
                    salesperson(who, conn)
                finally:
                    if session_no is not None:
                        end_session(conn, who, session_no)

        
        elif choice == "2":
            signup(conn)

        elif choice == "3":
            clear()
            print("Goodbye!")
            conn.close()
            break

        else:
            print("Not a valid choice")
            input("Press Enter to continue")

if __name__ == "__main__":
    main()


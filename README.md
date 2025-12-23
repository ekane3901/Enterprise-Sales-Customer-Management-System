# Enterprise-Sales-Customer-Management-System

## Overview
This project is a Python-based Command Line Interface (CLI) application that simulates an enterprise sales and customer management system. The system integrates SQLite for secure data storage and retrieval, and demonstrates practical use of SQL in a host programming language.

The goal of the project is twofold: 
1. Teach the use of SQL in a host programming language (Python).  
2. Demonstrate functionalities that arise from combining SQL with a host language to manage enterprise data.

---

## Features

### Customer Functionalities
- **Search Products:** Search by keywords matching product names or descriptions (case-insensitive). Search history is recorded. Results are paginated (5 products per page).  
- **Product Details & Cart Management:** View product details, add to cart, update quantities, and remove items.  
- **Checkout:** Process orders with automatic order numbers, timestamps, and stock updates.  
- **Order History:** View past orders in reverse chronological order, with detailed line items and totals.  

### Salesperson Functionalities
- **Product Management:** View and update product details including price and stock count.  
- **Sales Reports:** Generate weekly sales summaries with total sales, distinct orders, and customer metrics.  
- **Top-Selling Products:** View top products by number of orders and total views.  

### Security & Validation
- Password input is masked.  
- SQL injection attacks are mitigated.  
- Input validation ensures proper format and positive numerical values.  
- Graceful error handling with clear messages.  

---

## Database Schema
The system uses the following SQLite tables:

- `users(uid, pwd, role)` 
- `customers(cid, name, email)`  
- `products(pid, name, category, price, stock_count, descr)`  
- `orders(ono, cid, sessionNo, odate, shipping_address)`  
- `orderlines(ono, lineNo, pid, qty, uprice)`  
- `sessions(cid, sessionNo, start_time, end_time)`  
- `viewedProduct(cid, sessionNo, ts, pid)`  
- `search(cid, sessionNo, ts, query)`  
- `cart(cid, sessionNo, pid, qty)`  

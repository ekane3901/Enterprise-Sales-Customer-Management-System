-- Let's drop the tables in case they exist from previous runs
drop table if exists orderlines;
drop table if exists orders;
drop table if exists cart;
drop table if exists search;
drop table if exists viewedProduct;
drop table if exists sessions;
drop table if exists products;
drop table if exists customers;
drop table if exists users;

create table users (
  uid		int,
  pwd		text,
  role		text,
  primary key (uid)
);
create table customers (
  cid		int,
  name		text, 
  email		text,
  primary key (cid),
  foreign key (cid) references users
);
create table products (
  pid		int, 
  name		text, 
  category	text, 
  price		float, 
  stock_count	int, 
  descr		text,
  primary key (pid)
);
create table sessions (
  cid		int,
  sessionNo	int, 
  start_time	datetime, 
  end_time	datetime,
  primary key (cid, sessionNo),
  foreign key (cid) references customers on delete cascade
);
create table viewedProduct (
  cid		int, 
  sessionNo	int, 
  ts		timestamp, 
  pid		int,
  primary key (cid, sessionNo, ts),
  foreign key (cid, sessionNo) references sessions,
  foreign key (pid) references products
);
create table search (
  cid		int, 
  sessionNo	int, 
  ts		timestamp, 
  query		text,
  primary key (cid, sessionNo, ts),
  foreign key (cid, sessionNo) references sessions
);
create table cart (
  cid		int, 
  sessionNo	int, 
  pid		int,
  qty		int,
  primary key (cid, sessionNo, pid),
  foreign key (cid, sessionNo) references sessions,
  foreign key (pid) references products
);
create table orders (
  ono		int, 
  cid		int,
  sessionNo	int,
  odate		date, 
  shipping_address text,
  primary key (ono),
  foreign key (cid, sessionNo) references sessions
);
create table orderlines (
  ono		int, 
  lineNo	int, 
  pid		int, 
  qty		int, 
  uprice	float, 
  primary key (ono, lineNo),
  foreign key (ono) references orders on delete cascade
);





insert into users values
(1, 'pass123', 'customer'),
(2, 'secret', 'customer'),
(3, 'qwerty', 'customer'),
(4, 'admin1', 'sales'),
(5, 'alpha', 'customer'),
(6, 'beta', 'customer'),
(7, 'gamma', 'customer'),
(8, 'delta', 'customer'),
(9, 'omega', 'customer'),
(10, 'root', 'sales');

-- CUSTOMERS (only some users are customers)
insert into customers values
(1, 'John Smith', 'john@example.com'),
(2, 'Jane Doe', 'jane@example.com'),
(3, 'Carlos Ruiz', 'carlos@example.com'),
(5, 'Anna Lee', 'anna@example.com'),
(6, 'Emily Chan', 'emily@example.com'),
(7, 'Mark Patel', 'mark@example.com'),
(8, 'Sara Kim', 'sara@example.com'),
(9, 'Leo Martin', 'leo@example.com');

-- PRODUCTS
insert into products values
(101, 'Wireless Mouse', 'Electronics', 25.99, 120, 'Ergonomic wireless mouse'),
(102, 'Mechanical Keyboard', 'Electronics', 79.99, 80, 'RGB backlit keyboard'),
(103, 'Laptop Stand', 'Accessories', 34.50, 50, 'Adjustable aluminum stand'),
(104, 'USB-C Cable', 'Electronics', 9.99, 300, '1m USB-C cable'),
(105, 'Noise-Cancelling Headphones', 'Electronics', 129.99, 40, 'Over-ear design'),
(106, 'Office Chair', 'Furniture', 199.00, 25, 'Ergonomic mesh chair'),
(107, 'Desk Lamp', 'Furniture', 49.50, 60, 'LED desk lamp with dimmer'),
(108, 'Notebook', 'Stationery', 3.50, 500, '100-page ruled notebook'),
(109, 'Pen Set', 'Stationery', 7.20, 400, 'Pack of 5 gel pens'),
(110, 'Smartphone Stand', 'Accessories', 12.99, 150, 'Universal phone stand'),
(111, 'Bluetooth Speaker', 'Electronics', 59.00, 90, 'Portable speaker'),
(112, 'Water Bottle', 'Lifestyle', 15.00, 200, 'Insulated steel bottle'),
(113, 'Backpack', 'Lifestyle', 49.99, 70, 'Laptop backpack'),
(114, 'Wireless Charger', 'Electronics', 29.99, 110, 'Fast charging pad'),
(115, 'Monitor 24in', 'Electronics', 149.00, 35, 'Full HD LED monitor'),
(116, 'Webcam', 'Electronics', 39.00, 65, '1080p webcam'),
(117, 'Mouse Pad', 'Accessories', 8.00, 220, 'Large surface mouse pad'),
(118, 'Desk Organizer', 'Accessories', 18.75, 90, 'Wooden desktop organizer'),
(119, 'Standing Desk', 'Furniture', 299.99, 15, 'Adjustable height desk'),
(120, 'Sticky Notes', 'Stationery', 4.25, 600, 'Pack of 6 colors');

-- SESSIONS (8 customers × several sessions)
insert into sessions values
(1, 1, '2025-10-01 09:00', '2025-10-01 09:45'),
(1, 2, '2025-10-05 14:00', '2025-10-05 15:00'),
(2, 1, '2025-10-03 10:00', '2025-10-03 10:30'),
(2, 2, '2025-10-10 13:00', '2025-10-10 13:40'),
(3, 1, '2025-10-02 16:00', '2025-10-02 17:00'),
(3, 2, '2025-10-07 09:30', '2025-10-07 10:00'),
(5, 1, '2025-10-01 12:00', '2025-10-01 12:20'),
(5, 2, '2025-10-12 18:00', '2025-10-12 18:40'),
(6, 1, '2025-10-08 11:00', '2025-10-08 11:50'),
(6, 2, '2025-10-15 19:00', '2025-10-15 19:45'),
(7, 1, '2025-10-04 08:00', '2025-10-04 08:35'),
(7, 2, '2025-10-09 09:15', '2025-10-09 09:50'),
(8, 1, '2025-10-03 19:00', '2025-10-03 19:30'),
(8, 2, '2025-10-11 10:10', '2025-10-11 10:50'),
(9, 1, '2025-10-02 08:30', '2025-10-02 09:00'),
(9, 2, '2025-10-14 20:00', '2025-10-14 20:45');

-- VIEWED PRODUCTS (sample of ~200, truncated for brevity)
insert into viewedProduct values
(1,1,'2025-10-01 09:05',101),
(1,1,'2025-10-01 09:10',102),
(1,2,'2025-10-05 14:05',105),
(2,1,'2025-10-03 10:05',104),
(2,2,'2025-10-10 13:10',111),
(3,1,'2025-10-02 16:05',115),
(3,2,'2025-10-07 09:35',103),
(5,1,'2025-10-01 12:05',108),
(5,2,'2025-10-12 18:10',113),
(6,1,'2025-10-08 11:05',110),
(6,2,'2025-10-15 19:10',114),
(7,1,'2025-10-04 08:10',107),
(7,2,'2025-10-09 09:20',117),
(8,1,'2025-10-03 19:05',101),
(8,2,'2025-10-11 10:15',119),
(9,1,'2025-10-02 08:35',120),
(9,2,'2025-10-14 20:10',112);

-- SEARCHES
insert into search values
(1,1,'2025-10-01 09:02','wireless mouse'),
(1,2,'2025-10-05 14:02','headphones'),
(2,1,'2025-10-03 10:02','usb cable'),
(3,1,'2025-10-02 16:02','laptop stand'),
(5,2,'2025-10-12 18:02','backpack'),
(6,2,'2025-10-15 19:02','charger'),
(7,1,'2025-10-04 08:02','desk lamp'),
(8,2,'2025-10-11 10:12','standing desk');

-- CARTS
insert into cart values
(1,1,101,1),
(1,2,105,1),
(2,1,104,2),
(3,1,115,1),
(5,2,113,1),
(6,2,114,1),
(7,1,107,1),
(8,2,119,1),
(9,1,120,3);

-- ORDERS
insert into orders values
(5001,1,2,'2025-10-05','123 Main St, Toronto'),
(5002,2,1,'2025-10-03','98 King St, Ottawa'),
(5003,3,1,'2025-10-02','12 Bay Rd, Montreal'),
(5004,5,2,'2025-10-12','22 Pine St, Vancouver'),
(5005,6,2,'2025-10-15','44 River Ave, Calgary'),
(5006,7,1,'2025-10-04','89 Elm St, Edmonton'),
(5007,8,2,'2025-10-11','77 Queen St, Toronto');

-- ORDERLINES
insert into orderlines values
(5001,1,105,1,129.99),
(5002,1,104,2,9.99),
(5003,1,115,1,149.00),
(5004,1,113,1,49.99),
(5005,1,114,1,29.99),
(5006,1,107,1,49.50),
(5007,1,119,1,299.99);
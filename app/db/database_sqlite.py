import sqlite3

database_path = './database.db'

try:
    with sqlite3.connect(database_path) as db:
        cursor = db.cursor()
        queries = [
            """CREATE TABLE IF NOT EXISTS categories (
                   id INTEGER PRIMARY KEY,
                   name TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS style (
                    id INTEGER PRIMARY KEY,
                    name TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS sets (
                   id INTEGER PRIMARY KEY,
                   name TEXT NOT NULL,
                   discount INTEGER NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role_id INTEGER NOT NULL,
                    FOREIGN KEY (role_id) REFERENCES roles(id),
                    CONSTRAINT valid_role CHECK (role_id IN (1, 2))
            )""",
            """CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category_id INTEGER,
                    style_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories(id),
                    FOREIGN KEY (style_id) REFERENCES style(id)
            )""",
            """CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    total_price REAL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
            )""",
            """CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
            )""",
            """CREATE TABLE IF NOT EXISTS set_items (
                    id INTEGER PRIMARY KEY,
                    set_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (set_id) REFERENCES sets(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
            )""",
            """CREATE TABLE IF NOT EXISTS roles (
                   id INTEGER PRIMARY KEY,
                   name TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS set_order (
                    id INTEGER PRIMARY KEY,
                    set_id INTEGER NOT NULL,
                    order_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (set_id) REFERENCES sets(id),
                    FOREIGN KEY (order_id) REFERENCES orders(id)
            )"""
        ]
        for q in queries:
            cursor.execute(q)

        db.commit()
except sqlite3.Error as e:
    print("Ошибка при работе с базой данных:", e)

import sqlite3
import os

DB_NAME = "store.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def setup():
    conn = get_connection()
    cursor = conn.cursor()

    # Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        purchase_price REAL,
        sale_price REAL,
        quantity REAL,
        min_stock REAL,
        unit TEXT
    )
    ''')

    # Clients Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        balance REAL DEFAULT 0
    )
    ''')

    # Suppliers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        balance REAL DEFAULT 0
    )
    ''')

    # Sales Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        date TEXT,
        total REAL,
        discount REAL,
        paid REAL,
        remaining REAL,
        FOREIGN KEY (client_id) REFERENCES clients (id)
    )
    ''')

    # Sale Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        product_id INTEGER,
        quantity REAL,
        price REAL,
        total REAL,
        FOREIGN KEY (sale_id) REFERENCES sales (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # Purchases Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER,
        date TEXT,
        total REAL,
        paid REAL,
        remaining REAL,
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
    )
    ''')

    # Purchase Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchase_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        purchase_id INTEGER,
        product_id INTEGER,
        quantity REAL,
        price REAL,
        total REAL,
        FOREIGN KEY (purchase_id) REFERENCES purchases (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # Expenses Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        amount REAL,
        date TEXT,
        category TEXT
    )
    ''')

    # General Transactions Table (for accounting/cashbox)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, -- 'income' or 'expense'
        amount REAL,
        date TEXT,
        description TEXT,
        reference_type TEXT, -- e.g., 'sale', 'purchase', 'expense', 'client_payment', 'supplier_payment'
        reference_id INTEGER
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup()
    print("Database setup complete.")

# --- Products CRUD ---
def add_product(name, category, purchase_price, sale_price, quantity, min_stock, unit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, category, purchase_price, sale_price, quantity, min_stock, unit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, category, purchase_price, sale_price, quantity, min_stock, unit))
    conn.commit()
    conn.close()

def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_product(product_id, name, category, purchase_price, sale_price, quantity, min_stock, unit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE products
        SET name=?, category=?, purchase_price=?, sale_price=?, quantity=?, min_stock=?, unit=?
        WHERE id=?
    ''', (name, category, purchase_price, sale_price, quantity, min_stock, unit, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

# --- Sales CRUD ---
def add_sale(client_id, date, total, discount, paid, remaining, items):
    """
    items should be a list of dicts: [{'product_id': id, 'quantity': q, 'price': p, 'total': t}, ...]
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO sales (client_id, date, total, discount, paid, remaining)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (client_id, date, total, discount, paid, remaining))
        sale_id = cursor.lastrowid

        for item in items:
            cursor.execute('''
                INSERT INTO sale_items (sale_id, product_id, quantity, price, total)
                VALUES (?, ?, ?, ?, ?)
            ''', (sale_id, item['product_id'], item['quantity'], item['price'], item['total']))

            # Update product quantity
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (item['quantity'], item['product_id']))

        # Update client balance if remaining > 0
        if client_id and remaining > 0:
            cursor.execute("UPDATE clients SET balance = balance + ? WHERE id = ?", (remaining, client_id))

        # Record transaction
        if paid > 0:
            cursor.execute('''
                INSERT INTO transactions (type, amount, date, description, reference_type, reference_id)
                VALUES ('income', ?, ?, 'Sale payment', 'sale', ?)
            ''', (paid, date, sale_id))

        conn.commit()
        return sale_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_sales():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, c.name as client_name
        FROM sales s
        LEFT JOIN clients c ON s.client_id = c.id
        ORDER BY s.date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_sale_items(sale_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT si.*, p.name as product_name
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        WHERE si.sale_id = ?
    ''', (sale_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- Purchases CRUD ---
def add_purchase(supplier_id, date, total, paid, remaining, items):
    """
    items should be a list of dicts: [{'product_id': id, 'quantity': q, 'price': p, 'total': t}, ...]
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO purchases (supplier_id, date, total, paid, remaining)
            VALUES (?, ?, ?, ?, ?)
        ''', (supplier_id, date, total, paid, remaining))
        purchase_id = cursor.lastrowid

        for item in items:
            cursor.execute('''
                INSERT INTO purchase_items (purchase_id, product_id, quantity, price, total)
                VALUES (?, ?, ?, ?, ?)
            ''', (purchase_id, item['product_id'], item['quantity'], item['price'], item['total']))

            # Update product quantity and possibly purchase price
            cursor.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (item['quantity'], item['product_id']))

        # Update supplier balance if remaining > 0
        if supplier_id and remaining > 0:
            cursor.execute("UPDATE suppliers SET balance = balance + ? WHERE id = ?", (remaining, supplier_id))

        # Record transaction
        if paid > 0:
            cursor.execute('''
                INSERT INTO transactions (type, amount, date, description, reference_type, reference_id)
                VALUES ('expense', ?, ?, 'Purchase payment', 'purchase', ?)
            ''', (paid, date, purchase_id))

        conn.commit()
        return purchase_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_purchases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, s.name as supplier_name
        FROM purchases p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        ORDER BY p.date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- Clients CRUD ---
def add_client(name, phone, balance=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (name, phone, balance) VALUES (?, ?, ?)", (name, phone, balance))
    conn.commit()
    conn.close()

def get_clients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- Suppliers CRUD ---
def add_supplier(name, phone, balance=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO suppliers (name, phone, balance) VALUES (?, ?, ?)", (name, phone, balance))
    conn.commit()
    conn.close()

def get_suppliers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- Expenses CRUD ---
def add_expense(description, amount, date, category):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO expenses (description, amount, date, category) VALUES (?, ?, ?, ?)", (description, amount, date, category))
        expense_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO transactions (type, amount, date, description, reference_type, reference_id)
            VALUES ('expense', ?, ?, 'Expense', 'expense', ?)
        ''', (amount, date, expense_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_expenses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- Dashboard Stats ---
def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()
    import datetime
    today = datetime.date.today().isoformat()

    stats = {}

    # Total sales today
    cursor.execute("SELECT SUM(total) FROM sales WHERE date=?", (today,))
    stats['sales_today'] = cursor.fetchone()[0] or 0

    # Total purchases today
    cursor.execute("SELECT SUM(total) FROM purchases WHERE date=?", (today,))
    stats['purchases_today'] = cursor.fetchone()[0] or 0

    # Expenses today
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date=?", (today,))
    stats['expenses_today'] = cursor.fetchone()[0] or 0

    # Total items
    cursor.execute("SELECT COUNT(id) FROM products")
    stats['total_products'] = cursor.fetchone()[0] or 0

    # Total client dues
    cursor.execute("SELECT SUM(balance) FROM clients")
    stats['client_dues'] = cursor.fetchone()[0] or 0

    # Total supplier dues
    cursor.execute("SELECT SUM(balance) FROM suppliers")
    stats['supplier_dues'] = cursor.fetchone()[0] or 0

    # Simple profit calculation for today: total sales income - total purchase cost of items sold today
    # (Actually true profit calculation requires tracking average cost price. For now, simple diff of total sales - purchases/expenses might suffice or cost of goods sold).
    cursor.execute('''
        SELECT SUM((si.price - p.purchase_price) * si.quantity)
        FROM sale_items si
        JOIN sales s ON si.sale_id = s.id
        JOIN products p ON si.product_id = p.id
        WHERE s.date = ?
    ''', (today,))
    stats['profit_today'] = cursor.fetchone()[0] or 0

    conn.close()
    return stats

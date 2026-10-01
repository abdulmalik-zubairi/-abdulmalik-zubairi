import os
import db
import datetime

# Use a test DB
db.DB_NAME = "test_store.db"

def test_db():
    if os.path.exists(db.DB_NAME):
        os.remove(db.DB_NAME)

    db.setup()

    # Products
    db.add_product("Cement", "مواد بناء", 15.0, 20.0, 100, 10, "كيس")
    products = db.get_products()
    assert len(products) == 1
    p_id = products[0][0]
    assert products[0][1] == "Cement"

    # Clients and Suppliers
    db.add_client("Ahmed", "123", 0)
    db.add_supplier("Supplier1", "456", 0)

    clients = db.get_clients()
    suppliers = db.get_suppliers()
    c_id = clients[0][0]
    s_id = suppliers[0][0]

    # Sales
    today = datetime.date.today().isoformat()
    db.add_sale(c_id, today, 20.0, 0, 10.0, 10.0, [{'product_id': p_id, 'quantity': 1, 'price': 20.0, 'total': 20.0}])

    sales = db.get_sales()
    assert len(sales) == 1

    # Check client balance updated
    clients_after = db.get_clients()
    assert clients_after[0][3] == 10.0

    # Check stock updated
    products_after = db.get_products()
    assert products_after[0][5] == 99.0

    # Expenses
    db.add_expense("Rent", 500, today, "الإيجار")

    stats = db.get_dashboard_stats()
    assert stats['sales_today'] == 20.0
    assert stats['expenses_today'] == 500.0
    assert stats['total_products'] == 1

    print("All tests passed.")

if __name__ == '__main__':
    test_db()

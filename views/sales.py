import flet as ft
import db
import datetime

def SalesView(page):

    # Client Selection
    clients = db.get_clients()
    client_dropdown = ft.Dropdown(
        label="اختر العميل",
        options=[ft.dropdown.Option(key=str(c[0]), text=c[1]) for c in clients] + [ft.dropdown.Option(key="", text="عميل نقدي")],
        width=300
    )

    # Product Selection
    products = db.get_products()
    product_dropdown = ft.Dropdown(
        label="اختر الصنف",
        options=[ft.dropdown.Option(key=str(p[0]), text=p[1]) for p in products],
        width=300
    )
    qty_field = ft.TextField(label="الكمية", value="1", width=100)

    selected_items = [] # list of dicts: {'product_id', 'name', 'quantity', 'price', 'total'}

    items_list = ft.ListView(expand=True, spacing=10)
    total_text = ft.Text("الإجمالي: 0", size=20, weight=ft.FontWeight.BOLD)
    discount_field = ft.TextField(label="الخصم", value="0", width=100)
    paid_field = ft.TextField(label="المدفوع", value="0", width=100)

    def update_totals():
        total = sum(item['total'] for item in selected_items)
        try:
            discount = float(discount_field.value or 0)
        except:
            discount = 0
        final_total = total - discount
        total_text.value = f"الإجمالي بعد الخصم: {final_total}"
        paid_field.value = str(final_total) # default fully paid
        page.update()

    def add_item_to_list(e):
        if not product_dropdown.value: return
        p_id = int(product_dropdown.value)
        qty = float(qty_field.value)

        # Get price from db
        product = db.get_product(p_id)
        price = product[4] # sale_price
        name = product[1]

        item_total = price * qty
        selected_items.append({
            'product_id': p_id,
            'name': name,
            'quantity': qty,
            'price': price,
            'total': item_total
        })

        refresh_items_list()

    def remove_item(index):
        selected_items.pop(index)
        refresh_items_list()

    def refresh_items_list():
        items_list.controls.clear()
        for i, item in enumerate(selected_items):
            items_list.controls.append(
                ft.Row([
                    ft.Text(item['name'], width=200),
                    ft.Text(f"الكمية: {item['quantity']}", width=100),
                    ft.Text(f"السعر: {item['price']}", width=100),
                    ft.Text(f"المجموع: {item['total']}", width=100),
                    ft.IconButton(ft.icons.DELETE, on_click=lambda e, idx=i: remove_item(idx))
                ])
            )
        update_totals()
        page.update()

    def save_sale(e):
        if not selected_items:
            # show error
            return

        client_id = int(client_dropdown.value) if client_dropdown.value else None
        date = datetime.date.today().isoformat()
        total = sum(item['total'] for item in selected_items)
        try:
            discount = float(discount_field.value or 0)
            paid = float(paid_field.value or 0)
        except:
            discount = 0
            paid = 0

        final_total = total - discount
        remaining = final_total - paid

        try:
            db.add_sale(client_id, date, total, discount, paid, remaining, selected_items)
            # clear form
            selected_items.clear()
            discount_field.value = "0"
            paid_field.value = "0"
            refresh_items_list()
            # Show success message
            page.snack_bar = ft.SnackBar(ft.Text("تم حفظ الفاتورة بنجاح"))
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            print("Error saving sale:", ex)
            page.snack_bar = ft.SnackBar(ft.Text("حدث خطأ أثناء الحفظ"))
            page.snack_bar.open = True
            page.update()

    discount_field.on_change = lambda e: update_totals()

    return ft.Column([
        ft.Text("فاتورة مبيعات جديدة", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([client_dropdown]),
        ft.Row([product_dropdown, qty_field, ft.ElevatedButton("إضافة", on_click=add_item_to_list)]),
        ft.Divider(),
        items_list,
        ft.Divider(),
        ft.Row([
            total_text,
            discount_field,
            paid_field,
            ft.ElevatedButton("حفظ الفاتورة", on_click=save_sale, bgcolor=ft.colors.GREEN, color=ft.colors.WHITE)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ], expand=True)

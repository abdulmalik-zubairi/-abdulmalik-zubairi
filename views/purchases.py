import flet as ft
import db
import datetime

def PurchasesView(page):

    # Supplier Selection
    suppliers = db.get_suppliers()
    supplier_dropdown = ft.Dropdown(
        label="اختر المورد",
        options=[ft.dropdown.Option(key=str(s[0]), text=s[1]) for s in suppliers],
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
    price_field = ft.TextField(label="سعر الشراء للوحدة", value="0", width=150)

    selected_items = []

    items_list = ft.ListView(expand=True, spacing=10)
    total_text = ft.Text("الإجمالي: 0", size=20, weight=ft.FontWeight.BOLD)
    paid_field = ft.TextField(label="المدفوع", value="0", width=100)

    def update_totals():
        total = sum(item['total'] for item in selected_items)
        total_text.value = f"الإجمالي: {total}"
        paid_field.value = str(total)
        page.update()

    def add_item_to_list(e):
        if not product_dropdown.value: return
        p_id = int(product_dropdown.value)
        qty = float(qty_field.value)

        try:
            price = float(price_field.value)
        except:
            price = 0

        product = db.get_product(p_id)
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

    def save_purchase(e):
        if not selected_items or not supplier_dropdown.value:
            # show error
            return

        supplier_id = int(supplier_dropdown.value)
        date = datetime.date.today().isoformat()
        total = sum(item['total'] for item in selected_items)
        try:
            paid = float(paid_field.value or 0)
        except:
            paid = 0

        remaining = total - paid

        try:
            db.add_purchase(supplier_id, date, total, paid, remaining, selected_items)
            selected_items.clear()
            paid_field.value = "0"
            refresh_items_list()
            page.snack_bar = ft.SnackBar(ft.Text("تم حفظ فاتورة المشتريات بنجاح"))
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            print("Error saving purchase:", ex)
            page.snack_bar = ft.SnackBar(ft.Text("حدث خطأ أثناء الحفظ"))
            page.snack_bar.open = True
            page.update()

    def on_product_change(e):
        if product_dropdown.value:
            p = db.get_product(int(product_dropdown.value))
            if p:
                price_field.value = str(p[3]) # purchase_price
                page.update()

    product_dropdown.on_change = on_product_change

    return ft.Column([
        ft.Text("فاتورة مشتريات جديدة", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([supplier_dropdown]),
        ft.Row([product_dropdown, price_field, qty_field, ft.ElevatedButton("إضافة", on_click=add_item_to_list)]),
        ft.Divider(),
        items_list,
        ft.Divider(),
        ft.Row([
            total_text,
            paid_field,
            ft.ElevatedButton("حفظ الفاتورة", on_click=save_purchase, bgcolor=ft.colors.GREEN, color=ft.colors.WHITE)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ], expand=True)

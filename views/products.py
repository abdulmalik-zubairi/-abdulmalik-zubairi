import flet as ft
import db

def ProductsView(page):

    products_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("الرقم")),
            ft.DataColumn(ft.Text("الاسم")),
            ft.DataColumn(ft.Text("التصنيف")),
            ft.DataColumn(ft.Text("سعر الشراء")),
            ft.DataColumn(ft.Text("سعر البيع")),
            ft.DataColumn(ft.Text("الكمية")),
            ft.DataColumn(ft.Text("الوحدة")),
            ft.DataColumn(ft.Text("الإجراءات")),
        ],
        rows=[]
    )

    def load_data():
        products = db.get_products()
        products_table.rows.clear()
        for p in products:
            p_id, name, cat, p_price, s_price, qty, min_stock, unit = p
            products_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p_id))),
                        ft.DataCell(ft.Text(name)),
                        ft.DataCell(ft.Text(cat)),
                        ft.DataCell(ft.Text(str(p_price))),
                        ft.DataCell(ft.Text(str(s_price))),
                        ft.DataCell(ft.Text(str(qty))),
                        ft.DataCell(ft.Text(unit)),
                        ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, id=p_id: delete_product(id))),
                    ]
                )
            )
        page.update()

    def delete_product(id):
        db.delete_product(id)
        load_data()

    def open_add_dialog(e):
        name_field = ft.TextField(label="اسم الصنف")
        cat_dropdown = ft.Dropdown(
            label="التصنيف",
            options=[
                ft.dropdown.Option("مواد بناء"),
                ft.dropdown.Option("مواد كهربائية"),
                ft.dropdown.Option("سيراميك وبورسلان"),
                ft.dropdown.Option("سباكة"),
                ft.dropdown.Option("أدوات ومستلزمات"),
            ]
        )
        p_price_field = ft.TextField(label="سعر الشراء", value="0")
        s_price_field = ft.TextField(label="سعر البيع", value="0")
        qty_field = ft.TextField(label="الكمية", value="0")
        min_stock_field = ft.TextField(label="الحد الأدنى", value="0")
        unit_field = ft.TextField(label="الوحدة (حبة، كرتون...)")

        def save_product(e):
            db.add_product(
                name_field.value,
                cat_dropdown.value or "",
                float(p_price_field.value),
                float(s_price_field.value),
                float(qty_field.value),
                float(min_stock_field.value),
                unit_field.value
            )
            dialog.open = False
            load_data()

        dialog = ft.AlertDialog(
            title=ft.Text("إضافة صنف جديد"),
            content=ft.Column([
                name_field, cat_dropdown, p_price_field, s_price_field, qty_field, min_stock_field, unit_field
            ], tight=True),
            actions=[
                ft.TextButton("حفظ", on_click=save_product),
                ft.TextButton("إلغاء", on_click=lambda e: setattr(dialog, 'open', False) or page.update())
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    load_data()

    return ft.Column([
        ft.Row([
            ft.Text("إدارة الأصناف والمنتجات", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("إضافة صنف", icon=ft.icons.ADD, on_click=open_add_dialog)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        products_table
    ], expand=True)

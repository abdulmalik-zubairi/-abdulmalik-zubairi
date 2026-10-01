import flet as ft
import db

def InventoryView(page):

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("الرقم")),
            ft.DataColumn(ft.Text("الصنف")),
            ft.DataColumn(ft.Text("الكمية الحالية")),
            ft.DataColumn(ft.Text("الحد الأدنى")),
            ft.DataColumn(ft.Text("الحالة")),
        ],
        rows=[]
    )

    def load_data():
        products = db.get_products()
        table.rows.clear()
        for p in products:
            p_id, name, cat, p_price, s_price, qty, min_stock, unit = p
            status = "متوفر"
            color = ft.colors.BLACK
            if qty <= 0:
                status = "نفذت الكمية"
                color = ft.colors.RED
            elif qty <= min_stock:
                status = "وصل للحد الأدنى"
                color = ft.colors.ORANGE

            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p_id))),
                        ft.DataCell(ft.Text(name)),
                        ft.DataCell(ft.Text(str(qty))),
                        ft.DataCell(ft.Text(str(min_stock))),
                        ft.DataCell(ft.Text(status, color=color, weight=ft.FontWeight.BOLD)),
                    ]
                )
            )
        page.update()

    load_data()

    return ft.Column([
        ft.Text("حالة المخزون", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        table
    ], expand=True)

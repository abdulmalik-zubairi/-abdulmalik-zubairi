import flet as ft
import db

def PartiesView(page, party_type):
    # party_type can be 'clients' or 'suppliers'

    title_text = "إدارة العملاء" if party_type == 'clients' else "إدارة الموردين"

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("الرقم")),
            ft.DataColumn(ft.Text("الاسم")),
            ft.DataColumn(ft.Text("الهاتف")),
            ft.DataColumn(ft.Text("الرصيد / المستحق")),
        ],
        rows=[]
    )

    def load_data():
        table.rows.clear()
        if party_type == 'clients':
            data = db.get_clients()
        else:
            data = db.get_suppliers()

        for row in data:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(ft.Text(row[2])),
                        ft.DataCell(ft.Text(str(row[3]))),
                    ]
                )
            )
        page.update()

    def open_add_dialog(e):
        name_field = ft.TextField(label="الاسم")
        phone_field = ft.TextField(label="الهاتف")
        balance_field = ft.TextField(label="الرصيد الافتتاحي (ديون)", value="0")

        def save_party(e):
            try:
                bal = float(balance_field.value)
            except:
                bal = 0

            if party_type == 'clients':
                db.add_client(name_field.value, phone_field.value, bal)
            else:
                db.add_supplier(name_field.value, phone_field.value, bal)

            dialog.open = False
            load_data()

        dialog = ft.AlertDialog(
            title=ft.Text(f"إضافة {('عميل' if party_type == 'clients' else 'مورد')} جديد"),
            content=ft.Column([
                name_field, phone_field, balance_field
            ], tight=True),
            actions=[
                ft.TextButton("حفظ", on_click=save_party),
                ft.TextButton("إلغاء", on_click=lambda e: setattr(dialog, 'open', False) or page.update())
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    load_data()

    return ft.Column([
        ft.Row([
            ft.Text(title_text, size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("إضافة جديد", icon=ft.icons.ADD, on_click=open_add_dialog)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        table
    ], expand=True)

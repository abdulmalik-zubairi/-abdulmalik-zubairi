import flet as ft
import db
import datetime

def ExpensesView(page):

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("التاريخ")),
            ft.DataColumn(ft.Text("البيان")),
            ft.DataColumn(ft.Text("التصنيف")),
            ft.DataColumn(ft.Text("المبلغ")),
        ],
        rows=[]
    )

    def load_data():
        expenses = db.get_expenses()
        table.rows.clear()
        for exp in expenses:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(exp[3])), # date
                        ft.DataCell(ft.Text(exp[1])), # description
                        ft.DataCell(ft.Text(exp[4])), # category
                        ft.DataCell(ft.Text(str(exp[2]))), # amount
                    ]
                )
            )
        page.update()

    def open_add_dialog(e):
        desc_field = ft.TextField(label="البيان (الوصف)")
        amount_field = ft.TextField(label="المبلغ", value="0")
        cat_dropdown = ft.Dropdown(
            label="التصنيف",
            options=[
                ft.dropdown.Option("الإيجار"),
                ft.dropdown.Option("الكهرباء"),
                ft.dropdown.Option("النقل"),
                ft.dropdown.Option("الرواتب"),
                ft.dropdown.Option("الصيانة"),
                ft.dropdown.Option("مصروفات أخرى"),
            ]
        )

        def save_expense(e):
            try:
                amt = float(amount_field.value)
            except:
                amt = 0
            date = datetime.date.today().isoformat()
            db.add_expense(desc_field.value, amt, date, cat_dropdown.value or "مصروفات أخرى")
            dialog.open = False
            load_data()

        dialog = ft.AlertDialog(
            title=ft.Text("تسجيل مصروف جديد"),
            content=ft.Column([
                desc_field, amount_field, cat_dropdown
            ], tight=True),
            actions=[
                ft.TextButton("حفظ", on_click=save_expense),
                ft.TextButton("إلغاء", on_click=lambda e: setattr(dialog, 'open', False) or page.update())
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    load_data()

    return ft.Column([
        ft.Row([
            ft.Text("المصروفات", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("تسجيل مصروف", icon=ft.icons.ADD, on_click=open_add_dialog)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        table
    ], expand=True)

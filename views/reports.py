import flet as ft
import db

def ReportsView(page):
    return ft.Column([
        ft.Text("التقارير", size=30, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Text("سيتم إضافة التقارير التفصيلية هنا مستقبلاً (مثل كشوفات الحسابات وحركة الأصناف).", size=18)
    ], expand=True)

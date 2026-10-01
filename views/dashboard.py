import flet as ft
import db

def DashboardView(page):
    stats = db.get_dashboard_stats()

    def create_card(title, value, icon_name, color):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon_name, size=40, color=color),
                    ft.Text(title, size=16, weight=ft.FontWeight.W_500),
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=200,
                height=150,
                padding=10,
            )
        )

    cards = ft.Row([
        create_card("مبيعات اليوم", stats['sales_today'], ft.icons.ATTACH_MONEY, ft.colors.BLUE),
        create_card("مشتريات اليوم", stats['purchases_today'], ft.icons.SHOPPING_BAG, ft.colors.ORANGE),
        create_card("المصروفات", stats['expenses_today'], ft.icons.MONEY_OFF, ft.colors.RED),
        create_card("الأرباح التقديرية", stats['profit_today'], ft.icons.TRENDING_UP, ft.colors.GREEN),
    ], wrap=True, alignment=ft.MainAxisAlignment.CENTER)

    cards2 = ft.Row([
        create_card("عدد الأصناف", stats['total_products'], ft.icons.INVENTORY_2, ft.colors.TEAL),
        create_card("مستحقات على العملاء", stats['client_dues'], ft.icons.PEOPLE, ft.colors.INDIGO),
        create_card("مستحقات للموردين", stats['supplier_dues'], ft.icons.LOCAL_SHIPPING, ft.colors.BROWN),
    ], wrap=True, alignment=ft.MainAxisAlignment.CENTER)

    return ft.Column([
        ft.Text("لوحة التحكم", size=30, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        cards,
        ft.Container(height=20),
        cards2
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

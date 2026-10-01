import flet as ft
import db
from views.products import ProductsView
from views.sales import SalesView
from views.purchases import PurchasesView
from views.parties import PartiesView
from views.inventory import InventoryView
from views.expenses import ExpensesView
from views.dashboard import DashboardView
from views.reports import ReportsView

def main(page: ft.Page):
    page.title = "نظام إدارة محل مواد البناء"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.rtl = True
    page.window.width = 1200
    page.window.height = 800

    db.setup()

    def change_view(index, content_container):
        if index == 0:
            content_container.content = DashboardView(page)
        elif index == 1:
            content_container.content = ProductsView(page)
        elif index == 2:
            content_container.content = SalesView(page)
        elif index == 3:
            content_container.content = PurchasesView(page)
        elif index == 4:
            content_container.content = PartiesView(page, 'clients')
        elif index == 5:
            content_container.content = PartiesView(page, 'suppliers')
        elif index == 6:
            content_container.content = InventoryView(page)
        elif index == 7:
            content_container.content = ExpensesView(page)
        elif index == 8:
            content_container.content = ft.Text("الصندوق والحسابات سيتم برمجتها لاحقاً", size=20)
        elif index == 9:
            content_container.content = ReportsView(page)
        else:
            content_container.content = ft.Text("قريباً", size=20)

        content_container.update()

    def route_change(e):
        page.views.clear()

        main_content = ft.Container(expand=True, padding=20)

        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            extended=True,
            destinations=[
                ft.NavigationRailDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD, label="لوحة التحكم"),
                ft.NavigationRailDestination(icon=ft.icons.INVENTORY_2_OUTLINED, selected_icon=ft.icons.INVENTORY_2, label="الأصناف والمنتجات"),
                ft.NavigationRailDestination(icon=ft.icons.SHOPPING_CART_OUTLINED, selected_icon=ft.icons.SHOPPING_CART, label="المبيعات"),
                ft.NavigationRailDestination(icon=ft.icons.SHOPPING_BAG_OUTLINED, selected_icon=ft.icons.SHOPPING_BAG, label="المشتريات"),
                ft.NavigationRailDestination(icon=ft.icons.PEOPLE_OUTLINED, selected_icon=ft.icons.PEOPLE, label="العملاء"),
                ft.NavigationRailDestination(icon=ft.icons.LOCAL_SHIPPING_OUTLINED, selected_icon=ft.icons.LOCAL_SHIPPING, label="الموردون"),
                ft.NavigationRailDestination(icon=ft.icons.WAREHOUSE_OUTLINED, selected_icon=ft.icons.WAREHOUSE, label="المخزون"),
                ft.NavigationRailDestination(icon=ft.icons.MONEY_OFF_OUTLINED, selected_icon=ft.icons.MONEY_OFF, label="المصروفات"),
                ft.NavigationRailDestination(icon=ft.icons.ACCOUNT_BALANCE_OUTLINED, selected_icon=ft.icons.ACCOUNT_BALANCE, label="الصندوق والحسابات"),
                ft.NavigationRailDestination(icon=ft.icons.BAR_CHART_OUTLINED, selected_icon=ft.icons.BAR_CHART, label="التقارير"),
                ft.NavigationRailDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label="الإعدادات"),
            ],
            on_change=lambda e: change_view(e.control.selected_index, main_content)
        )

        page.views.append(
            ft.View(
                "/",
                [
                    ft.Row(
                        [
                            rail,
                            ft.VerticalDivider(width=1),
                            main_content
                        ],
                        expand=True,
                    )
                ],
            )
        )

        change_view(rail.selected_index, main_content)
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

if __name__ == "__main__":
    ft.run(main)

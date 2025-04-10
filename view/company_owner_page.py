from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QSplitter,
    QVBoxLayout,
    QStackedWidget,
)

from models.company_owner import CompanyOwner
from models.constant import OrderStatus, PaymentStatus
from utils.helpers import load_stylesheet_from_resource
from utils.patterns.singletone import SingletonMixin
from view.base_view import BaseView
from view.widgets.table_widget import TableWidget, DelegatesType
from view.widgets.text_edit_widget import TextEditWidget
from pyqtspinner import WaitingSpinner


class CompanyOwnerWindow(BaseView, SingletonMixin):

    def __init__(self, widget: QWidget, controller):
        self.table_widget = None
        self.widget = widget
        self.controller = controller
        self.initUi()

    def initUi(self):
        self.setup_table_widget()

    def get_column_headers(self, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return [
                "id",
                "تاريخ السداد",
                "تاريخ الطلب",
                "حالة السداد",
                "اجمالي الربح من الطلب",
                "اجمالي الخصم",
                "كوبون الخصم",
                "وسيلة الدفع",
                "اجمالي الطلب",
                "المسترجع",
                "شركة الشحن",
                "مجموع السلة",
                "تكلفة",
                "حالة الطلب",
                "رقم الطلب",
                "اسم المتجر",
            ]
        else:
            return [
                "payment_date",
                "order_date",
                "payment_status",
                "total_profit",
                "total_discount",
                "coupon_code",
                "payment_method",
                "total_demand",
                "retrieved_order",
                "shipping_company",
                "salla_total",
                "cost",
                "order_status",
                "order_number",
                "store_name",
            ]

    def update_table_data(self):
        return CompanyOwner.get_all(callback=self.update_items)

    def update_items(self, result=None, error=None):
        print(len(result))
        if error:
            raise Exception("Error in Employee get_all function..")
        if len(result) >= 0:
            self.switch_window("table")
        rows = self.create_table_item_widgets(result)
        self.table_widget.setRowItems(rows)
        self.table_widget.add_rows()
        self.table_widget.update()

    def _create_waiting_spinner(self):
        self.spinner_widget = QWidget()
        # self.spinner_widget.setStyleSheet("background-color : red")
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.spinner_widget)
        self.spinner = WaitingSpinner(
            self.spinner_widget,
            color=QColor(105, 15, 117),
            disable_parent_when_spinning=False,
        )
        self.spinner.start()

        # self.widget.setLayout(self.vbox)

    def _setup_stack_widget(self):
        self.stack_widget = QStackedWidget()
        self.stack_widget.addWidget(self.table_widget)
        self.stack_widget.addWidget(self.spinner_widget)
        self.switch_window("loading")

    def switch_window(self, window="loading"):
        if not self.stack_widget or not self.spinner_widget:
            raise Exception("Init Window widgets error")

        if window == "loading":
            self.stack_widget.setCurrentWidget(self.spinner_widget)
        elif window == "table":
            self.stack_widget.setCurrentWidget(self.table_widget)

    def create_table_item_widgets(self, rows):
        items = []
        for row in rows:
            row: CompanyOwner
            coupon_code = str(row.coupons.code) if row.coupons is not None else ""
            coupon_discount = row.coupons.discount if row.coupons is not None else 0
            shipping_name = str(row.shippings.name) if row.shippings is not None else ""
            shipping_percentage = (
                row.shippings.percentage if row.shippings is not None else 0
            )
            payment_name = str(row.payments.name) if row.payments is not None else ""
            payment_percentage = (
                row.payments.percentage if row.payments is not None else 0
            )
            item: List[QTableWidgetItem] = [
                self.create_table_item_widget(str(row.id), row.id),
                self.create_table_item_widget(str(row.payment_date), row.payment_date),
                self.create_table_item_widget(str(row.order_date), row.order_date),
                self.create_table_item_widget(
                    PaymentStatus.get_str(row.payment_status), row.payment_status
                ),
                self.create_table_item_widget(str(row.total_profit), row.total_profit),
                self.create_table_item_widget(
                    str(row.total_discount), row.total_discount
                ),
                self.create_table_item_widget(
                    str(row.retrieved_order), row.retrieved_order
                ),
                self.create_table_item_widget(coupon_code, coupon_discount),
                self.create_table_item_widget(payment_name, payment_percentage),
                self.create_table_item_widget(str(row.total_demand), row.total_demand),
                self.create_table_item_widget(shipping_name, shipping_percentage),
                self.create_table_item_widget(str(row.salla_total), row.salla_total),
                self.create_table_item_widget(str(row.cost), row.cost),
                self.create_table_item_widget(
                    OrderStatus.get_str(row.order_status), row.order_status
                ),
                self.create_table_item_widget(str(row.order_number), row.order_number),
                self.create_table_item_widget(str(row.store_name), row.store_name),
            ]
            items.append(item)
        else:
            print("there's no item")
        return items

    def create_table_item_widget(self, for_display, for_edit):
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, for_display)
        item.setData(Qt.UserRole, for_edit)
        return item

    def setup_table_widget(self):
        columns = self.get_column_headers()
        self.table_widget = TableWidget(
            columns=columns, controller=self.controller, parent=self
        )
        self.table_widget.setReadOnlyColumns([0, 4, 5, 8, 9])
        self.table_widget.add_delegate(1, DelegatesType.DATE_EDITOR)
        self.table_widget.add_delegate(2, DelegatesType.DATE_EDITOR)
        self.table_widget.add_delegate(3, DelegatesType.COMBOBOXPAYMENT)
        self.table_widget.add_delegate(4, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(5, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(6, DelegatesType.COMBOBOXWITHADD)
        self.table_widget.add_delegate(7, DelegatesType.COMBOBOXWITHADD)
        self.table_widget.add_delegate(8, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(9, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(10, DelegatesType.COMBOBOXWITHADD)
        self.table_widget.add_delegate(11, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(12, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(13, DelegatesType.COMBOBOXORDER)
        self.table_widget.add_delegate(14, DelegatesType.StringDelegate)
        self.table_widget.add_delegate(15, DelegatesType.StringDelegate)
        self.table_widget.itemChanged.connect(self.controller.on_item_changed)
        self._create_waiting_spinner()
        self._setup_stack_widget()
        self.hbox: QHBoxLayout = QHBoxLayout()
        self.splitter: QSplitter = QSplitter(Qt.Horizontal)
        self.textEdit = TextEditWidget(self)
        self.splitter.addWidget(self.textEdit)
        self.splitter.addWidget(self.stack_widget)

        self.splitter.setSizes([300, 300])
        self.splitter.setStretchFactor(1, 1)
        self.hbox.addWidget(self.splitter)
        self.widget.setLayout(self.hbox)
        self.update_table_data()

import os
from typing import List

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import (
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter, QStackedWidget,
)

from models.company_owner import  Company
from utils.logger.logger import setup_logger
from models.employee import Employee
from utils.helpers import resource_path, find_widget, load_stylesheet_from_resource
from functools import lru_cache
from decimal import Decimal

from utils.patterns.singletone import SingletonMixin
from view.base_view import BaseView
from view.widgets.table_widget import TableWidget, DelegatesType
from view.widgets.text_edit_widget import TextEditWidget
from pyqtspinner import WaitingSpinner

class CompanyWindow(BaseView , SingletonMixin ):

    def __init__(self, widget: QWidget, controller):
        self.table_widget = None
        self.widget = widget
        self.controller = controller
        self.initUi()
        self.widget.setStyleSheet(load_stylesheet_from_resource())

    def initUi(self):
        self.setup_table_widget()



    def update_items(self, result=None, error=None):
        print(len(result))
        if error:
            raise Exception("Error in Employee get_all function..")
        if len(result) >=  0 :
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
        self.spinner = WaitingSpinner(self.spinner_widget, color=QColor(105, 15, 117),
                                      disable_parent_when_spinning=False)
        self.spinner.start()


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


    def get_column_headers(self, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return [
                "id",
                "شركة الشحن",
                "مبالغ المديونية",
                "تاريخ المديونية",
                "مبالغ مسددة",
                "المتبقي" ,
                "ملاحظة",
                "تاريخ السداد الشهري",
            ]
        else:
            return [
                "shipping_id",
                "loan_amount",
                "date_of_debt",
                "paid_amounts",
                "rem_amounts" ,
                "note",
                "monthly_payment_due_date",
            ]

    def update_table_data(self):
        return Company.get_all(callback=self.update_items)

    def create_table_item_widgets(self, rows):
        items = []
        for row in rows:
            row: Company
            shipping_name   =  str(row.shippings.name) if row.shippings is not None else ""
            shipping_percentage = row.shippings.percentage if row.shippings is not None else None
            item: List[QTableWidgetItem] = [
                self.create_table_item_widget(str(row.id), row.id),
                self.create_table_item_widget(shipping_name, shipping_percentage),
                self.create_table_item_widget(str(row.loan_amount), Decimal(row.loan_amount)),
                self.create_table_item_widget(str(row.date_of_debt), row.date_of_debt),
                self.create_table_item_widget(
                    str(row.paid_amounts), Decimal(row.paid_amounts) if row.paid_amounts else 0
                ),
                self.create_table_item_widget(
                    str(row.rem_amounts), Decimal(row.rem_amounts) if row.rem_amounts else 0
                ),
                self.create_table_item_widget(str(row.note), row.note),
                self.create_table_item_widget(
                    str(row.monthly_payment_due_date), row.monthly_payment_due_date
                ),
            ]
            items.append(item)
        return items

    def create_table_item_widget(self, for_display, for_edit):
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, for_display)
        item.setData(Qt.UserRole, for_edit)
        return item

    def setup_table_widget(self):
        columns = self.get_column_headers()
        self.table_widget = TableWidget(columns, self.controller , self )
        self.table_widget.setReadOnlyColumns([0])
        self.table_widget.add_delegate(1, DelegatesType.COMBOBOXWITHADD)
        self.table_widget.add_delegate(2, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(3, DelegatesType.DATE_EDITOR)
        self.table_widget.add_delegate(4, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(5, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(6, DelegatesType.StringDelegate)
        self.table_widget.add_delegate(7, DelegatesType.DATE_EDITOR)
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




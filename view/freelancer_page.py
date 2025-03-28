from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter, QStackedWidget,
)

from models.freelancer import FreeLancer
from utils.helpers import load_stylesheet_from_resource
from utils.patterns.singletone import SingletonMixin
from view.base_view import BaseView
from view.widgets.table_widget import TableWidget, DelegatesType
from view.widgets.text_edit_widget import TextEditWidget
from pyqtspinner import WaitingSpinner

class FreeLancerWindow(BaseView , SingletonMixin):

    def __init__(self, widget: QWidget, controller):
        self.widget = widget
        self.controller = controller

        self.initUi()
        self.widget.setStyleSheet(load_stylesheet_from_resource())

    def initUi(self):
        self._create_waiting_spinner()
        self.setup_table_widget()
        self._setup_stack_widget()
        self._setup_splitter_widget()

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
        self.spinner = WaitingSpinner(self.spinner_widget, color=QColor(105, 15, 117),
                                      disable_parent_when_spinning=False)
        self.spinner.start()

        # self.widget.setLayout(self.vbox)

    def _setup_stack_widget(self):
        print("Creating stack widget")
        self.stack_widget = QStackedWidget()

        # Ensure widgets exist before adding
        if self.table_widget is None:
            print("Warning: Table widget is None")
            self.setup_table_widget()

        if self.spinner_widget is None:
            print("Warning: Spinner widget is None")
            self._create_waiting_spinner()

        print("Adding widgets to stack")
        self.stack_widget.addWidget(self.table_widget)
        self.stack_widget.addWidget(self.spinner_widget)

        print("Stack widget count:", self.stack_widget.count())

        self.switch_window("table")

    def switch_window(self, window="loading"):
        if not hasattr(self, 'stack_widget') or not hasattr(self, 'spinner_widget'):
            return

        if window == "loading":
            self.stack_widget.setCurrentWidget(self.spinner_widget)
        elif window == "table":
            self.stack_widget.setCurrentWidget(self.table_widget)

    def setup_table_widget(self):
        columns = self.get_column_headers()

        self.table_widget = TableWidget( columns, self.controller , self )
        self.table_widget.setReadOnlyColumns([0])
        self.table_widget.add_delegate(1, DelegatesType.StringDelegate)
        self.table_widget.add_delegate(2, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(3, DelegatesType.StringDelegate)
        self.table_widget.add_delegate(4, DelegatesType.DATE_EDITOR)
        self.table_widget.itemChanged.connect(self.controller.on_item_changed)

    def _setup_splitter_widget(self):
        print("Setting up splitter widget")

        # Ensure stack widget exists
        if self.stack_widget is None:
            print("Warning: Stack widget is None, recreating")
            self._setup_stack_widget()

        self.hbox: QHBoxLayout = QHBoxLayout()
        self.splitter: QSplitter = QSplitter(Qt.Horizontal)

        print("Adding text edit to splitter")
        self.textEdit = TextEditWidget(self)
        self.splitter.addWidget(self.textEdit)

        print("Adding stack widget to splitter")
        self.splitter.addWidget(self.stack_widget)

        self.splitter.setSizes([300, 300])
        self.splitter.setStretchFactor(1, 1)

        print("Setting layout")
        self.hbox.addWidget(self.splitter)
        self.widget.setLayout(self.hbox)

        print("Updating table data")
        self.update_table_data()

    def update_table_data(self):
        return FreeLancer.get_all(callback=self.update_items)

    def get_column_headers(self, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return ["id", "تكاليف اخري", "المبلغ", "ملاحظة", "تاريخ"]
        else:
            return ["other_costs", "amount", "note", "date"]

    def create_table_item_widgets(self, rows):
        items = []
        for row in rows:
            row: FreeLancer
            item: List[QTableWidgetItem] = [
                self.create_table_item_widget(str(row.id), row.id),
                self.create_table_item_widget(row.other_costs, row.other_costs),
                self.create_table_item_widget(str(row.amount), row.amount),
                self.create_table_item_widget(row.note, row.note),
                self.create_table_item_widget(str(row.date), row.date),
            ]
            items.append(item)
        return items

    def create_table_item_widget(self, for_display, for_edit):
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, for_display)
        item.setData(Qt.UserRole, for_edit)
        return item

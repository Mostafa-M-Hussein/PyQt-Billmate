from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
)

from models.freelancer import FreeLancer
from utils.helpers import load_stylesheet_from_resource
from view.widgets.table_widget import TableWidget, DelegatesType
from view.widgets.text_edit_widget import TextEditWidget


class FreeLancerWindow:

    def __init__(self, widget: QWidget, controller):
        self.table_widget = None
        self.widget = widget
        self.controller = controller
        self.initUi()
        self.widget.setStyleSheet(load_stylesheet_from_resource())

    def initUi(self):
        self.setup_table_widget()

    def setup_table_widget(self):
        columns = self.get_column_headers()
        rows = self.get_freelancer_data()
        items = self.create_row_items(rows)
        self.table_widget = TableWidget(items,  columns, self.controller , self )
        self.table_widget.setReadOnlyColumns([0])
        self.table_widget.add_delegate(1, DelegatesType.StringDelegate)
        self.table_widget.add_delegate(2, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(3, DelegatesType.StringDelegate)
        self.table_widget.add_delegate(4, DelegatesType.DATE_EDITOR)
        self.table_widget.add_rows(items)


        self.table_widget.itemChanged.connect(self.controller.on_item_changed)

        self.hbox: QHBoxLayout = QHBoxLayout()
        self.splitter: QSplitter = QSplitter(Qt.Horizontal)

        self.textEdit = TextEditWidget(self)
        self.splitter.addWidget(self.textEdit)
        self.splitter.addWidget(self.table_widget)
        self.splitter.setSizes([300, 300])
        self.splitter.setStretchFactor(1, 1)
        self.hbox.addWidget(self.splitter)
        self.widget.setLayout(self.hbox)

    def get_freelancer_data(self):
        return FreeLancer.get_all()

    def get_column_headers(self, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return ["id", "تكاليف اخري", "المبلغ", "ملاحظة", "تاريخ"]
        else:
            return ["other_costs", "amount", "note", "date"]

    def create_row_items(self, rows):
        items = []
        for row in rows:
            row: FreeLancer
            item: List[QTableWidgetItem] = [
                self.create_table_item(str(row.id), row.id),
                self.create_table_item(row.other_costs, row.other_costs),
                self.create_table_item(str(row.amount), row.amount),
                self.create_table_item(row.note, row.note),
                self.create_table_item(str(row.date), row.date),
            ]
            items.append(item)
        return items

    def create_table_item(self, for_display, for_edit):
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, for_display)
        item.setData(Qt.UserRole, for_edit)
        return item

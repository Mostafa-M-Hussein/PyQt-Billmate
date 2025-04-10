from decimal import Decimal

from PyQt5.QtCore import QDate, Qt

from models.freelancer import FreeLancer
from view.freelancer_page import FreeLancerWindow


class FreeLancerWindowController:

    def __init__(self, parent):
        super().__init__()
        self.view: FreeLancerWindow = FreeLancerWindow(controller=self, widget=parent)

    def on_item_changed(self, item):
        self.view.table_widget.itemChanged.disconnect(self.on_item_changed)
        value = item.text()
        item.setData(Qt.DisplayRole, value)
        qdate = QDate.fromString(value, "yyyy-MM-dd")
        if value.isnumeric() and not item.data(Qt.UserRole):
            item.setData(Qt.UserRole, Decimal(value))
        elif qdate.isValid():
            item.setData(Qt.UserRole, qdate.toPyDate())
        else:
            item.setData(Qt.UserRole, value)

        print("cell changed")
        row = item.row()
        self.update_or_add_freelancer(row)
        self.view.table_widget.update_sums()

        self.view.table_widget.itemChanged.connect(self.on_item_changed)

    def update_or_add_freelancer(self, row):
        print("FreeLance Page im here")
        row_data = [
            (
                self.view.table_widget.item(row, c).data(Qt.UserRole)
                if self.view.table_widget.item(row, c)
                else []
            )
            for c in range(self.view.table_widget.columnCount())
        ]
        id_data, other_costs, amount, note, date = row_data
        print(row_data)
        if id_data is None or id_data == 0:
            id_data = -1

        if id_data == -1 and len(str(other_costs)) > 0:
            print("add new company")
            freelancer_id = FreeLancer.add(
                other_costs=str(other_costs),
                amount=amount,
                note=str(note),
                date=date,
                callback=lambda result, error: self.set_item_id(result, error, row),
            )

        elif id_data != -1:
            print("update company")
            FreeLancer.update(
                {
                    "id": id_data,
                    "other_costs": str(other_costs),
                    "amount": amount,
                    "note": str(note),
                    "date": date,
                }
            )

    def set_item_id(self, result, error, row):
        if error:
            raise error

        item = self.view.table_widget.item(row, 0)
        item.setData(Qt.UserRole, result.id)
        item.setData(Qt.DisplayRole, result.id)

    def update_field_value(self):
        pass

    def show(self) -> None:
        self.view.show()

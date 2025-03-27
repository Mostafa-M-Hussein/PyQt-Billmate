from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDateEdit


class DateWidget(QDateEdit):
    def __init__(self, date):
        super().__init__()
        self.date = date
        self.setCalendarPopup(True)
        if self.date is None:
            self.setDate(QDate.currentDate())
        else:
            self.setDate(self.date)
        self.setDisplayFormat("yyyy-MM-dd-HH")
        self.dateTimeChanged.connect(
            lambda date: self.controller.on_date_changed(date, self.row, self.col)
        )

from PyQt5.QtCore import QDate, QRect, Qt
from PyQt5.QtWidgets import (
    QPushButton,
    QLabel,
    QCalendarWidget,
    QSizePolicy,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)


class CalendarWidget(QWidget):

    def __init__(self, header_text: str, parent=None):

        super().__init__(parent=parent)

        self.header_text = header_text

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.calendar = QCalendarWidget()
        # self.calendar.activated.connect(self.controller.selected_date_checkin)

        self.calendar.setMinimumDate(QDate(QDate.currentDate()))

        self.header_label = QLabel()
        self.header_label.setObjectName("calendar_header_label")
        self.header_label.setText(self.header_text)

        self.exit_button = QPushButton()
        # self.exit_button.clicked.connect(self.controller.calendar_close_button)

        self.exit_button.setObjectName("calendar_close_button")

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.header_label)
        self.hbox.addWidget(self.exit_button, 10, Qt.AlignRight | Qt.AlignVCenter)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.vbox.addSpacing(5)
        self.vbox.addWidget(self.calendar)
        self.setLayout(self.vbox)
        # self.setContentsMargins(10, 10, 10, 10)
        # self.setGeometry(self.geometry.x(), self.geometry.y(), 500, 500)
        self.hide()

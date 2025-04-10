from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QStackedWidget, QWidget, QVBoxLayout

from pyqtspinner import WaitingSpinner

from view.widgets.table_widget import TableWidget


class StackedWidget(QStackedWidget):
    def __init__(self):
        super().__init__()
        # self._create_waiting_spinner()

        print("table_widget", self.widget(0))
        # self.showLoadingWidget()
        # print ("table_widget" ,  self.currentWidget() )
        # print ( self.widget(1) )
        # print ( self.widget(0) )
        # print ( self.widget(2) )

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
        self.addWidget(self.spinner_widget)
        self.setLayout(self.vbox)

    def showLoadingWidget(self):
        self.setCurrentWidget(self.widget(0))

    def showTableWidget(self):
        self.setCurrentWidget(self.widget(1))

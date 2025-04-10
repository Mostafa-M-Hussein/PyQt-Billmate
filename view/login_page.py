from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QApplication,
)
from utils.helpers import load_stylesheet_from_resource, find_widget
from view.ui.login_window import Ui_Form


class LoginWindow(QWidget):

    def __init__(self, controller=None, model=None):
        super().__init__()
        self.controller = controller
        self.model = model
        self.init_ui()
        self.setStyleSheet(load_stylesheet_from_resource())

    def init_ui(self):
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("Manager")
        self.setWindowIcon(QIcon(":icons/icons/icon.png"))
        screen = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.geometry()

        # Calculate center position
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2

        # Move window to center
        self.move(x, y)
        self.passwordLineEdit: QLineEdit = find_widget(
            self, QLineEdit, "passwordLineEdit"
        )
        self.usernameLineEdit: QLineEdit = find_widget(
            self, QLineEdit, "usernameLineEdit"
        )
        self.submitButton: QPushButton = find_widget(self, QPushButton, "pushButton")
        self.submitButton.clicked.connect(self.controller.on_submit_clicked)

from PyQt5.QtWidgets import QMessageBox

from controllers.home_page_controller import MainWindowController
from models.user import User
from utils.settings_manager import SettingManager
from view.login_page import LoginWindow


class LoginWindowController:
    def __init__(self):
        super().__init__()
        self.view: LoginWindow = LoginWindow(
            controller=self
        )

    def on_submit_clicked(self):
        username = self.view.usernameLineEdit.text()
        password = self.view.passwordLineEdit.text()
        if username and password and len(username) > 0 and len(password) > 0:
            check_user = User.verify(username, password)
            print(check_user)
            if check_user:
                settings = SettingManager()
                main_controller = MainWindowController()
                settings.set_value("current_role", check_user.role)
                print(settings.get_value("current_role"))
                self.view.close()
                main_controller.show()
            else:
                QMessageBox.warning(self.view, "Error", "cannot find  username or password..")
        else:
            QMessageBox.warning(self.view, "Error", "there's missing values you have to fill it")

    def show(self):
        self.view.show()

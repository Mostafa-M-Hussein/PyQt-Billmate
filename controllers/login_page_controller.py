from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QApplication

from controllers.home_page_controller import MainWindowController
from models.user import User
from utils.settings_manager import SettingManager
from view.login_page import LoginWindow


class LoginWindowController(QObject):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.view: LoginWindow = LoginWindow(controller=self)
        self.settings = SettingManager()
        self.closed = False
        self.is_verifying = False  # Add a flag to track verification state

    def on_submit_clicked(self):
        if self.is_verifying:
            return  # Ignore clicks if verification is in progress

        self.is_verifying = True  # Set the flag to indicate verification started
        self.view.submitButton.setEnabled(
            False
        )  # Disable the button to prevent further clicks

        try:
            username = self.view.usernameLineEdit.text()
            password = self.view.passwordLineEdit.text()
            if username and password and len(username) > 0 and len(password) > 0:
                check_user = User.verify(
                    username, password, callback=self.on_data_enter
                )

            else:
                msg_box = QMessageBox.warning(
                    self.view, "Error", "there's missing values you have to fill it"
                )
                self.is_verifying = False  # Reset the flag if there are missing values
                self.view.submitButton.setEnabled(True)  # Re-enable the button
                if msg_box == QMessageBox.Ok:
                    pass  # You can add actions here if needed

        except Exception as e:
            QMessageBox.warning(self.view, "Error", str(e))
            self.is_verifying = False  # Reset the flag in case of an exception
            self.view.submitButton.setEnabled(True)  # Re-enable the button

    def on_data_enter(self, result, error):
        try:
            self.is_verifying = False  # Reset the flag as verification is complete
            self.view.submitButton.setEnabled(True)  # Re-enable the button

            if error:
                QMessageBox.warning(self.view, "error", str(error))
            if result:
                print(result.role)
                self.settings.set_value("current_role", result.role)
                # Schedule GUI updates on the main thread
                self.view.hide()
                self.finished.emit()
                print("done")
            else:
                QMessageBox.warning(self.view, "Error", "Invalid username or password.")
        except Exception as e:
            print(str(e))
            QMessageBox.warning(self.view, "Error", f"Login failed: {str(e)}")

    def show(self):
        self.view.show()

import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

from controllers.home_page_controller import MainWindowController
from controllers.login_page_controller import LoginWindowController
from models.db_context import ensure_tables
from utils.helpers import load_stylesheet_from_resource
from resources import resources_rc
from utils.seeder import seed_users


# class AnimatedSplashScreen(QSplashScreen):
#     def __init__(self, gif_path):
#         # Start with a placeholder pixmap
#         pixmap = QPixmap(400, 300)  # Adjust size as needed
#         super().__init__(pixmap=pixmap)
#
#         # Setup movie
#         self.movie = QMovie(gif_path)
#         self.movie.frameChanged.connect(self.update_splash)
#
#         # Window flags
#         self.setWindowFlags(
#             Qt.WindowStaysOnTopHint |
#             Qt.SplashScreen |
#             Qt.FramelessWindowHint
#         )
#
#     def update_splash(self):
#         # Update pixmap with current frame
#         current_pixmap = self.movie.currentPixmap()
#         self.setPixmap(current_pixmap)
#         self.resize(current_pixmap.size())
#
#     def start(self):
#         self.movie.start()
#         self.show()
#
#     def stop(self):
#         self.movie.stop()
#         self.close()


class Main:
    def __init__(self):
        self.app = None
        self.splash_screen = None
        self.main_window = None
        self.login_window = None

    def run(self):
        ensure_tables()
        # seed_users()
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(load_stylesheet_from_resource())
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)

        self.login_window = LoginWindowController()
        self.login_window.finished.connect(
            lambda: QTimer.singleShot(1000, self.start_main_window)
        )
        self.login_window.show()
        # self.splash_screen = AnimatedSplashScreen(":icons/icons/loading.gif")
        # self.splash_screen.start()
        #

        sys.exit(self.app.exec_())

    def start_main_window(self):
        self.main_window = MainWindowController()
        self.main_window.view.configureWindow()
        self.main_window.view.show()
        self.login_window.view.close()
        self.login_window = None  # Explicitly delete

        # del self.login_window

    def on_startup_complete(self):
        self.splash_screen.stop()
        self.splash_screen = None


if __name__ == "__main__":
    Main().run()

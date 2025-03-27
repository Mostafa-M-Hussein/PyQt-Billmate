import asyncio
import subprocess
import sys
import threading
import time

from PyQt5.QtCore import Qt, QTimer, QEventLoop, QThread, pyqtSignal, QThreadPool
from PyQt5.QtGui import QPixmap , QMovie
from PyQt5.QtWidgets import QApplication, QSplashScreen, QLabel
from controllers.home_page_controller import MainWindowController
from controllers.login_page_controller import LoginWindowController
from models.db_context import ensure_tables
from utils.helpers import load_stylesheet_from_resource
from utils.seeder import seed
from utils.settings_manager import SettingManager
from PyQt5 import sip
from resources import  resources_rc
from pyqtspinner import  WaitingSpinner
import sys
from PyQt5.QtCore import Qt, QTimer, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QSplashScreen

from controllers.home_page_controller import MainWindowController
from models.db_context import ensure_tables
from utils.settings_manager import SettingManager


class AnimatedSplashScreen(QSplashScreen):
    def __init__(self, gif_path):
        # Start with a placeholder pixmap
        pixmap = QPixmap(400, 300)  # Adjust size as needed
        super().__init__(pixmap=pixmap)

        # Setup movie
        self.movie = QMovie(gif_path)
        self.movie.frameChanged.connect(self.update_splash)

        # Window flags
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.SplashScreen |
            Qt.FramelessWindowHint
        )

    def update_splash(self):
        # Update pixmap with current frame
        current_pixmap = self.movie.currentPixmap()
        self.setPixmap(current_pixmap)
        self.resize(current_pixmap.size())

    def start(self):
        self.movie.start()
        self.show()

    def stop(self):
        self.movie.stop()
        self.close()


class StartupWorker(QObject):

    startup_complete = pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def perform_startup_tasks(self):
        try:

            ensure_tables()

            main_window = MainWindowController()

            settings = SettingManager()




            self.startup_complete.emit(main_window)

        except Exception as e:
            print(f"Startup error: {e}")
            self.startup_complete.emit(None)


class Main:
    def __init__(self):
        self.app = None
        self.splash_screen = None
        self.main_window = None

    def run(self):
        ensure_tables()
        # seed(200)
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(load_stylesheet_from_resource())
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)


        self.splash_screen = AnimatedSplashScreen(":icons/icons/loading.gif")
        self.splash_screen.start()
        # self.app.processEvents(QEventLoop.AllEvents)

        main_window = MainWindowController()

        QTimer.singleShot(3500 , lambda  : self.on_startup_complete(main_window))


        for t in threading.enumerate() :
            print(t.is_alive())
            print(t.name)


        sys.exit(self.app.exec_())

    def on_startup_complete(self, main_window):
        if self.splash_screen:
            self.splash_screen.stop()

        if main_window:
            self.main_window = main_window
            self.main_window.show()
        else:
            print("Startup failed")


if __name__ == "__main__":
    Main().run()
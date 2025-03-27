from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QSplashScreen, QApplication

from models import logger


class PrintThread(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)

    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self._is_running = False

    def run(self) -> None:
        try:
            self._is_running = True
            splash_screen_pixmap = QPixmap(":icons/icons/delete.png")
            splash_screen = QSplashScreen(splash_screen_pixmap, Qt.WindowStaysOnTopHint)
            splash_screen.showMessage(
                "Preparing document for printing....",
                Qt.AlignBottom | Qt.AlignCenter,
                Qt.black
            )
            splash_screen.show()
            # QApplication.processEvents()

            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName("table.pdf")
            printer.setPageSize(QPrinter.A4)
            printer.setOrientation(QPrinter.Portrait)

            painter = QPainter()
            if not painter.begin(printer):
                self.finished.emit(False, "Failed to open PDF file for writing")
                return

            table_width = self.widget.width()
            table_height = self.widget.height()

            page_rect = printer.pageRect()
            x_scale = page_rect.width() / table_width
            y_scale = page_rect.height() / table_height
            scale_factor = min(x_scale, y_scale)  # Changed to min to prevent overflow
            painter.scale(scale_factor, scale_factor)
            self.widget.render(painter)
            painter.end()

            splash_screen.finish(None)
            self.finished.emit(True, "PDF generated successfully")

        except Exception as e:
            logger.debug(e, exc_info=True)
            self.finished.emit(False, str(e))
        finally:
            self._is_running = False

    def stop(self):
        if self._is_running:
            self.terminate()
            self.wait()

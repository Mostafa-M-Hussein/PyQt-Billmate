import os
import sys
import re
import json
from PyQt5.QtCore import QFile, QTextStream, QDir
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication

from utils.logger.logger import setup_logger
from utils.errors import WidgetNotFoundError

logger = setup_logger("helpers", "logs/helpers.log")


def resource_path(paths: [], enable_error=True):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    path = os.path.join(base_path, os.path.join(*paths))
    if enable_error:
        assert os.path.exists(path), f"cannot find this path -- {path}"
    return path


def load_stylesheet_from_resource():
    qss_file = QFile(":styles/styles/style.qss")
    if not qss_file.exists():
        print("unable to find stylesheet file  ")
        return ""
    else:
        qss_file.open(QFile.ReadOnly | QFile.Text)
        text_stream = QTextStream(qss_file)
        stylesheet = text_stream.readAll()
        qss_file.close()
        return stylesheet


def read_frame(frame_number, image_format="png"):
    frame_filename = f"{frame_number:01d}.{image_format}"
    frame_path = resource_path(["App", "resources", "video_frames", frame_filename])
    assert os.path.exists(frame_path), f"cannot find the frame folder  {frame_path}"
    if not os.path.exists(frame_path):
        return QPixmap()
    pixmap = QPixmap(frame_path)
    return pixmap


def test_widget(widget):
    try:
        app = QApplication(sys.argv)
        window = widget()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(e, exc_info=True)


def find_widget(parent, widget_class, object_name):
    widget = parent.findChild(widget_class, object_name)
    if widget is None:
        raise WidgetNotFoundError(
            f"{widget_class.__name__} with objectName '{object_name}' not found."
        )

    return widget


def split_text_by_width(text, max_width, inputBox):
    lines = []
    current_line = ""
    for word in text:
        current_line += word
        word_width = inputBox.fontMetrics().width(current_line)
        if word_width >= max_width:
            current_line += "\n"
            lines.append(current_line)
            current_line = ""

    if current_line:
        lines.append(current_line)
    return "".join(lines)


def is_it_all_arabic(s):
    return not re.search(
        r"[^\u0600-\u06FF\u0020-\u0040\u005B-\u0060\u007B-\u007E]", s or ""
    )


def contains_arabic(text):
    return bool(re.search(r"[\u0600-\u06FF\u0750-\u077F]", text or ""))


def get_setup_info():
    jsonPath = os.path.join(QDir.currentPath(), "initials.json")
    if not os.path.exists(jsonPath):
        return {"baseURL": None, "botName": None}
    with open(jsonPath) as json_file:
        initData = json.load(json_file)
    return initData

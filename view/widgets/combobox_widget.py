import typing

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QAbstractItemModel, QStringListModel
from PyQt5.QtGui import QPainter, QIcon
from PyQt5.QtWidgets import (
    QComboBox,
    QStyleOptionComboBox,
    QCompleter,
    QAbstractItemView,
    QStyle,
)

from models.employee import PaymentStatus


class ComboBoxWidget(QComboBox):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setPlaceholderText("Status")
        self.setLayoutDirection(Qt.LeftToRight)
        # self.setAttribute(Qt.WA_DeleteOnClose, False)

    # def closeEvent(self, a0: typing.Optional[QtGui.QCloseEvent]) -> None:
    #     a0.ignore()

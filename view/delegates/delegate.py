import decimal
import enum
import typing
from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtCore import QDate, Qt, QModelIndex, QRectF, QSize, QLocale, QTimer
from PyQt5.QtGui import QPainterPath, QColor, QBrush, QPainter, QDoubleValidator
from PyQt5.QtWidgets import (
    QStyledItemDelegate,
    QSpinBox,
    QDateEdit,
    QStyleOptionViewItem,
    QWidget, QLineEdit, QMessageBox, QComboBox, QTableView, QApplication, )

from models.company_owner import Coupon, ShippingCompany, Payment
from models.constant import OrderStatus
from models.employee import PaymentStatus
from .. import logger
from ..widgets.combobox_widget import ComboBoxWidget
from ..widgets.combobox_withadd_widget import ComboBoxWithAdd


class DelegatesType(enum.Enum):
    COMBOBOXORDER = 0
    COMBOBOXPAYMENT = 1
    COMBOBOXWITHADD = 2
    DATE_EDITOR = 3
    SPINBOX_EDITOR = 4
    CUSTOMTYPE = 5
    NumericalDelegate = 6
    StringDelegate = 7


class NumericalDelegate(QStyledItemDelegate):
    """
    Delegate to validate input for numerical values in QTableWidget cells.
    Allows integers and floating-point numbers.
    """

    def createEditor(self, parent: typing.Optional[QWidget], option: 'QStyleOptionViewItem', index: QModelIndex) -> \
            typing.Optional[QWidget]:
        editor = QLineEdit(parent)
        # Use QDoubleValidator directly
        validator = QDoubleValidator(parent)  # For integers and floats
        editor.setValidator(validator)
        return editor

    def setModelData(self, editor: QWidget, model: typing.Optional[QtCore.QAbstractItemModel],
                     index: QModelIndex) -> None:
        if isinstance(editor, QLineEdit):
            text = editor.text()
            if self.validate_input(text):
                model.setData(index, text, Qt.DisplayRole)
            else:
                # Optionally provide visual feedback or revert to previous value
                QMessageBox.warning(editor, "Invalid Input", "Please enter a valid numerical value.")
                # Revert to the original data (optional - you can choose to do nothing to reject edit)
                model.setData(index, index.data(Qt.DisplayRole), Qt.DisplayRole)

    def validate_input(self, text: str) -> bool:
        """
        Validates if the input text is a valid numerical value (integer or float).
        """
        try:
            QLocale().toDouble(text)  # Still use QLocale().toDouble for parsing with locale awareness
            return True
        except:
            return False


class StringDelegate(QStyledItemDelegate):
    """
    Delegate to validate input for string/text values in QTableWidget cells.
    By default, it ensures that the input is not empty and is a string.
    You can customize `validate_input` for more specific string validation.
    """

    def createEditor(self, parent: typing.Optional[QWidget], option: 'QStyleOptionViewItem', index: QModelIndex) -> \
            typing.Optional[QWidget]:
        editor = QLineEdit(parent)
        return editor

    def setModelData(self, editor: QWidget, model: typing.Optional[QtCore.QAbstractItemModel],
                     index: QModelIndex) -> None:
        if isinstance(editor, QLineEdit):
            text = editor.text()
            if self.validate_input(text):
                model.setData(index, text, Qt.DisplayRole)
            else:
                QMessageBox.warning(editor, "Invalid Input", "Please enter a valid text value (cannot be empty).")
                # Revert to the original data
                model.setData(index, index.data(Qt.DisplayRole), Qt.DisplayRole)

    def validate_input(self, text: str) -> bool:
        """
        Validates if the input text is a valid string (e.g., not empty).
        Customize this method for more specific string validation rules.
        """
        return isinstance(text, str) and text.strip() != ""  # Example: Not empty string


class CellDataTypeDelegate(QStyledItemDelegate):

    def setEditorData(
            self, editor: typing.Optional[QWidget], index: QtCore.QModelIndex
    ) -> None:
        value = index.data(Qt.DisplayRole)
        if value:
            editor.setText(value)
        super().setEditorData(editor, index)


class DateEditorDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDisplayFormat("yyyy-MM-dd")
        editor.setDate(QDate.currentDate())  # Default to current date
        return editor

    def setEditorData(self, editor, index) -> None:
        value = index.data(Qt.DisplayRole)
        if value:
            if isinstance(value, str):
                qdate = QDate.fromString(value, "yyyy-MM-dd")
                if qdate.isValid():
                    editor.setDate(qdate)
                else:
                    logger.warning(f"Invalid date string: {value}")

            elif isinstance(value, (datetime.date, datetime.datetime)):
                editor.setDate(QDate(value.year, value.month, value.day))

            elif isinstance(value, QDate):
                editor.setDate(value)

            else:
                logger.warning("Unsupported date format, using current date")
                editor.setDate(QDate.currentDate())
        else:
            editor.setDate(QDate.currentDate())

        if value is None:
            editor.setDate(QDate.currentDate())

        logger.debug(f"Raw value from index: {value} (type: {type(value)})")

    def setModelData(self, editor, model, index) -> None:
        qdate = editor.date()
        if qdate is None:
            qdate = QDate.currentDate()
        logger.debug(f"Saving date to model: {qdate.toString(Qt.ISODate)}")
        model.setData(index, qdate.toString(Qt.ISODate), Qt.DisplayRole)
        model.setData(index, qdate, Qt.UserRole)


class TextEditDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        # Custom painting for the item
        text = index.data(Qt.DisplayRole)
        painter.save()
        painter.drawText(option.rect, Qt.AlignLeft, text)
        painter.restore()

    def sizeHint(self, option, index):
        # Custom size hint for the item
        return QSize(200, 50)  # Set a fixed size for the item


class ComboBoxEditorPayment(QStyledItemDelegate):

    def paint(
            self,
            painter: typing.Optional[QPainter],
            option: "QStyleOptionViewItem",
            index: QModelIndex,
    ) -> None:
        value = index.data(Qt.UserRole)
        if value and type(value) == str:
            value = PaymentStatus.get_status(value)

        rect = option.rect
        rect_f = QRectF(rect)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(rect_f, 0, 0)

        if value == PaymentStatus.PENDING:
            painter.fillPath(path, QColor(255, 244, 142))
        elif value == PaymentStatus.COMPLETED:
            painter.fillPath(path, QColor(175, 225, 175))
        elif value == PaymentStatus.REFUSED:
            painter.fillPath(path, QColor(255, 0, 0))

        super().paint(painter, option, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    # def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
    def createEditor(self, parent, option, index):
        value = index.data(Qt.DisplayRole)
        editor = ComboBoxWidget(parent)

        editor.addItems([PaymentStatus.get_str(status) for status in PaymentStatus])
        if value:
            editor.setCurrentText(value)
        return editor

    def editorEvent(self, event, model, option, index):
        """
        Robust method to handle ComboBox editor events with improved error handling

        Args:
            event: Qt event
            model: Data model
            option: Style option
            index: Model index

        Returns:
            bool: Whether event was handled
        """
        try:
            # Check if it's a left mouse button press
            if (event.type() == event.MouseButtonPress and
                    event.button() == Qt.LeftButton):

                # Get the table widget
                table = option.widget

                # Ensure the table is valid
                if not isinstance(table, QTableView):
                    return super().editorEvent(event, model, option, index)

                # Start editing
                table.edit(index)

                # Use QApplication to find the focused widget
                app = QApplication
                focused_widget = app.focusWidget()

                # Verify it's a QComboBox
                if isinstance(focused_widget, QComboBox):
                    # Store reference to active editor
                    self._active_editor = focused_widget

                    # Safely show popup with a small delay
                    QTimer.singleShot(0, self._show_popup)

                return True

            return super().editorEvent(event, model, option, index)

        except RuntimeError:
            # Handle potential deleted object scenarios
            print("Editor event encountered a runtime error")
            return False

    def _show_popup(self):
        """
        Safely show ComboBox popup
        """
        try:
            if self._active_editor and isinstance(self._active_editor, QComboBox):
                self._active_editor.showPopup()
        except Exception as e:
            print(f"Error showing popup: {e}")

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        editor.setCurrentText(value)  #

    def setModelData(self, editor, model, index):
        text = editor.currentText()
        model.setData(index, text, Qt.DisplayRole)  # Update the data in the model

        model.setData(
            index, PaymentStatus.get_status(text), Qt.UserRole
        )  # Update the UserRole if needed
        model.dataChanged.emit(
            index, index
        )  # Notify the view that the data has changed


class ComboBoxEditorOrder(QStyledItemDelegate):

    def paint(
            self,
            painter: typing.Optional[QPainter],
            option: "QStyleOptionViewItem",
            index: QModelIndex,
    ) -> None:
        value = index.data(Qt.UserRole)
        # print(value)
        if value and type(value) == str:
            value = OrderStatus.get_status(value)

        rect = option.rect
        rect_f = QRectF(rect)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(rect_f, 0, 0)

        if value:
            if value == OrderStatus.PENDING:
                painter.fillPath(path, QColor(255, 244, 142))
            elif value == OrderStatus.COMPLETED:
                painter.fillPath(path, QColor(175, 225, 175))
            elif value == OrderStatus.REFUSED:
                painter.fillPath(path, QColor(255, 0, 0))

        super().paint(painter, option, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    # def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
    def createEditor(self, parent, option, index):
        value = index.data(Qt.DisplayRole)
        editor = ComboBoxWidget(parent)
        editor.addItems([OrderStatus.get_str(status) for status in OrderStatus])
        if value:
            editor.setCurrentText(value)
        return editor

    def editorEvent(self, event, model, option, index):
        """
        Robust method to handle ComboBox editor events with improved error handling

        Args:
            event: Qt event
            model: Data model
            option: Style option
            index: Model index

        Returns:
            bool: Whether event was handled
        """
        try:
            # Check if it's a left mouse button press
            if (event.type() == event.MouseButtonPress and
                    event.button() == Qt.LeftButton):

                # Get the table widget
                table = option.widget

                # Ensure the table is valid
                if not isinstance(table, QTableView):
                    return super().editorEvent(event, model, option, index)

                # Start editing
                table.edit(index)

                # Use QApplication to find the focused widget
                app = QApplication
                focused_widget = app.focusWidget()

                # Verify it's a QComboBox
                if isinstance(focused_widget, QComboBox):
                    # Store reference to active editor
                    self._active_editor = focused_widget

                    # Safely show popup with a small delay
                    QTimer.singleShot(0, self._show_popup)

                return True

            return super().editorEvent(event, model, option, index)

        except RuntimeError:
            # Handle potential deleted object scenarios
            print("Editor event encountered a runtime error")
            return False

    def _show_popup(self):
        """
        Safely show ComboBox popup
        """
        try:
            if self._active_editor and isinstance(self._active_editor, QComboBox):
                self._active_editor.showPopup()
        except Exception as e:
            print(f"Error showing popup: {e}")

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        editor.setCurrentText(value)  #

    def setModelData(self, editor, model, index):
        text = editor.currentText()
        model.setData(index, text, Qt.DisplayRole)  # Update the data in the model
        model.setData(
            index, OrderStatus.get_status(text), Qt.UserRole
        )  # Update the UserRole if needed
        model.dataChanged.emit(
            index, index
        )  # Notify the view that the data has changed


class SpinBoxEditorDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setMinimum(-1)
        editor.setMaximum(100)

        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        try:
            editor.setValue(int(value) if value is not None else -1)
        except (TypeError, ValueError):
            editor.setValue(-1)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value(), Qt.EditRole)

    def paint(self, painter, option, index):
        if index.data() is None:
            return
        try:
            value = int(index.data())
            if value < 0:
                painter.fillRect(option.rect, QBrush(QColor(255, 200, 200)))
        except (TypeError, ValueError):
            pass
        super().paint(painter, option, index)


class ComboBoxWithAddDelegate(QStyledItemDelegate):

    def createEditor(self, parent: typing.Optional[QWidget], option: 'QStyleOptionViewItem',
                     index: QtCore.QModelIndex) -> typing.Optional[QWidget]:

        try:



            col = index.column()
            column_name = index.model().headerData(col, Qt.Horizontal)
            current_text = index.data(Qt.DisplayRole)
            editor = ComboBoxWithAdd(parent=parent, column_name=column_name)
            editor.setEditable(False)  # Optional: Disable manual text entry
            editor.clear()

            if column_name == "كوبون الخصم":

                # editor.addItem("Loading..")


                coupons = Coupon.get_all(
                )
                coupons.finished.connect(self.addEditorItems)


            elif column_name == "وسيلة الدفع":
                payments = Payment.get_all()
                payments.finished.connect(self.addEditorItems)



            elif column_name == "شركة الشحن":
                shippings = ShippingCompany.get_all()
                shippings.finished.connect(self.addEditorItems)



            else:
                raise Exception(f"There's no column named {column_name}")

            editor.addItem(editor.add_item_text)
            editor.add_delegate_index()
            editor.update()
            if current_text != editor.add_item_text:
                if current_text:
                    editor.setCurrentText(current_text)
            return editor


        except Exception as e:
            logger.error(e, exc_info=True)
    def addEditorItems(self , result = None , error= None  ):

        loading_item_index = self._active_editor.findText("Loading..")

        # self._active_editor.removeItem(loading_item_index)
        if result and len(result) > 0 :

            for item in result:
                if isinstance(item  , Coupon ) :
                    self._active_editor.add_item(item.code, decimal.Decimal(item.discount))
                elif isinstance(item , Payment ) :
                    self._active_editor.add_item(item.name, decimal.Decimal(item.percentage))
                elif  isinstance(item , ShippingCompany ) :
                    self._active_editor.add_item(item.name, decimal.Decimal(item.percentage))
                else :
                    raise  Exception("item error")


            self._active_editor.add_delegate_index()
            self._active_editor.update()
            self._active_editor.view().update()



    def editorEvent(self, event, model, option, index):
        """
        Robust method to handle ComboBox editor events with improved error handling

        Args:
            event: Qt event
            model: Data model
            option: Style option
            index: Model index

        Returns:
            bool: Whether event was handled
        """
        try:
            # Check if it's a left mouse button press
            if (event.type() == event.MouseButtonPress and
                    event.button() == Qt.LeftButton):

                # Get the table widget
                table = option.widget

                # Ensure the table is valid
                if not isinstance(table, QTableView):
                    return super().editorEvent(event, model, option, index)

                # Start editing
                table.edit(index)

                # Use QApplication to find the focused widget
                app = QApplication
                focused_widget = app.focusWidget()

                # Verify it's a QComboBox
                if isinstance(focused_widget, QComboBox):
                    # Store reference to active editor
                    self._active_editor = focused_widget

                    # Safely show popup with a small delay
                    QTimer.singleShot(0, self._show_popup)

                return True

            return super().editorEvent(event, model, option, index)

        except RuntimeError:
            # Handle potential deleted object scenarios
            print("Editor event encountered a runtime error")
            return False

    def _show_popup(self):
        """
        Safely show ComboBox popup
        """
        try:
            if self._active_editor and isinstance(self._active_editor, QComboBox):
                self._active_editor.showPopup()
        except Exception as e:
            print(f"Error showing popup: {e}")

    def setEditorData(self, editor: typing.Optional[QWidget], index: QtCore.QModelIndex) -> None:
        display_value = index.data(Qt.DisplayRole)
        user_value = index.data(Qt.UserRole)
        # print("setEditorData - Display Value from Index:", display_value)
        # print("setEditorData - User Value from Index:", user_value)
        if display_value:
            editor.setCurrentText(display_value)  # Set the current text to the existing display value

    def setModelData(self, editor: typing.Optional[QWidget], model: typing.Optional[QtCore.QAbstractItemModel],
                     index: QtCore.QModelIndex) -> None:
        """
        Saves the data from the editor widget back to the model.
        """
        text = editor.currentText()
        user_data = editor.currentData(Qt.UserRole)

        if text == "اضافة":
            return

        model.setData(index, text, Qt.DisplayRole)
        model.setData(index, user_data, Qt.UserRole)

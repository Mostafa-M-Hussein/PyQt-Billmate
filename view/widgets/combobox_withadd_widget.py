import decimal

from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QDoubleValidator, QIcon
from PyQt5.QtWidgets import QLineEdit, QDialog, QDialogButtonBox, QFormLayout, QLabel, QStyledItemDelegate, QStyle, \
    QComboBox, QMessageBox, QMenu, QAction, QApplication, QListView

from models.company_owner import Coupon, Payment, ShippingCompany


class TwoInputDialog(QDialog):
    def __init__(self, parent=None, column_name=None):
        super().__init__(parent)
        self.column_name = column_name
        self.setWindowTitle("MoneyMaker")
        self.setLayoutDirection(Qt.RightToLeft)

        print("column ==>", column_name)
        # Create input fields
        self.input1 = QLineEdit()
        self.input1.setLayoutDirection(Qt.RightToLeft)

        self.input2 = QLineEdit()
        self.input2.setLayoutDirection(Qt.RightToLeft)

        double_validator = QDoubleValidator()
        double_validator.setBottom(0)
        double_validator.setTop(100000)
        double_validator.setDecimals(5)
        self.input2.setValidator(double_validator)

        # self.input1.setStyleSheet("""
        #  }""")
        # self.input2.setStyleSheet("""QLineEdit{
        #      border  : 3px solid red ;
        #   }""")
        # Create buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttons.button(QDialogButtonBox.Ok).setText("موافق")
        self.buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        # Layout
        layout = QFormLayout()
        layout.setFormAlignment(Qt.AlignRight | Qt.AlignTop)
        layout.setLabelAlignment(Qt.AlignRight)
        lable1_name: str = ""
        lable2_name: str = ""
        if self.column_name == "كوبون الخصم":
            lable1_name = "كود الخصم"
            lable2_name = "نسبة الخصم %"
        elif self.column_name == "وسيلة الدفع":
            lable1_name = "وسيله الدفع"
            lable2_name = "نسبة الخصم %"
        elif self.column_name == "شركة الشحن":
            lable1_name = "شركة الشحن"
            lable2_name = "السعر SAR"
        else:
            lable1_name = "لا يوجد"
            lable2_name = "لا يوجد"

        label1 = QLabel(lable1_name)
        label2 = QLabel(lable2_name)

        label1.setLayoutDirection(Qt.RightToLeft)
        label2.setLayoutDirection(Qt.RightToLeft)
        label1.setAlignment(Qt.AlignRight)
        label2.setAlignment(Qt.AlignRight)
        layout.addRow(label1, self.input1)
        layout.addRow(label2, self.input2)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_first_text(self):
        return self.input1.text()

    def get_second_text(self):
        if self.input2.hasAcceptableInput():
            return self.input2.text()
        else:
            QMessageBox.warning(self.parent(), "validator", "you should enter valid number")


class AddItemDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_item_index = -1

    def paint(self, painter: QPainter, option, index):
        if index.row() == self.add_item_index:
            painter.save()

            rect = option.rect

            is_hovered = option.state & QStyle.State_MouseOver
            is_selected = option.state & QStyle.State_Selected

            if is_selected:
                background_color = QColor("#d0d0d0")
            elif is_hovered:
                background_color = QColor("#e6e6e6")
            else:
                background_color = QColor("#f0f0f0")

            painter.fillRect(rect, background_color)
            painter.setPen(QColor("#cccccc"))
            painter.drawRect(rect.adjusted(0, 0, -1, -1))
            plus_size = 12
            x = rect.left() + 10
            y = rect.center().y() - plus_size // 2
            if is_hovered or is_selected:
                painter.setPen(QColor("#333333"))
            else:
                painter.setPen(QColor("#666666"))

            painter.drawLine(x, y + plus_size // 2,
                             x + plus_size, y + plus_size // 2)
            painter.drawLine(x + plus_size // 2, y,
                             x + plus_size // 2, y + plus_size)

            text_rect = QRect(x + plus_size + 8, rect.top(),
                              rect.width() - (x + plus_size + 8), rect.height())
            painter.drawText(text_rect, Qt.AlignVCenter, "اضافة")

            painter.restore()
        else:
            super().paint(painter, option, index)


class ComboBoxWithAdd(QComboBox):
    def __init__(self, column_name, parent=None, ):
        super().__init__(parent)
        self.column_name = column_name
        self.delegate = AddItemDelegate(self)
        self.setItemDelegate(self.delegate)
        self.add_item_text = "اضافة"
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # Initialize with coupons first

        # self.addItem(self.add_item_text)

        # Set add item index to last position

        self.view().setMouseTracking(True)
        self.activated.connect(self._handle_activation)

    def show_context_menu(self, position):
        context_menu = QMenu(self)
        context_menu.setLayoutDirection(Qt.LeftToRight)
        remove_action = QAction("delete")
        remove_action.setIcon(QIcon(":icons/icons/delete.png"))
        remove_action.triggered.connect(self.remove_current_item)
        copy_action = QAction("copy")
        # remove_action.setIcon(QIcon(":icons/icons/delete.png"))
        copy_action.triggered.connect(self.copy_action_handler)
        context_menu.addAction(remove_action)
        # context_menu.addAction(copy_action)
        context_menu.exec_(self.mapToGlobal(position))

    def copy_action_handler(self):
        text = self.currentText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def remove_current_item(self):
        current_index = self.currentIndex()
        if current_index >= 0:
            text = self.currentText()
            reply = QMessageBox.question(self, "Confirm Deletion",
                                         f"Remove item '{text}'?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.column_name == "كوبون الخصم":
                    Coupon.remove(text)
                elif self.column_name == "وسيلة الدفع":
                    Payment.remove(text)
                elif self.column_name == "شركة الشحن":
                    ShippingCompany.remove(text)
                else:
                    raise Exception("error when remove the combobox item selected")

                self.removeItem(current_index)

    def add_delegate_index(self):
        if self.delegate.add_item_index != -1:
            self.removeItem(self.delegate.add_item_index)
            self.addItem(self.add_item_text)
        self.delegate.add_item_index = self.count() - 1

    def add_item(self, display_data: str, hidden_data: decimal.Decimal):
        insert_position = self.count()
        self.insertItem(insert_position, display_data, hidden_data)
        self.setItemData(insert_position, hidden_data, Qt.UserRole)
        #todo remove me if i rais an exception

        view = self.view()
        if isinstance(view, QListView):
            # Calculate WIDTH based on content
            width = view.sizeHintForColumn(0)  # Width of the longest item
            width += 2 * view.frameWidth()  # Add border width

            # Add scrollbar width if visible
            if view.verticalScrollBar().isVisible():
                scrollbar_width = view.style().pixelMetric(QStyle.PM_ScrollBarExtent)
                width += scrollbar_width

            view.setMinimumWidth(width)

            # Calculate HEIGHT based on number of items
            row_height = view.sizeHintForRow(0)  # Height of a single row
            num_items = self.model().rowCount()
            max_visible = self.maxVisibleItems()  # Max items to show without scrolling

            # Total height = row height * min(items, max_visible) + frame
            visible_rows = min(num_items, max_visible)
            height = row_height * visible_rows + 2 * view.frameWidth()

            # Ensure height doesn't exceed screen space (optional)
            screen_height = QApplication.primaryScreen().availableGeometry().height()
            height = min(height, int(screen_height * 0.75))  # Max 75% of screen

            view.setMinimumHeight(height)

        if self.view().isVisible() :
            QTimer.singleShot(0 , self.showPopup )
        # self.setCurrentIndex(insert_position)

    def _handle_activation(self, index: int):
        if index == self.delegate.add_item_index:

            if self.count() > 1:
                self.setCurrentIndex(self.count() - 2)
            else:
                self.setCurrentIndex(-1)
            self.handle_add_new_item()

    def handle_add_new_item(self):
        dialog = TwoInputDialog(self, self.column_name)

        if dialog.exec_() == QDialog.Accepted:
            text1 = dialog.get_first_text()
            text2 = dialog.get_second_text()
            if text1 and text2:
                self.add_item(text1, decimal.Decimal(text2))
                if self.column_name == "كوبون الخصم":
                    Coupon.add(code=text1, discount=text2)
                elif self.column_name == "وسيلة الدفع":
                    Payment.add(text1, text2)
                elif self.column_name == "شركة الشحن":
                    ShippingCompany.add(text1, text2)
                else:
                    raise Exception("error in line 151 combobx_withadd_widget")

                self.add_delegate_index()

    def currentData(self, role=Qt.UserRole):
        index = self.currentIndex()
        if index != -1:
            data = self.itemData(index, role)
            return data
        return None

    def setCurrentText(self, text):
        index = self.findText(text)
        if index != -1:
            self.setCurrentIndex(index)

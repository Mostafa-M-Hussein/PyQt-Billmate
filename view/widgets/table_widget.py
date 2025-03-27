import typing

from PyQt5 import sip, QtGui
from PyQt5.QtCore import Qt, QPoint, QMutex, QMutexLocker
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QMenu,
    QAction,
    QMessageBox,
    QFileDialog, )

from models.alchemy import *
from models.company_owner import CompanyOwner, Company
from models.constant import PaymentStatus, OrderStatus
from models.employee import Employee
from models.freelancer import FreeLancer
from services.excel_service import ExcelService
from services.pdf_service import PrintThread
from . import logger
from ..delegates.delegate import (
    DelegatesType,
    ComboBoxEditorPayment,
    DateEditorDelegate,
    SpinBoxEditorDelegate,
    ComboBoxEditorOrder, ComboBoxWithAddDelegate, NumericalDelegate, StringDelegate,
)



class TableWidget(QTableWidget):
    def __init__(self, columns, controller, parent=None):
        self.hidden_column_index = None
        try:
            super().__init__()
            self.parent = parent
            self.delegates = []
            self.mutex = QMutex()
            self.columns: List[str] = columns
            self.controller = controller
            self._read_only_columns = None
            self._is_removing_rows = False
            self.numerical_columns = set()
            self.sum_row_index = None
            self.last_row = None
            self._rowItems = []
            self.methods = TableAction(self)

            self.init()

        except Exception as e:
            logger.debug(e, exc_info=True)

    def closeEvent(self, a0: typing.Optional[QtGui.QCloseEvent]) -> None:
        print("Delete attempt ignore!")  # Prevents deletion

        a0.ignore()

    def deleteLater(self):
        print("Delete attempt blocked!")  # Prevents deletion

    def init(self):

        with QMutexLocker(self.mutex):
            self.hidden_column_index = self.columns.index("id")
            if self.hidden_column_index is None:
                self.hidden_column_index = 0
            self.setLayoutDirection(Qt.RightToLeft)
            self.resizeRowsToContents()
            self.setColumnCount(len(self.columns))
            self.setHorizontalHeaderLabels(self.columns)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.horizontalHeader().setStretchLastSection(True)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.verticalHeader().setVisible(False)
            self.horizontalHeader().setVisible(True)
            self.setGridStyle(Qt.PenStyle.NoPen)
            self.setShowGrid(False)
            self.setSortingEnabled(False)
            if self.isCornerButtonEnabled():
                self.setCornerButtonEnabled(False)

            self.setAlternatingRowColors(True)

            header = self.horizontalHeader()
            for i in range(len(self.columns)):
                header.setSectionResizeMode(i, QHeaderView.Interactive)

            self.setContextMenuPolicy(Qt.CustomContextMenu)

            self.customContextMenuRequested.connect(self.show_context_menu)

            self.setColumnHidden(self.hidden_column_index, True)

    def update_sums(self):
        if not sip.isdeleted(self):
            self.add_sum_row()
        else:
            logger.error("object is deleted in update sums")

    def update_column_status(self, col):
        if self.rowCount() > 0:
            for row in range(self.rowCount()):
                index = self.model().index(row, col)
                if index.isValid():
                    item = self.item(row, col)
                    self.model().setData(index, PaymentStatus.get_str(PaymentStatus.COMPLETED), Qt.DisplayRole)
                    self.model().setData(index, PaymentStatus.COMPLETED, Qt.UserRole)

    def calculate_column_sum(self, column: int):
        total = decimal.Decimal(0.0)
        for row in range(self.rowCount() - 1):
            item = self.item(row, column)
            if item:
                value = item.data(Qt.ItemDataRole.UserRole)
                if value:
                    if not value or isinstance(value, str) and len(value) == 0:
                        value = 0

                    elif isinstance(value, str) :
                        value = decimal.Decimal(value)

                    if isinstance(self.methods.current_object, CompanyOwner):
                        is_order_retrieved = self.item(row, 13)
                        is_order_retrieved = is_order_retrieved.data(Qt.UserRole)
                        if isinstance(is_order_retrieved , str ) :
                            is_order_retrieved = OrderStatus.get_status(is_order_retrieved)


                        if OrderStatus.REFUSED is  is_order_retrieved and column in [4, 5, 8]:
                            continue

                    total += value

        return f"{total:.2f}"

    @property
    def getRowItems(self):
        return self._rowItems

    def setRowItems(self, values):
        self._rowItems = values

    def adjust_row_count(self):
        viewport_height = self.viewport().height()
        row_height = self.verticalHeader().defaultSectionSize()

        if self.rowCount() > 0:
            row_height = self.rowHeight(0)

        total_rows = max(1, viewport_height // row_height)

        current_rows = self.rowCount()
        if current_rows != total_rows:
            self.setRowCount(total_rows)

    def setReadOnlyColumns(self, read_only_columns: list):
        self._read_only_columns = read_only_columns

    def add_delegate(self, column: int, delegate_type: DelegatesType):
        delegate_obj = None
        if delegate_type == DelegatesType.COMBOBOXPAYMENT:
            delegate_obj = ComboBoxEditorPayment()
        elif delegate_type == DelegatesType.COMBOBOXORDER:
            delegate_obj = ComboBoxEditorOrder()
        elif delegate_type == DelegatesType.DATE_EDITOR:
            delegate_obj = DateEditorDelegate()
        elif delegate_type == DelegatesType.SPINBOX_EDITOR:
            delegate_obj = SpinBoxEditorDelegate()
        elif delegate_type == DelegatesType.CUSTOMTYPE:
            delegate_obj = ()
        elif delegate_type == DelegatesType.COMBOBOXWITHADD:
            delegate_obj = ComboBoxWithAddDelegate()
        elif delegate_type == DelegatesType.NumericalDelegate:
            delegate_obj = NumericalDelegate()
        elif delegate_type == DelegatesType.StringDelegate:
            delegate_obj = StringDelegate()
        else:
            raise Exception("No Custom DelegateType Founded..")
        self.delegates.append((column, delegate_obj))
        self.setItemDelegateForColumn(column, delegate_obj)

        # self.verticalScrollBar().actionTriggered.connect(lambda : print("print") )

    # def wheelEvent(self, event: typing.Optional[QtGui.QWheelEvent]) -> None:
    #     max_rows = self.viewport().height() // self.rowHeight(0)
    #     if event.angleDelta().y() < 0:
    #         visible_rows = self.viewport().height() // self.rowHeight(0)
    #         rows_needed = visible_rows - self.rowCount()
    #         if rows_needed > 0 and self.rowCount() < max_rows:
    #             rows_to_add = min(
    #                 rows_needed, max_rows - self.rowCount()
    #             )  # Limit to max rows
    #             max_rows = self.rowCount() + rows_to_add
    #             for row in range(self.rowCount(), max_rows):
    #                 self.insertRow(row)
    #     super().wheelEvent(event)

    def show_context_menu(self, pos: QPoint):
        context_menu = QMenu(self)
        context_menu.setLayoutDirection(Qt.LeftToRight)
        item = self.itemAt(pos)
        if item:
            remove_action = QAction("remove row")
            remove_action.setIcon(QIcon(":icons/icons/delete.png"))
            remove_action.triggered.connect(
                lambda: self.methods.remove_action_handler(item)
            )

            add_action = QAction("add row")
            add_action.setIcon(QIcon(":icons/icons/insert.png"))
            add_action.triggered.connect(lambda: self.methods.add_action_handler())

            print_action = QAction("print")
            print_action.setIcon(QIcon(":icons/icons/printer.png"))
            print_action.triggered.connect(lambda: self.methods.print_action_handler())

            export_action = QAction("export")
            export_action.setIcon(QIcon(":icons/icons/export.png"))
            export_action.triggered.connect(
                lambda: self.methods.export_action_handler()
            )

            hide_show_action = QAction("hide Column")
            hide_show_action.setIcon(QIcon(":icons/icons/hide.png"))
            hide_show_action.triggered.connect(
                lambda: self.methods.hide_action(item.column())
            )

            show_all_action = QAction("show all columns")
            show_all_action.setIcon(QIcon(":icons/icons/eye.png"))
            show_all_action.triggered.connect(lambda: self.methods.show_all_action())

            context_menu.addAction(show_all_action)
            context_menu.addAction(hide_show_action)
            context_menu.addSeparator()
            context_menu.addAction(add_action)
            context_menu.addAction(remove_action)
            context_menu.addSeparator()
            context_menu.addAction(print_action)
            context_menu.addAction(export_action)
            # context_menu.move(pos.x() + 60, pos.y() + 150)
            context_menu.exec_(self.mapToGlobal(pos))

    def setDefaultSettings(self):
        self.sum_row_index = None
        self.setRowCount(0)

    def add_sum_row(self):
        if sip.isdeleted(self):
            logger.error("object is deleted tablewidget...")
            return
        self.blockSignals(True)

        if self.rowCount() >= 0:
            for column, delegate in self.delegates:
                if isinstance(delegate, NumericalDelegate):
                    self.numerical_columns.add(column)

            if hasattr(self, 'sum_row_index') and self.sum_row_index is not None:
                if 0 <= self.sum_row_index < self.rowCount():
                    self.removeRow(self.sum_row_index)

            self.sum_row_index = self.rowCount()
            print("sum row index is --> " ,  self.sum_row_index)
            self.insertRow(self.sum_row_index)

            for col in range(self.columnCount()):
                item = QTableWidgetItem()
                if col in self.numerical_columns:
                    sum_value = self.calculate_column_sum(col)
                    item.setData(Qt.ItemDataRole.DisplayRole, str(sum_value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    item.setBackground(Qt.GlobalColor.lightGray)

                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make read-only
                self.setItem(self.sum_row_index, col, item)

        self.blockSignals(False)

    def add_rows(self, rows: List[List[QTableWidgetItem]] = None ):
        self.blockSignals(True)

        if hasattr(self, 'sum_row_index' ) :
            self.sum_row_index = None


        if rows is None :
            rows = self.getRowItems



        print("rows count is-->" , len(rows))
        # Clear existing rows
        # if self.rowCount() > 0:
        #     self.setRowCount(0)



        # Set row count based on input
        self.setRowCount(len(rows)  if rows else 0)
        # Iterate through rows and columns
        for r in range(self.rowCount()):
            self.last_row = r

            for c in range(self.columnCount()):
                # Ensure we don't go out of bounds
                if r < len(rows) and c < len(rows[r]):
                    item = rows[r][c]
                else:
                    item = QTableWidgetItem()

                # Handle read-only columns
                if (self.read_only_columns and
                        len(self.read_only_columns) > 0 and
                        c in self.read_only_columns):
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                # Set alignment
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                # Set item in table
                self.setItem(r, c, item)

            # Resize columns
            for c in range(self.columnCount()):
                self.resizeColumnToContents(c)

        # Add sum row if needed

        self.add_sum_row()

        self.blockSignals(False)

    @property
    def read_only_columns(self):
        return self._read_only_columns


class TableAction:
    def __init__(self, tablewidget):
        self.widget: TableWidget = tablewidget
        self.current_object = self.get_current_object()
        self._print_thread = None

    def get_columns_default_values(self, obj, new_row_count):
        hidden_columns: list = self.widget.read_only_columns.copy()
        columns_type: dict = sqlalchemy_to_python_type(obj)

        i = 0
        for c, column_name in enumerate(get_columns_name(obj)):
            temp_item = QTableWidgetItem()
            column_type = columns_type.get(column_name, "")
            if hidden_columns and i in hidden_columns:
                temp_item.setFlags(temp_item.flags() & ~Qt.ItemIsEditable)
                temp_item.setData(Qt.UserRole, decimal.Decimal(0))
                temp_item.setData(Qt.DisplayRole, str(decimal.Decimal(0)))
                self.widget.setItem(new_row_count, c, temp_item)
                hidden_columns.remove(i)
                i += 1
            else:
                temp_item.setData(Qt.UserRole, column_type)
                temp_item.setData(Qt.DisplayRole, str(column_type))
                self.widget.setItem(new_row_count, c, temp_item)
                i += 1

    def add_action_handler(self):
        new_row_count = self.widget.rowCount()
        self.widget.insertRow(new_row_count)
        self.widget.itemChanged.disconnect(self.widget.controller.on_item_changed)
        if self.current_object:
            self.get_columns_default_values(self.current_object, new_row_count)
        else:
            raise Exception("There's no controller name")
        self.widget.update()
        self.widget.itemChanged.connect(self.widget.controller.on_item_changed)
        self.widget.update_sums()

    def get_current_object(self):
        controller_name = self.widget.controller.__class__.__name__
        if controller_name == "MainWindowController":
            return Employee()
        elif controller_name == "FreeLancerWindowController":
            return FreeLancer()
        elif controller_name == "CompanyWindowController":
            return Company()
        elif controller_name == "CompanyOwnerController":
            return CompanyOwner()
        else:
            raise Exception("ControllerName not found")

    def remove_action_handler(self, item: QTableWidgetItem):
        if self.widget is None or sip.isdeleted(self.widget):
            logger.error("object is deleted in remove action handler...")
            return

        item_row = item.row()
        if item_row == self.widget.sum_row_index:
            return

        hidden_item = self.widget.item(item_row, self.widget.hidden_column_index).text()
        if hidden_item != -1:
            self.current_object.remove(hidden_item)

        self.widget.removeRow(item_row)
        self.widget.sum_row_index -= 1
        self.widget.update_sums()

    def hide_action(self, column):
        total_columns_hides = 0
        for col in range(1, self.widget.columnCount()):
            if self.widget.isColumnHidden(col) :
                total_columns_hides += 1



        if total_columns_hides >=  self.widget.columnCount() - 2   :
            QMessageBox.warning(self.widget , 'info' , "you cannot hide all the columns ! ")
            return
        self.widget.hideColumn(column)

    def show_all_action(self):
        for col in range(1, self.widget.columnCount()):
            if col != self.widget.hidden_column_index:
                if self.widget.isColumnHidden(col):
                    self.widget.showColumn(col)

    def closeEvent(self, event):
        # Ensure print thread is properly cleaned up
        if self._print_thread and self._print_thread.isRunning():
            self._print_thread.stop()
            self._print_thread.wait()
        super().closeEvent(event)

    def handle_print_finished(self, success, message):
        if success:
            QMessageBox.information(self.widget, "Success", message)
        else:
            QMessageBox.warning(self.widget, "Error", message)


        if self._print_thread:
            self._print_thread.deleteLater()
            self._print_thread = None

    def print_action_handler(self):
        if self._print_thread and self._print_thread.isRunning():
            return

        self._print_thread = PrintThread(self.widget)
        self._print_thread.finished.connect(self.handle_print_finished)
        self._print_thread.start()

    def export_action_handler(self):
        try:
            excel = ExcelService()
            file_filter = "Excel  Files (*.xlsx)"
            filepath, _ = QFileDialog.getSaveFileName(
                parent=self.widget, caption="Save File", filter=file_filter
            )
            if filepath:
                # exclude the id header
                headers = self.widget.columns.copy()
                headers.remove("id")
                data_rows = []
                for row in range(self.widget.rowCount()):
                    single_row = []
                    # exclude the id
                    for col in range(self.widget.columnCount()):
                        if self.widget.isColumnHidden(col):
                            column_index = self.widget.item(row, col).column()
                            column_name = self.widget.columns[column_index]
                            if column_name in headers:
                                headers.remove(column_name)
                            continue
                        text = self.widget.item(row, col).data(Qt.DisplayRole)
                        single_row.append(text)
                    data_rows.append(single_row)
                excel.create_excel_sheet(
                    headers=headers, data_rows=data_rows, path=filepath
                )
                QMessageBox.information(
                    self.widget,
                    "Excel",
                    f"excel has been saved in this path {filepath} ",
                )
            else:
                QMessageBox.information(
                    self.widget, "E", "you did't save the filename "
                )

        except Exception as e:
            QMessageBox.information(self.widget, "E", str(e))
            logger.error(e, exc_info=True)

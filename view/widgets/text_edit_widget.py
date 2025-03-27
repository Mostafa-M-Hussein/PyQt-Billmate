from decimal import Decimal
from typing import List, Any

from PyQt5.QtCore import QLocale, QVariant, pyqtSignal
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtWidgets import QCalendarWidget
from PyQt5.QtWidgets import (
    QTextEdit,
    QSizePolicy,
    QWidget,
    QPushButton,
    QGridLayout,
    QComboBox,
    QMessageBox, QTableWidgetItem, QVBoxLayout, )
from fuzzywuzzy.fuzz import partial_ratio

from models.alchemy import get_columns_name
from models.company_owner import CompanyOwner, Company
from models.constant import PaymentStatus, OrderStatus
from models.employee import Employee
from models.freelancer import FreeLancer
from view.widgets.table_widget import TableWidget


class RangeCalendar(QCalendarWidget):
    range_selected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Popup)
        self.setMinimumDate(QDate.currentDate().addDays(-365))
        self.setMaximumDate(QDate.currentDate().addDays(365))
        self.setSelectedDate(QDate.currentDate())
        self.setWindowModality(Qt.ApplicationModal)
        self.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)

        self.start_date = None
        self.end_date = None

        self.clicked.connect(self.handle_date_click)

    def clearSelection(self):
        """Clears the selection manually and refreshes the calendar."""
        self.start_date = None
        self.end_date = None
        self.update()  # Force a repaint

    def handle_date_click(self, date):
        """Handles date selection logic for the range."""
        if not self.start_date:
            self.start_date = date
            self.end_date = None
            print(f"Start date selected: {self.start_date.toString()}")
        else:
            self.end_date = date
            print(f"End date selected: {self.end_date.toString()}")

            # Ensure start_date is always earlier than end_date
            if self.start_date > self.end_date:
                self.start_date, self.end_date = self.end_date, self.start_date

            self.range_selected.emit()
            self.clearSelection()
            self.close()

        self.update()

    def getCurrentDate(self):
        return self.start_date.toPyDate(), self.end_date.toPyDate()

    def paintCell(self, painter: QPainter, rect, date: QDate):
        """Custom painting for highlighting selected date range."""
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Highlight the range between start_date and end_date
        if date == self.selectedDate() and self.start_date == date:
            painter.setBrush(QBrush(Qt.GlobalColor.lightGray))
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)

        # Draw default content (date number)
        painter.setPen(Qt.black)
        painter.drawText(rect, Qt.AlignCenter, str(date.day()))
        painter.restore()


class TextEditWidget(QWidget):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.rows = []
        self.table_widget: TableWidget = self.widget.table_widget
        self.controller = self.widget.controller
        self.current_model_object = self.table_widget.methods.get_current_object()
        if not self.table_widget or not self.controller:
            raise Exception("error")

        print(self.width(), self.current_model_object)
        self.setMinimumWidth(100)
        self.setMaximumWidth(600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plainText = QTextEdit()
        # self.plainText.textChanged.connect(self.on_text_changed)
        self.plainText.setLocale(QLocale(QLocale.Language.Arabic))
        self.plainText.setMinimumWidth(250)
        self.plainText.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.plainText.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("searchBtn")
        self.search_btn.setIcon(QIcon(":icons/icons/search.png"))
        self.search_btn.clicked.connect(self.handle_search_button)
        self.search_btn.setStyleSheet("padding : 5px ")

        self.combobox = QComboBox()
        self.combobox.setObjectName("search_combobox")
        self.search_container = QWidget()
        self.search_container_layout = QGridLayout()
        self.search_container.setLayout(self.search_container_layout)
        self.search_container_layout.addWidget(self.plainText, 0, 0)
        self.search_container_layout.addWidget(self.search_btn, 0, 0, Qt.AlignVCenter | Qt.AlignBottom)
        # self.search_container_layout.setRowStretch(0, 10)
        # self.search_container_layout.setColumnStretch(0, 10)
        # self.combobox.setFixedSize(50 , 50 )

        exculded_columns = [
            'total_profit',
            'total_discount',
            'total_demand',
            'salla_total',
            'cost',
            'amount',
            'salary',
            'loan_from_salary',
            'amount_paid',
            'rem_from_salary',
            'amount_settled',
            'loan_amount',
            'paid_amounts',
            'retrevied_order',
            'rem_amounts',

        ]
        self.headers_display = self.widget.get_column_headers()[1:]
        self.headers_user = self.widget.get_column_headers(Qt.UserRole)
        removed_index = [self.headers_user.index(i) for i in self.headers_user if i in exculded_columns]
        headers_user_copy = self.headers_user.copy()
        headers_user_display_copy = self.headers_display.copy()
        for i in removed_index:
            self.headers_user.remove(headers_user_copy[i])
            self.headers_display.remove(headers_user_display_copy[i])
        for i, item in enumerate(self.headers_display):
            self.combobox.addItem(item)
            self.combobox.setItemData(i, QVariant(item), Qt.UserRole)

        if isinstance(self.current_model_object, CompanyOwner):
            self.combobox.addItem("رقم الطلب مع التحديث")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.search_container, 1)
        self.layout.addWidget(self.combobox, Qt.AlignVCenter)
        self.setLayout(self.layout)

    def on_text_changed(self):
        text = self.plainText.toPlainText()
        if len(text) == 0:
            rows = self.current_model_object.get_all()
            table_items = self.create_table_items(rows)
            self.table_widget.add_rows(table_items)
            self.search_btn.setText("Search")
            self.search_btn.setIcon(QIcon(":icons/icons/search.png"))

    def createCalendar(self):
        if not hasattr(self, 'calendar'):
            self.calendar = RangeCalendar()
            self.calendar.range_selected.connect(self.getSelectedDate)

    def showCalendar(self):
        pos = self.search_container.mapToGlobal(self.search_container.rect().topLeft())
        self.calendar.move(pos)
        self.calendar.show()

    def getSelectedDate(self):
        # This slot is triggered when the date selection changes
        start_date, end_date = self.calendar.getCurrentDate()
        if hasattr(self, 'selected_item') and self.selected_item:
            self.rows = self.current_model_object.search(column=self.selected_item,
                                                         start=start_date,
                                                         end=end_date ,
                                                         value=None , operator='between')
            print("item found --> ", self.rows)
            self.updateTable()
            self.search_btn.setText("Back")
            del self.selected_item
        self.calendar.hide()

    def handle_search_button(self):
        if self.search_btn.text() == "Search":
            text = self.plainText.toPlainText()
            current_search_column = self.combobox.currentIndex()
            if self.combobox.currentText() == "رقم الطلب مع التحديث":
                current_search_column = 8

            selected_item = self.headers_user[current_search_column]
            if "date" in selected_item:
                self.createCalendar()
                self.showCalendar()
                self.selected_item = selected_item
                print(self.selected_item)

            elif text:
                splitted_text = text.split("\n")
                if len(splitted_text) <= 0:
                    QMessageBox.information(
                        parent=self, title="info", text="plain text is empty"
                    )

                if selected_item is not None and selected_item in get_columns_name(
                        self.current_model_object
                ):

                    searched_text = splitted_text.copy()
                    for searched_value in splitted_text:
                        searched_value = searched_value.strip(" ")
                        if selected_item in ["payment_status", "payment_status"]:
                            for status in PaymentStatus:
                                text = PaymentStatus.get_str(status)
                                threshold = partial_ratio(searched_text, text)
                                if threshold >= 80:
                                    searched_value = status
                                    break
                        elif selected_item in ["order_status"]:
                            for status in OrderStatus:
                                text = OrderStatus.get_str(status)
                                threshold = partial_ratio(searched_text, text)
                                if threshold >= 80:
                                    searched_value = status
                                    break

                        print(selected_item, searched_value)
                        try:
                            qdate = QDate.fromString(searched_value, "yyyy-MM-dd")
                            if qdate.isValid():
                                searched_value = qdate.toPyDate()
                        except:
                            pass

                        self.updateDatabaseRows(selected_item, searched_value, searched_text)
                    self.updateTable()

                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"You Cannot make a search on this column {self.combobox.currentText()} ",
                    )

            else:
                QMessageBox.warning(self, "Error", "You should first add search text")

        else:
            self.back_button_action()

    def removeDatabaseRows(self):
        self.rows.clear()

    def updateDatabaseRows(self, selected_item, searched_value, searched_text):
        if selected_item in ["coupon_code", "payment_method", "shipping_company", 'shipping_id']:
            filters = {"coupon_code": {'coupons.code': searched_value},
                       "shipping_company": {"shippings.name": searched_value},
                       "payment_method": {"payments.name": searched_value},
                       "shipping_id": {"shippings.name": searched_value}
                       }
            db = self.current_model_object.search_with_relations(
                filters=filters[selected_item])
        else:
            db = self.current_model_object.search(selected_item, searched_value)
            print(db)
        if len(db) > 0 and db not in self.rows:
            self.rows.extend(db)
            if isinstance(searched_value, PaymentStatus):
                searched_value = PaymentStatus.get_str(searched_value)
            elif isinstance(searched_value, OrderStatus):
                searched_value = OrderStatus.get_str(searched_value)

            try:
                searched_text.remove(searched_value)
            except:
                searched_text.pop(0)

        self.plainText.setPlainText('\n'.join(searched_text))
        if len(self.rows) == 0:
            QMessageBox.warning(self, "Error", f"there's  no item founded..")
            return False
        return True

    def updateTable(self):
        if len(self.rows) > 0:
            table_items = self.create_table_items(self.rows)
            self.table_widget.add_rows(table_items)
            print(table_items)
            if isinstance(self.current_model_object,
                          CompanyOwner) and self.combobox.currentText() == "رقم الطلب مع التحديث":
                print("update the status order ")
                self.table_widget.update_column_status(3)
            self.search_btn.setText("Back")
            self.search_btn.setIcon(QIcon(":icons/icons/left-arrows.png"))
            self.removeDatabaseRows()

    def back_button_action(self):
        rows = self.current_model_object.get_all()
        self.table_widget.setDefaultSettings()
        table_items = self.create_table_items(rows)
        self.table_widget.add_rows(table_items)
        self.search_btn.setText("Search")
        self.search_btn.setIcon(QIcon(":icons/icons/search.png"))

    def create_table_items(self, rows: List[Any]):
        items = []
        for row in rows:
            items.append(self.create_row_items(row))
        return items

    def create_row_items(self, row: Any):
        if isinstance(self.current_model_object, Employee):
            emp_id = self.create_table_item(str(row.id), row.id)
            name = self.create_table_item(str(row.name), row.name)
            salary = self.create_table_item(str(row.salary), row.salary)
            payment_status = self.create_table_item(
                PaymentStatus.get_str(row.payment_status), row.payment_status
            )
            loan_from_salary = self.create_table_item(
                str(row.loan_from_salary), row.loan_from_salary
            )
            rem_from_salary_cal = row.salary - row.loan_from_salary - row.amount_settled
            rem_from_salary = self.create_table_item(
                str(rem_from_salary_cal), rem_from_salary_cal
            )
            amount_settled = self.create_table_item(str(row.amount_settled), row.amount_settled)
            amount_paid_res = self.controller.calculate_amount_paid(row.amount_settled, row.loan_from_salary)
            amount_paid = self.create_table_item(
                str(amount_paid_res), amount_paid_res
            )
            loan_date = self.create_table_item(str(row.loan_date), row.loan_date)
            payment_date = self.create_table_item(str(row.payment_date), row.payment_date)
            return [
                emp_id,
                name,
                salary,
                payment_status,
                loan_from_salary,
                rem_from_salary,
                amount_paid,
                amount_settled,
                loan_date,
                payment_date,
            ]
        elif isinstance(self.current_model_object, CompanyOwner):
            coupon_code = str(row.coupons.code) if row.coupons is not None else ""
            coupon_discount = row.coupons.discount if row.coupons is not None else 0
            shipping_name = str(row.shippings.name) if row.shippings is not None else ""
            shipping_percentage = row.shippings.percentage if row.shippings is not None else 0
            payment_method = str(row.payments.name) if row.payments is not None else ""
            payment_percentage = row.payments.percentage if row.payments is not None else 0
            return [
                self.create_table_item(str(row.id), row.id),
                self.create_table_item(str(row.payment_date), row.payment_date),
                self.create_table_item(str(row.order_date), row.order_date),
                self.create_table_item(
                    PaymentStatus.get_str(row.payment_status), row.payment_status
                ),
                self.create_table_item(str(row.total_discount), row.total_discount),
                self.create_table_item(str(row.retrieved_order), row.retrieved_order),
                self.create_table_item(str(row.total_profit), row.total_profit),
                self.create_table_item(coupon_code, coupon_discount),
                self.create_table_item(payment_method, payment_percentage),
                self.create_table_item(str(row.total_demand), row.total_demand if row.total_demand else 0),
                self.create_table_item(shipping_name, shipping_percentage),
                self.create_table_item(str(row.salla_total), row.salla_total),
                self.create_table_item(str(row.cost), row.cost),
                self.create_table_item(
                    OrderStatus.get_str(row.order_status), row.order_status
                ),
                self.create_table_item(str(row.order_number), row.order_number),
                self.create_table_item(str(row.store_name), row.store_name),
            ]
        elif isinstance(self.current_model_object, Company):
            shipping_name = str(row.shippings.name) if row.shippings is not None else ""
            shipping_percentage = row.shippings.percentage if row.shippings is not None else 0
            return [
                self.create_table_item(str(row.id), row.id),
                self.create_table_item(shipping_name, shipping_percentage),
                self.create_table_item(str(row.loan_amount), Decimal(row.loan_amount)),
                self.create_table_item(str(row.date_of_debt), row.date_of_debt),
                self.create_table_item(
                    str(row.paid_amounts), row.paid_amounts if Decimal(row.paid_amounts) else 0
                ),
                self.create_table_item(
                    str(row.rem_amounts), Decimal(row.rem_amounts) if row.rem_amounts else 0
                ),
                self.create_table_item(str(row.note), row.note),
                self.create_table_item(
                    str(row.monthly_payment_due_date), row.monthly_payment_due_date
                ),
            ]
        elif isinstance(self.current_model_object, FreeLancer):
            return [
                self.create_table_item(str(row.id), row.id),
                self.create_table_item(row.other_costs, row.other_costs),
                self.create_table_item(str(row.amount), row.amount),
                self.create_table_item(row.note, row.note),
                self.create_table_item(str(row.date), row.date),
            ]
        else:
            raise Exception(f"There's no model named {self.current_model_object}")

    def create_table_item(self, for_display, for_edit):
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, for_display)
        item.setData(Qt.UserRole, for_edit)
        return item

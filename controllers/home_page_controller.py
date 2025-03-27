import datetime
from decimal import Decimal

from PyQt5 import sip
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QTableWidgetItem

from controllers.base_controller import BaseController
from models.employee import Employee, PaymentStatus
from view.home_page import MainWindow


class MainWindowController(BaseController):

    def __init__(self):
        super().__init__()
        self.view = MainWindow(self)

    def __check_fields(self, fields: list) -> bool:
        return all(isinstance(field, QTableWidgetItem) for field in fields)

    def update_employee_data(self, row):
        row_data = [
            self.view.table_widget.item(row, c).data(Qt.UserRole) if self.view.table_widget.item(row, c) else []
            for c in range(self.view.table_widget.columnCount())
        ]
        if row_data:
            (
                id_data,
                name,
                salary,
                status,
                loan_from_salary,
                amount_settled,
                rem_from_salary,
                amount_paid,
                loan_date,
                payment_date,
            ) = row_data
            print(row_data)
            print("A ======>" , amount_settled)
            if id_data is None or id_data is False:
                id_data = -1

            if id_data == -1 and name and len(name) > 0:
                emp_id = self.add_new_employee(
                    name=name,
                    salary=salary,
                    amount_settled=amount_settled,
                    loan_from_salary=loan_from_salary,
                    loan_date=loan_date,
                    status=PaymentStatus.get_status(status) if type(status) == str else status,
                    payment_date=payment_date,
                )
                if emp_id:
                    item = self.view.table_widget.item(row, 0)
                    item.setData(Qt.UserRole, emp_id)

            elif id_data != -1:
                self.update_existing_employee(
                    id_data,
                    name=name,
                    salary=salary,
                    amount_settled=amount_settled,
                    loan_from_salary=loan_from_salary,
                    loan_date=loan_date,
                    payment_date=payment_date,
                    status=PaymentStatus.get_status(status) if type(status) == str else status,
                )

    def add_new_employee(
            self, name, salary, amount_settled, loan_from_salary, loan_date, status, payment_date
    ):
        """Add a new employee to the database."""
        emp = Employee.add(
            name=name,
            salary=salary,
            amount_settled=amount_settled,
            loan_from_salary=loan_from_salary,
            loan_date=loan_date,
            payment_status=status,
            payment_date=payment_date,
        )
        if emp:
            return emp.id
        return False

    def update_existing_employee(
            self,
            employee_id,
            name,
            salary,
            amount_settled,
            loan_from_salary,
            loan_date,
            payment_date,
            status,
    ):
        Employee.update(
            {
                "id": employee_id,
                "name": name,
                "salary": salary,
                "loan_from_salary": loan_from_salary,
                "loan_date": loan_date,
                "payment_date": payment_date,
                "payment_status": status,
                "amount_settled": amount_settled
            }
        )

    def calculate_amount_paid(self, amount_settled, loan_from_salary):
        if not loan_from_salary:
            loan_from_salary = 0
        if amount_settled and loan_from_salary:
            return Decimal(amount_settled) + Decimal(loan_from_salary)
        return 0

    def calculate_remaining_salary(self, salary, loan_from_salary , amount_settled ):
        """Calculate remaining salary."""
        if salary and loan_from_salary:
            return Decimal(salary) - Decimal(loan_from_salary) - Decimal(amount_settled)
        return 0

    def on_item_changed(self, item: QTableWidgetItem):
        print("is removing rows ===> ", self.view.table_widget._is_removing_rows )
        # sip.isdeleted(self.view.table_widget)
        # self.view.table_widget.itemChanged.disconnect(self.on_item_changed)
        self.view.table_widget.blockSignals(True)
        string_columns = [1]
        value = item.text()
        item.setData(Qt.DisplayRole, value)
        if Qt.ItemIsEditable & item.flags():
            if item is not None:
                value = item.text()
                item.setData(Qt.DisplayRole, value)
                qdate = QDate.fromString(value, "yyyy-MM-dd")
                if value.isnumeric() and not item.data(Qt.UserRole) and item.column() not in string_columns:
                    item.setData(Qt.UserRole, Decimal(value))
                elif qdate.isValid():
                    item.setData(Qt.UserRole, qdate.toPyDate())
                else:
                    item.setData(Qt.UserRole, value)
                row = item.row()
                self.update_field_value(row)
                self.update_employee_data(row)

        self.view.table_widget.update_sums()
        # self.view.table_widget.itemChanged.connect(self.on_item_changed)
        self.view.table_widget.blockSignals(False)


    def update_field_value(self, row):
        """Update values in the table based on the current state."""
        salary = self.view.table_widget.item(row, 2)
        loan_from_salary = self.view.table_widget.item(row, 4)
        amount_settled = self.view.table_widget.item(row, 5)
        rem_from_salary = self.view.table_widget.item(row, 6)
        amount_paid = self.view.table_widget.item(row, 7)
        loan_date = self.view.table_widget.item(row, 8)
        payment_date = self.view.table_widget.item(row, 9)

        if salary and not salary.text():
            salary.setText("0")

        if loan_from_salary and not loan_from_salary.text():
            loan_from_salary.setText("0")

        if amount_settled and not amount_settled.text():
            amount_settled.setText("0")
            amount_settled.setData(Qt.UserRole , 0 )

        if loan_date and not loan_date:
            loan_date.setData(Qt.DisplayRole, str(datetime.date.today()))
            loan_date.setData(Qt.UserRole, datetime.date.today())
            loan_date.setText(str(datetime.date.today()))

        if payment_date and not payment_date:
            payment_date.setData(Qt.DisplayRole, str(datetime.date.today()))
            payment_date.setData(Qt.UserRole, datetime.date.today())
            payment_date.setData(str(datetime.date.today()))

        if self.check_fields([amount_settled, amount_paid, loan_from_salary]):
            paid_amount_result = str(
                self.calculate_amount_paid(
                    amount_settled.text(), loan_from_salary.text()
                )
            )
            amount_paid.setText(paid_amount_result)
            amount_paid.setData(Qt.UserRole, Decimal(paid_amount_result))

        if self.check_fields([rem_from_salary, salary]):
            rem_from_salary_result = str(
                self.calculate_remaining_salary(salary.text(), loan_from_salary.text() , amount_settled.text()  )
            )
            rem_from_salary.setText(rem_from_salary_result)
            rem_from_salary.setData(Qt.UserRole, Decimal(rem_from_salary_result))

    def on_cell_clicked(self, row, col):
        item = self.view.table_widget.item(row, col)
        if item:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def show(self) -> None:
        self.view.showMaximized()
        # self.view.show()

    def close(self) :
        self.view.close()
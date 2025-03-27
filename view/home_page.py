import asyncio
from typing import List

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRunnable
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QTabWidget,
    QHBoxLayout,
    QSplitter,
    QFrame, QMessageBox,
)

from controllers.company_owner_controller import CompanyOwnerController
from controllers.company_page_controller import CompanyWindowController
from controllers.freelancer_page_controller import FreeLancerWindowController
from models.constant import PaymentStatus, UserRoles
from models.employee import Employee
from utils.helpers import find_widget, load_stylesheet_from_resource
from utils.settings_manager import SettingManager
from view.ui.main_window import Ui_Form
from view.widgets.table_widget import TableWidget, DelegatesType
from view.widgets.text_edit_widget import TextEditWidget


class AsyncDBWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(Exception)

    def __init__(self, coro_fun):
        super().__init__()
        self.coro_fun = coro_fun

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.coro_fun)
            self.finished.emit(result)
        except Exception as e:
            QMessageBox.warning(None, "error", str(e))
            self.error.emit(e)
        finally:
            loop.close()




class MainWindow(QWidget):

    def __init__(self, controller=None, model=None):
        super().__init__()
        self.settings = SettingManager()
        self.controller = controller
        self.model = model
        self.setStyleSheet(load_stylesheet_from_resource())
        self.init_ui()

    def init_ui(self):
        # uifile = resource_path([os.path.dirname(__file__), "ui", "main_window.ui"])
        # uic.loadUi(uifile, self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("MoneyMaker")
        self.setWindowIcon(QIcon(":icons/icons/icon.png"))
        self.setup_table_widget()
        self.setup_tabs_and_layout()
        self.setup_controllers()



    def setup_table_widget(self ):
        columns = self.get_column_headers()
        rows  = self.get_employee_data()

        items = self.create_table_items(rows)
        print(rows)
        self.table_widget = TableWidget(
            rows=items, columns=columns, controller=self.controller , parent=self
        )
        self.table_widget.setReadOnlyColumns([6  , 7 ])
        self.table_widget.add_delegate(1, DelegatesType.StringDelegate)
        self.table_widget.add_delegate(2, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(4, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(5, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(6, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(7, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(3, DelegatesType.COMBOBOXPAYMENT)
        self.table_widget.add_delegate(8, DelegatesType.DATE_EDITOR)
        self.table_widget.add_delegate(9, DelegatesType.DATE_EDITOR)
        self.table_widget.add_rows(items)
        self.table_widget.itemChanged.connect(self.controller.on_item_changed)
        self.table_widget.setFrameShape(QFrame.StyledPanel)

    def setup_tabs_and_layout(self):
        self.tabWidget: QTabWidget = find_widget(self, QTabWidget, "tabWidget")
        self.tabWidget.setCurrentIndex(3)

        self.tab: QWidget = find_widget(self, QWidget, "tab_1")
        self.tab2: QWidget = find_widget(self, QWidget, "tab_3")
        self.hbox: QHBoxLayout = QHBoxLayout()
        self.splitter: QSplitter = QSplitter(Qt.Horizontal)

        self.textEdit = TextEditWidget(self)
        self.splitter.addWidget(self.textEdit)
        self.splitter.addWidget(self.table_widget)
        self.splitter.setSizes([100, 300])
        self.splitter.setStretchFactor(1, 1)

        self.hbox.addWidget(self.splitter)
        self.tab.setLayout(self.hbox)

    def setup_controllers(self):
        role = self.settings.get_value('current_role')
        if role and role != UserRoles.ADMIN:
            for user_role in UserRoles:
                if user_role != UserRoles.ADMIN and role != user_role:
                    widget = self.tabWidget.widget(user_role.value)
                    widget.deleteLater()

        else:
            print("user is admin..")
        self.company_tab = CompanyWindowController(self.tabWidget.widget(0))
        self.freelancer_tab = FreeLancerWindowController(self.tabWidget.widget(1))
        self.company_owner_tab = CompanyOwnerController(self.tabWidget.widget(2))


    def get_employee_data(self):
        return Employee.get_all()


    def get_column_headers(self, role=Qt.DisplayRole):
        if Qt.DisplayRole == role:
            return [
                "id",
                "اسم الموظف",
                "الراتب",
                "حالتة",
                "دين من الراتب",
                "المبلغ المسدد",
                "المبلغ المتبقي",
                "المبلغ المدفوع",
                "تاريخ المديونيه",
                "تاريخ السداد",
            ]
        elif Qt.UserRole:
            return [
                "name",
                "salary",
                "payment_status",
                "loan_from_salary",
                "amount_settled",
                "rem_from_salary",
                "amount_paid",
                "loan_date",
                "payment_date",
            ]

    def create_table_items(self , rows  : List[Employee] ):
        items = []
        for row in rows:
            row : Employee
            items.append(self.create_row_items(row))
        return items

    def create_row_items(self, row: Employee):
        if row :
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
                amount_settled,
                rem_from_salary,
                amount_paid,
                loan_date,
                payment_date,
            ]


    def create_table_item(self, for_display, for_edit):
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, for_display)
        item.setData(Qt.UserRole, for_edit)
        return item

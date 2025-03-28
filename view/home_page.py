from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QTabWidget,
    QHBoxLayout,
    QSplitter,
    QFrame, QVBoxLayout, QStackedWidget,
)
from pyqtspinner import WaitingSpinner

from controllers.company_owner_controller import CompanyOwnerController
from controllers.company_page_controller import CompanyWindowController
from controllers.freelancer_page_controller import FreeLancerWindowController
from models.constant import PaymentStatus, UserRoles
from models.employee import Employee
from utils.helpers import find_widget, load_stylesheet_from_resource
from utils.patterns.singletone import SingletonMixin
from utils.settings_manager import SettingManager
from view.ui.main_window import Ui_Form
from view.widgets.table_widget import TableWidget, DelegatesType
from view.widgets.text_edit_widget import TextEditWidget


class MainWindow(QWidget, SingletonMixin):
    _instance = None

    def __init__(self, controller=None, model=None):
        super().__init__()

        self.settings = SettingManager()
        self.controller = controller
        self.model = model
        self.setStyleSheet(load_stylesheet_from_resource())
        self.init_ui()

    def init_ui(self):
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("MoneyMaker")
        self.setWindowIcon(QIcon(":icons/icons/icon.png"))
        self.setup_table_widget()
        self._create_waiting_spinner()
        self._setup_stack_widget()
        self.setup_tabs_and_layout()
        self.setup_controllers()

    def update_items(self, result=None, error=None):
        print(len(result))
        if error:
            raise Exception("Error in Employee get_all function..")
        if len(result) >= 0:
            self.switch_window("table")
        rows = self.create_table_item_widgets(result)
        self.table_widget.setRowItems(rows)
        self.table_widget.add_rows()
        self.table_widget.update()

    def _create_waiting_spinner(self):
        self.spinner_widget = QWidget()
        # self.spinner_widget.setStyleSheet("background-color : red")
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.spinner_widget)
        self.spinner = WaitingSpinner(self.spinner_widget, color=QColor(105, 15, 117),
                                      disable_parent_when_spinning=False)
        self.spinner.start()

        self.setLayout(self.vbox)

    def _setup_stack_widget(self):
        self.stack_widget = QStackedWidget()
        self.stack_widget.addWidget(self.table_widget)
        self.stack_widget.addWidget(self.spinner_widget)
        self.switch_window("loading")

    def switch_window(self, window="loading"):
        if not self.stack_widget or not self.spinner_widget:
            raise Exception("Init Window widgets error")

        if window == "loading":
            self.stack_widget.setCurrentWidget(self.spinner_widget)
        elif window == "table":
            self.stack_widget.setCurrentWidget(self.table_widget)

    def setup_table_widget(self):

        columns = self.get_column_headers()

        self.table_widget = TableWidget(
            columns=columns, controller=self.controller, parent=self
        )

        self.table_widget.setReadOnlyColumns([6, 7])
        self.table_widget.add_delegate(1, DelegatesType.StringDelegate)
        self.table_widget.add_delegate(2, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(4, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(5, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(6, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(7, DelegatesType.NumericalDelegate)
        self.table_widget.add_delegate(3, DelegatesType.COMBOBOXPAYMENT)
        self.table_widget.add_delegate(8, DelegatesType.DATE_EDITOR)
        self.table_widget.add_delegate(9, DelegatesType.DATE_EDITOR)

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

        self.splitter.addWidget(self.stack_widget)
        self.splitter.setSizes([300, 300])
        self.splitter.setStretchFactor(1, 1)

        self.hbox.addWidget(self.splitter)
        self.tab.setLayout(self.hbox)
        self.update_table_data()

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

    def update_table_data(self):
        return Employee.get_all(callback=self.update_items)

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

    def create_table_item_widgets(self, rows: List[Employee]):
        items = []
        for row in rows:
            row: Employee
            emp_id = self.create_table_item_widget(str(row.id), row.id)
            name = self.create_table_item_widget(str(row.name), row.name)
            salary = self.create_table_item_widget(str(row.salary), row.salary)
            payment_status = self.create_table_item_widget(
                PaymentStatus.get_str(row.payment_status), row.payment_status
            )
            loan_from_salary = self.create_table_item_widget(
                str(row.loan_from_salary), row.loan_from_salary
            )

            rem_from_salary_cal = row.salary - row.loan_from_salary - row.amount_settled
            rem_from_salary = self.create_table_item_widget(
                str(rem_from_salary_cal), rem_from_salary_cal
            )
            amount_settled = self.create_table_item_widget(str(row.amount_settled), row.amount_settled)
            amount_paid_res = self.controller.calculate_amount_paid(row.amount_settled, row.loan_from_salary)
            amount_paid = self.create_table_item_widget(
                str(amount_paid_res), amount_paid_res
            )

            loan_date = self.create_table_item_widget(str(row.loan_date), row.loan_date)
            payment_date = self.create_table_item_widget(str(row.payment_date), row.payment_date)
            item = [
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
            items.append(item)

        return items

    def create_table_item_widget(self, for_display, for_edit):
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, for_display)
        item.setData(Qt.UserRole, for_edit)
        return item

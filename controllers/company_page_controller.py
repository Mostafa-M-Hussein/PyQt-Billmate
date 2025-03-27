import decimal
from decimal import Decimal

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QWidget
from _pydecimal import ROUND_HALF_UP
from decimal import Decimal, InvalidOperation

from controllers.base_controller import BaseController
from models.company_owner import Company
from view.company_page import CompanyWindow


class CompanyWindowController(BaseController):

    def __init__(self, parent):
        super().__init__()
        self.view: CompanyWindow = CompanyWindow(controller=self, widget=parent)
        self.table_widget: QWidget

    def update_field_value(self , row ):

        def format_decimal(value):
            return f"{value:.2f}"

        def get_numeric_data(item):
            if item is None:
                return Decimal(0)

            user_data = item.data(Qt.UserRole)
            if user_data:
                try:
                    value = Decimal(user_data)
                    return Decimal(value.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))
                except (TypeError, InvalidOperation):
                    pass

            if item.text().strip():
                try:
                    text_value = item.text().strip()
                    value = Decimal(text_value)
                    return Decimal(value.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))
                except (TypeError, InvalidOperation):
                    pass

            return Decimal(0)

        paid_amounts = self.view.table_widget.item(row  , 4 )
        loan_amounts = self.view.table_widget.item(row  , 2 )
        rem_amounts = self.view.table_widget.item(row, 5 )

        original_rem_amounts_value  = get_numeric_data(rem_amounts)
        original_paid_amounts_value  = get_numeric_data(paid_amounts)
        original_loan_amounts_value  = get_numeric_data(loan_amounts)

        rem_amounts_str = format_decimal(original_loan_amounts_value - original_paid_amounts_value )
        rem_amounts.setText(rem_amounts_str)
        rem_amounts.setData(Qt.DisplayRole, rem_amounts_str)
        rem_amounts.setData(Qt.UserRole, original_rem_amounts_value)

    def on_item_changed(self, item):
        self.view.table_widget.itemChanged.disconnect(self.on_item_changed)
        hidden_columns_type = [1]
        value = item.text()
        print(value)
        print(item.column())
        item.setData(Qt.DisplayRole, value)
        if item.column() not in hidden_columns_type:
            qdate = QDate.fromString(value, "yyyy-MM-dd")
            if value.isnumeric() and not item.data(Qt.UserRole):
                item.setData(Qt.UserRole, Decimal(value))
            elif qdate.isValid():
                item.setData(Qt.UserRole, qdate.toPyDate())
            else:
                item.setData(Qt.UserRole, value)
        row = item.row()
        self.update_field_value(row)
        self.update_or_add_company(row)
        self.view.table_widget.update_sums()
        self.view.table_widget.itemChanged.connect(self.on_item_changed)

    def update_or_add_company(self, row):
        print("Company Page im here")
        row_data = [
            self.view.table_widget.item(row, c).data(Qt.UserRole) if self.view.table_widget.item(row, c) else []
            for c in range(self.view.table_widget.columnCount())
        ]
        (
            id_data,
            shipping_company,
            loan_amount,
            date_of_debt,
            paid_amounts,
            rem_amounts ,
            note,
            monthly_payment_due_date,
        ) = row_data

        shipping_name  = self.view.table_widget.item(row, 1).data(Qt.DisplayRole) if self.view.table_widget.item(row , 1 )  else None
        shipping_percentage = self.view.table_widget.item(row, 1).data(Qt.UserRole) if self.view.table_widget.item(row , 1 )  else None

        if id_data is None or id_data == 0 :
            id_data = -1

        print("Id ==> " , id_data)
        if id_data == -1 and shipping_name and type(shipping_name) == str and len(shipping_name) > 0 :
            print("add new company")
            company_id = Company.add(
                shipping_name=shipping_name ,
                shipping_percentage=shipping_percentage,
                loan_amount=loan_amount,
                date_of_debt=date_of_debt,
                rem_amounts=rem_amounts ,
                paid_amounts=paid_amounts,
                note=str(note),
                monthly_payment_due_date=monthly_payment_due_date,
            )
            item = self.view.table_widget.item(row, 0)
            item.setData(Qt.UserRole, company_id)
        elif id_data != -1:
            print("update company")
            update_dict =   {
                    "id": id_data,
                    "loan_amount": loan_amount,
                    "date_of_debt": date_of_debt,
                    "paid_amounts": paid_amounts,
                    "rem_amounts" : rem_amounts ,
                    "note": str(note),
                    "monthly_payment_due_date": monthly_payment_due_date,
                }
            if shipping_name and shipping_percentage and len(shipping_name) > 0:
                print('added shipping ')
                update_dict["shippings"] = {
                    "name": shipping_name,
                    "percentage": shipping_percentage if decimal.Decimal(shipping_percentage) else 0

                }
            Company.update(
              update_dict
            )

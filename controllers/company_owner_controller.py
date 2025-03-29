import decimal
import pprint
from _pydecimal import ROUND_HALF_UP
from decimal import Decimal, InvalidOperation

from PyQt5 import sip
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QTableWidgetItem

from controllers.base_controller import BaseController
from models.company_owner import CompanyOwner
from models.constant import PaymentStatus, OrderStatus
from view.company_owner_page import CompanyOwnerWindow


class CompanyOwnerController(BaseController):
    def __init__(self, parent):
        super().__init__()
        self.view: CompanyOwnerWindow = CompanyOwnerWindow(
            controller=self, widget=parent
        )
        self.rows_data = {}

    def on_item_changed(self, item: QTableWidgetItem):
        if sip.isdeleted(self.view.table_widget):
            return
        print("item chamged")

        self.view.table_widget.blockSignals(True)
        # self.view.table_widget.itemChanged.disconnect(self.on_item_changed)
        hidden_columns_type = [6, 10, 7, 3 , 13 ]
        value = item.text()
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

        db_values = self.update_field_value(row, item.column())
        print(db_values)
        self.update_or_add_company(row, db_values)
        self.view.table_widget.update_sums()
        self.view.table_widget.blockSignals(False)

        # self.view.table_widget.itemChanged.connect(self.on_item_changed)

    def update_or_add_company(self, row, db_values):
        if sip.isdeleted(self.view.table_widget):
            print("update or add company hass been deleted...! ")
            return

        row_data = [
            self.view.table_widget.item(row, c).data(Qt.UserRole) if self.view.table_widget.item(row, c) else []
            for c in range(self.view.table_widget.columnCount())
        ]
        (
            id_data,
            payment_date,
            order_date,
            payment_status,
            total_profit,
            total_discount,
            retrieved_order,
            coupon_code,
            payment_method,
            total_demand,
            shipping_company,
            salla_total,
            cost,
            order_status,
            order_number,
            store_name,
        ) = row_data
        coupon_code = self.view.table_widget.item(row, 6).data(Qt.DisplayRole) if self.view.table_widget.item(row,
                                                                                                              6) else None
        coupon_discount = self.view.table_widget.item(row, 6).data(Qt.UserRole) if self.view.table_widget.item(row,
                                                                                                               6) else None

        shipping_name = self.view.table_widget.item(row, 10).data(Qt.DisplayRole) if self.view.table_widget.item(row,
                                                                                                                 10) else None
        shipping_percentage = self.view.table_widget.item(row, 10).data(Qt.UserRole) if self.view.table_widget.item(row,
                                                                                                                    10) else None

        payment_name = self.view.table_widget.item(row, 7).data(Qt.DisplayRole) if self.view.table_widget.item(row,
                                                                                                               7) else None
        payment_percentage = self.view.table_widget.item(row, 7).data(Qt.UserRole) if self.view.table_widget.item(row,
                                                                                                                  7) else None



        print("payment percentage is --> ", shipping_percentage)
        if id_data is None or id_data == 0:
            id_data = -1

        if id_data == -1 and store_name and len(str(store_name)) > 0:
            print('add new company ')
            company_id = CompanyOwner.add(
                store_name=str(store_name),
                order_number=str(order_number),
                order_status=OrderStatus.get_status(order_status) if type(order_status) == str else order_status,
                salla_total=salla_total,
                shipping_name=shipping_name,
                shipping_percentage=shipping_percentage,
                total_demand=total_demand,
                retrieved_order=retrieved_order ,
                payment_status=PaymentStatus.get_status(payment_status) if type(
                    payment_status) == str else payment_status,
                order_date=order_date,
                payment_date=payment_date,
                coupon_code=coupon_code,
                coupon_discount=coupon_discount,
                payment_name=payment_name,
                payment_percentage=payment_percentage,
                cost=cost,
                total_profit=db_values.get('total_gross_profit', Decimal(0)),
                total_discount=db_values.get('total_discount', Decimal(0)) ,
            callback = lambda  result , error : self.set_item_id( result , error  , row )


            )


        elif id_data != - 1:
            update_dict = {
                "id": id_data,
                "cost": cost,
                "salla_total": salla_total,
                "store_name": str(store_name),
                "order_number": str(order_number),
                "order_status": OrderStatus.get_status(order_status) if type(order_status) == str else order_status,
                "total_demand": total_demand,
                "total_discount": total_discount,
                "retrieved_order": retrieved_order,
                "payment_status": PaymentStatus.get_status(payment_status) if type(
                    payment_status) == str else payment_status,
                "order_date": order_date,
                "payment_date": payment_date,
            }

            if db_values.get('total_gross_profit', None) is not None:
                print("update total gross profit --> ", db_values.get('total_discount'))
                update_dict["total_profit"] = db_values['total_gross_profit']

            if db_values.get('total_discount', None) is not None:
                print("update total discount --> ", db_values.get('total_discount'))
                update_dict["total_discount"] = db_values['total_discount']

            if shipping_name and shipping_percentage and len(shipping_name) > 0:
                update_dict["shippings"] = {
                    "name": shipping_name,
                    "percentage": shipping_percentage if decimal.Decimal(shipping_percentage) else 0

                }
            if coupon_code and coupon_discount and len(coupon_code) > 0:
                update_dict["coupons"] = {
                    "code": coupon_code if coupon_code else "",
                    "discount": coupon_discount if decimal.Decimal(coupon_discount) else 0
                }

            if payment_name and payment_percentage and len(payment_name) > 0:
                update_dict["payments"] = {
                    "name": payment_name if payment_name else "",
                    "percentage": payment_percentage if decimal.Decimal(payment_percentage) else 0
                }

            CompanyOwner.update(
                updated=update_dict
            )

    def set_item_id(self , result , error  , row ):
        if error :
            raise  error
        item = self.view.table_widget.item(row, 0)
        item.setData(Qt.UserRole, result.id )
        item.setData(Qt.DisplayRole, result.id )

    def update_field_value(self, row, changed_column=None):
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

        def format_decimal(value):
            return f"{value:.2f}"

        # Get all table items
        discount_coupon = self.view.table_widget.item(row, 6)
        payment_method = self.view.table_widget.item(row, 7)
        shipping_company = self.view.table_widget.item(row, 10)
        total_discount = self.view.table_widget.item(row, 5)
        total_gross_profit = self.view.table_widget.item(row, 4)
        total_of_orders = self.view.table_widget.item(row, 8)
        reterived_order = self.view.table_widget.item(row, 9)
        salla_total = self.view.table_widget.item(row, 11)
        cost_of_order = self.view.table_widget.item(row, 12)

        if self.rows_data.get(row, None):
            current_row_data = self.rows_data.get(row)
            if current_row_data['payment'] == payment_method.text() and current_row_data[
                'coupon'] == discount_coupon.text() and payment_method and discount_coupon:
                current_row_data['total_discount_value_pre_calculated'] = False
            else:
                current_row_data['total_discount_value_pre_calculated'] = True
        else:
            self.rows_data = {
                row: {
                    "salla_total_discount": Decimal(0),
                    "total_of_orders_discount": Decimal(0),
                    "coupon": '',
                    "payment": '',
                    "shipping": '',
                    'total_discount_value_pre_calculated': False,
                    'total_discount_value': Decimal(0),
                    'total_gross_profit': Decimal(0)

                }
            }


        original_discount_coupon_percentage = get_numeric_data(discount_coupon)
        original_payment_method_percentage = get_numeric_data(payment_method)
        original_shipping_value = get_numeric_data(shipping_company)
        original_total_of_orders_value = get_numeric_data(total_of_orders)
        original_salla_total_value = get_numeric_data(salla_total)
        original_cost_of_order_value = get_numeric_data(cost_of_order)
        # original_reterived_order_value = get_numeric_data(reterived_order)



        order_status = self.view.table_widget.item(row , 13 )
        order_status_enum  = order_status.data(Qt.UserRole)
        if len(order_status.text()) > 0  :
            if order_status_enum is OrderStatus.REFUSED :
                reterived_order_str = format_decimal(original_salla_total_value)
                reterived_order.setText(reterived_order_str)
                reterived_order.setData(Qt.DisplayRole, reterived_order_str)
                reterived_order.setData(Qt.UserRole,  original_salla_total_value )
            else :
                reterived_order_str = format_decimal(0)
                reterived_order.setText(reterived_order_str)
                reterived_order.setData(Qt.DisplayRole, "0")
                reterived_order.setData(Qt.UserRole, 0)




        db_values = {}

        revenue = original_total_of_orders_value - (
                original_payment_method_percentage / 100 * original_total_of_orders_value)
        total_of_orders_discount = original_total_of_orders_value - revenue
        if self.rows_data[row]['total_of_orders_discount'] != discount_coupon.text() or self.rows_data[row][
            'total_of_orders_discount'] <= 0:
            print("setting payment discount value")
            self.rows_data[row]['payment'] = discount_coupon.text()
            self.rows_data[row]['total_of_orders_discount'] = total_of_orders_discount
            self.rows_data[row]['total_discount_value_pre_calculated'] = False

        salla_total_after_discount = original_salla_total_value - (
                (original_discount_coupon_percentage / 100) * original_salla_total_value)

        salla_total_discount = original_salla_total_value - salla_total_after_discount
        if self.rows_data[row]['coupon'] != discount_coupon.text() or self.rows_data[row][
            'salla_total_discount'] <= 0:
            print("setting coupon discount value")
            print(salla_total_discount)
            self.rows_data[row]['coupon'] = discount_coupon.text()
            self.rows_data[row]['salla_total_discount'] = salla_total_discount
            self.rows_data[row]['total_discount_value_pre_calculated'] = False

        formatted_value = format_decimal(original_salla_total_value)
        salla_total.setText(formatted_value)
        salla_total.setData(Qt.DisplayRole, formatted_value)

        salla_total_with_shipping = original_salla_total_value + original_shipping_value
        formatted_value = format_decimal(salla_total_with_shipping)
        total_of_orders.setText(formatted_value)
        total_of_orders.setData(Qt.DisplayRole, formatted_value)
        total_of_orders.setData(Qt.UserRole, salla_total_with_shipping)




        # db_values['salla_total_without_shipping'] = salla_total_without_shipping
        # db_values['salla_total_after_discount'] = salla_total_after_discount

        if self.rows_data[row]['total_discount_value_pre_calculated'] is False:
            total_discount_value = self.rows_data[row]['salla_total_discount'] + self.rows_data[row][
                'total_of_orders_discount']
            total_discount_formatted = format_decimal(total_discount_value)
            total_discount.setText(total_discount_formatted)
            total_discount.setData(Qt.DisplayRole, total_discount_formatted)
            total_discount.setData(Qt.UserRole, total_discount_value)
            self.rows_data[row]['total_discount_value'] = total_discount_value

        total_revenue = original_salla_total_value - (
                original_cost_of_order_value + self.rows_data[row]['total_discount_value'])

        total_revenue = -total_revenue if  order_status_enum is OrderStatus.REFUSED else total_revenue
        total_revenue_formatted = format_decimal( total_revenue   )
        total_gross_profit.setText(total_revenue_formatted)
        total_gross_profit.setData(Qt.DisplayRole, total_revenue_formatted)
        total_gross_profit.setData(Qt.UserRole, total_revenue)

        db_values['total_gross_profit'] = total_revenue
        db_values['total_discount'] = self.rows_data[row]['total_discount_value']
        return db_values

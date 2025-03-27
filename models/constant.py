from enum import Enum as PyEnum


class PaymentStatus(PyEnum):
    PENDING = 1
    COMPLETED = 2
    REFUSED = 3

    @staticmethod
    def get_str(status):
        if status == PaymentStatus.PENDING:
            return "قيد السداد"
        elif status == PaymentStatus.COMPLETED:
            return "تم السداد"
        elif status == PaymentStatus.REFUSED:
            return "لم يسدد"
        return None

    @staticmethod
    def get_status(str):
        if str == "قيد السداد":
            return PaymentStatus.PENDING
        elif str == "تم السداد":
            return PaymentStatus.COMPLETED
        elif str == "لم يسدد":
            return PaymentStatus.REFUSED
        return None


class OrderStatus(PyEnum):
    PENDING = 1
    COMPLETED = 2
    REFUSED = 3

    @staticmethod
    def get_str(status):
        if status == OrderStatus.PENDING:
            return "بأنتظار المراجعة"
        elif status == OrderStatus.COMPLETED:
            return "تم التوصيل"
        elif status == OrderStatus.REFUSED:
            return "مسترجع"
        return None

    @staticmethod
    def get_status(str):
        if str == "بأنتظار المراجعة":
            return OrderStatus.PENDING
        elif str == "تم التوصيل":
            return OrderStatus.COMPLETED
        elif str == "مسترجع":
            return OrderStatus.REFUSED
        return None


class UserRoles(PyEnum):
    COMPANY = 0
    FREELANCE = 1
    COMPANY_OWNER = 2
    EMPLOYEE = 3
    ADMIN = 4

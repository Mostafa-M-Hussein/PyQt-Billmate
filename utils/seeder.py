import random
import time

from faker import Faker

from models.company_owner import CompanyOwner, Company
from models.constant import OrderStatus, UserRoles
from models.employee import Employee, PaymentStatus
from models.freelancer import FreeLancer
from models.user import User

faker = Faker()


def seed_users():
    users_role = [user for user in UserRoles]
    print(users_role)
    # User.add(name="zaid@gmail.com", password="zaid12345@", role=users_role[4])
    # User.add(name="Alamritime@gmail.com", password="Money1234567", role=users_role[4])
    # User.add(name="alamritime1@gmail.com", password="money123@", role=users_role[2])
    User.add(name="alamritime3@gmail.com", password="money321@", role=users_role[2] )
    # User.add(name="alamritime2@gmail.com", password="money123456@", role=users_role[2])


def seed(fake_number):

    for _ in range(fake_number):
        Employee.add(
            faker.name(),
            faker.pydecimal(right_digits=2, left_digits=5),
            loan_from_salary=faker.pydecimal(right_digits=2, left_digits=5),
            loan_date=faker.date_object(),
            payment_date=faker.date_object(),
            amount_settled=faker.pydecimal(2, 2, True),
            payment_status=random.choice(
                [PaymentStatus.PENDING, PaymentStatus.COMPLETED]
            ),
        )

        Company.add(
            shipping_name=faker.company(),
            shipping_percentage=faker.pydecimal(2, 4, True),
            loan_amount=faker.pydecimal(2, 4),
            rem_amounts=faker.pydecimal(2, 4),
            date_of_debt=faker.date_object(),
            paid_amounts=faker.pydecimal(2, 4),
            note=faker.text(),
            monthly_payment_due_date=faker.date_object(),
        )

        FreeLancer.add(
            note=faker.text(),
            amount=faker.pydecimal(2, 4),
            other_costs=faker.company(),
            date=faker.date_object(),
        )

        CompanyOwner.add(
            store_name=faker.name(),
            order_number=faker.phone_number(),
            order_status=random.choice([OrderStatus.PENDING, OrderStatus.COMPLETED]),
            salla_total=faker.pydecimal(2, 4, True),
            total_demand=faker.pydecimal(2, 4, True),
            payment_name=faker.company(),
            payment_percentage=faker.pydecimal(2, 4, True),
            coupon_code=str(faker.name()),
            coupon_discount=faker.pydecimal(2, 4),
            total_discount=faker.pydecimal(2, 4),
            total_profit=faker.pydecimal(2, 4),
            payment_status=random.choice(
                [PaymentStatus.PENDING, PaymentStatus.COMPLETED]
            ),
            order_date=faker.date_object(),
            payment_date=faker.date_object(),
            shipping_name=faker.company(),
            shipping_percentage=faker.pydecimal(2, 4, True),
            cost=faker.pydecimal(2, 4, True),
            retrieved_order=faker.pydecimal(2, 4),
        )


# ensure_tables()
# seed(5)

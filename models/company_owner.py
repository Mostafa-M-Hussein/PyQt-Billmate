import datetime
import decimal
from typing import Dict

from sqlalchemy import (
    String,
    Integer,
    Column,
    DECIMAL,
    DateTime,
    Date,
    select,
    Enum as SqlEnum, ForeignKey
)
from sqlalchemy.orm import relationship, selectinload, joinedload
from sqlalchemy.sql import func

from models import Base, get_session
from models.constant import PaymentStatus, OrderStatus
from utils.logger.logger import setup_logger

logger = setup_logger("employee_model", "logs/models.log")

from models.alchemy import DynamicSearch


class Coupon(Base, DynamicSearch):
    __tablename__ = 'coupons'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    code = Column(String(250), nullable=True, unique=True)
    discount = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=func.now())
    company_owners = relationship("CompanyOwner", back_populates="coupons")

    @staticmethod
    def get(code: str):
        with get_session() as session:
            try:
                stmt = select(Coupon).where(Coupon.code == code)
                result = session.execute(stmt)
                shipping_company = result.scalars().first()
                if shipping_company:
                    session.refresh(shipping_company)

                return shipping_company
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)
                return None

    @staticmethod
    def add(
            code: str,
            discount: decimal.Decimal,

    ):
        with get_session() as session:
            try:
                print("add new company")
                if len(code) > 0 and discount:
                    coupon = Coupon(
                        code=code,
                        discount=discount,

                    )
                    session.add(coupon)
                    session.commit()
                    # session.refresh(coupon)
                    return coupon.id
                return False
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)
                return False

    @staticmethod
    def update(coupon_update: dict):
        with get_session() as session:
            print(f"coupon update  data in {coupon_update}")
            try:
                stmt = select(Coupon).where(Coupon.id == coupon_update["id"])
                result = session.execute(stmt)
                old = result.scalars().first()
                if not old:
                    logger.debug(f"Event with ID {old} not found.")
                    return False
                valid_keys = set(
                    column
                    for column in coupon_update.keys()
                    if column in Coupon.__table__.columns
                )
                for key in coupon_update.keys():
                    if key not in valid_keys:
                        logger.debug(f"Invalid attribute '{key}' for Event model.")
                        raise AttributeError(f"Event has no attribute '{key}'")

                for key, value in coupon_update.items():
                    setattr(old, key, value)
                print(old)
                session.commit()
                session.refresh(old)
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    @staticmethod
    def get_all():
        with get_session() as session:
            try:
                stmt = select(Coupon).order_by(Coupon.created_at)
                result = session.execute(stmt)
                owners = result.scalars().all()
                for owner in owners:
                    session.refresh(owner)
                return owners
            except Exception as e:
                logger.error(e, exc_info=True)

    @staticmethod
    def remove(code: str):
        with get_session() as session:
            try:
                emp = Coupon.get(code)
                session.delete(emp)
                session.commit()

            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    def search(self, column, value):
        with get_session() as session:
            return self.where(column, value, session)


class ShippingCompany(Base):
    __tablename__ = "shipping_company"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=True, unique=True)
    percentage = Column(DECIMAL(10, 2), default=0)
    company_owners = relationship("CompanyOwner", back_populates="shippings")
    companys = relationship("Company", back_populates="shippings")
    created_at = Column(DateTime, default=func.now())

    @staticmethod
    def get(name: str):
        with get_session() as session:
            try:
                stmt = select(ShippingCompany).where(ShippingCompany.name == name)
                result = session.execute(stmt)
                shipping_company = result.scalars().first()
                if shipping_company:
                    session.refresh(shipping_company)
                return shipping_company
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)
                return None

    @staticmethod
    def add(
            name: str,
            percentage: decimal.Decimal,

    ):
        with get_session() as session:
            try:
                print("add new company")
                if len(name) > 0 and percentage:
                    shipping = ShippingCompany(
                        name=name,
                        percentage=percentage,

                    )
                    session.add(shipping)
                    session.commit()
                    # session.refresh(coupon)
                    return shipping.id
                return False
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)
                return False

    @staticmethod
    def update(shipping_update: dict):
        with get_session() as session:
            print(f"shipping  update  data in {shipping_update}")
            try:
                stmt = select(Coupon).where(Coupon.id == shipping_update["id"])
                result = session.execute(stmt)
                old = result.scalars().first()
                if not old:
                    logger.debug(f"Event with ID {old} not found.")
                    return False
                valid_keys = set(
                    column
                    for column in shipping_update.keys()
                    if column in Coupon.__table__.columns
                )
                for key in shipping_update.keys():
                    if key not in valid_keys:
                        logger.debug(f"Invalid attribute '{key}' for Event model.")
                        raise AttributeError(f"Event has no attribute '{key}'")

                for key, value in shipping_update.items():
                    setattr(old, key, value)
                print(old)
                session.commit()
                session.refresh(old)
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    @staticmethod
    def get_all():
        with get_session() as session:
            try:
                stmt = select(ShippingCompany).order_by(ShippingCompany.created_at)
                result = session.execute(stmt)
                owners = result.scalars().all()
                for owner in owners:
                    session.refresh(owner)
                return owners
            except Exception as e:
                logger.error(e, exc_info=True)

    @staticmethod
    def remove(id: str):
        with get_session() as session:

            try:
                emp = ShippingCompany.get(id)
                session.delete(emp)
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=True, unique=True)
    percentage = Column(DECIMAL(10, 2), default=0)
    company_owners = relationship("CompanyOwner", back_populates="payments")
    created_at = Column(DateTime, default=func.now())

    @staticmethod
    def get(name: str):
        with get_session() as session:
            try:
                stmt = select(Payment).where(Payment.name == name)
                result = session.execute(stmt)
                shipping_company = result.scalars().first()
                if shipping_company:
                    session.refresh(shipping_company)
                return shipping_company
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    @staticmethod
    def add(
            name: str,
            percentage: decimal.Decimal,

    ):
        with get_session() as session:
            try:
                print("add new company")
                if len(name) > 0 and percentage:
                    shipping = Payment(
                        name=name,
                        percentage=percentage,

                    )
                    session.add(shipping)
                    session.commit()
                    # session.refresh(coupon)
                    return shipping.id
                return False
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)
                return False

    @staticmethod
    def update(payment_update: dict):
        with get_session() as session:
            print(f"shipping  update  data in {payment_update}")
            try:
                stmt = select(Payment).where(Payment.id == payment_update["id"])
                result = session.execute(stmt)
                old = result.scalars().first()
                if not old:
                    logger.debug(f"Event with ID {old} not found.")
                    return False
                valid_keys = set(
                    column
                    for column in payment_update.keys()
                    if column in Coupon.__table__.columns
                )
                for key in payment_update.keys():
                    if key not in valid_keys:
                        logger.debug(f"Invalid attribute '{key}' for Event model.")
                        raise AttributeError(f"Event has no attribute '{key}'")

                for key, value in payment_update.items():
                    setattr(old, key, value)
                print(old)
                session.commit()
                session.refresh(old)
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    @staticmethod
    def get_all():
        with get_session() as session:

            try:
                stmt = select(Payment).order_by(Payment.created_at)
                result = session.execute(stmt)
                owners = result.scalars().all()
                for owner in owners:
                    session.refresh(owner)
                return owners
            except Exception as e:
                logger.error(e, exc_info=True)

    @staticmethod
    def remove(id: str):
        with get_session() as session:

            try:
                emp = Payment.get(id)
                session.delete(emp)
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)


class CompanyOwner(Base, DynamicSearch):
    __tablename__ = "company_owner"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_name = Column(String(250), nullable=False)
    order_number = Column(String(250), nullable=True, default=0)
    order_status = Column(
        SqlEnum(OrderStatus), default=OrderStatus.PENDING, nullable=True
    )
    salla_total = Column(DECIMAL(10, 2), nullable=True, default=0)
    cost = Column(DECIMAL(10, 2), nullable=True, default=0)
    total_demand = Column(DECIMAL(10, 2), nullable=True, default=0)
    total_profit = Column(DECIMAL(10, 2), nullable=True, default=0)
    total_discount = Column(DECIMAL(10, 2), nullable=True, default=0)
    payment_status = Column(
        SqlEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=True
    )
    retrieved_order = Column(DECIMAL(10 , 2 ) , nullable = True , default = 0 )
    order_date = Column(Date, nullable=True)
    payment_date = Column(Date)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    coupons_id = Column(Integer, ForeignKey("coupons.id"), nullable=True)
    shipping_id = Column(Integer, ForeignKey("shipping_company.id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)

    coupons = relationship("Coupon", back_populates="company_owners")
    shippings = relationship("ShippingCompany", back_populates="company_owners")
    payments = relationship("Payment", back_populates="company_owners")

    @staticmethod
    def get(id: str):
        with get_session() as session:
            try:
                stmt = select(CompanyOwner).where(CompanyOwner.id == id)
                result = session.execute(stmt)
                owner = result.scalars().first()
                # session.refresh(owner)
                return owner
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    @staticmethod
    def add(
            store_name: str,
            order_number: str,
            cost: decimal.Decimal,
            order_status: OrderStatus,
            salla_total: decimal.Decimal,
            total_demand: decimal.Decimal,
            retrieved_order: decimal.Decimal,
            total_profit: decimal.Decimal,
            total_discount: decimal.Decimal,
            payment_status: PaymentStatus,
            order_date: datetime.date,
            payment_date: datetime.date,
            coupon_code: str = None,
            coupon_discount: decimal.Decimal = None,
            shipping_name: str = None,
            shipping_percentage: decimal.Decimal = None,
            payment_name: str = None,
            payment_percentage: decimal.Decimal = None,
    ):
        with get_session() as session:
            try:
                coupon_id = None
                shipping_id = None
                payment_id = None
                if coupon_code:
                    coupon = Coupon.get(code=coupon_code)
                    if coupon:
                        print("using existsing coupon ")
                        coupon_id = coupon.id
                        print("coupon_code id in db is ==> ", coupon_code)
                    else:
                        coupon = Coupon.add(code=coupon_code, discount=coupon_discount)
                        session.flush()
                        coupon_id = coupon

                if shipping_name:
                    shipping = ShippingCompany.get(name=shipping_name)
                    if shipping:
                        print("using existsing shipping id ")
                        shipping_id = shipping.id
                    else:
                        shipping = ShippingCompany.add(name=shipping_name, percentage=shipping_percentage)
                        session.flush()
                        shipping_id = shipping

                if payment_name:
                    payment = Payment.get(name=payment_name)
                    if payment:
                        print("using existing payment id ")
                        payment_id = payment.id
                    else:
                        payment = Payment.add(name=payment_name, percentage=payment_percentage)
                        session.flush()
                        payment_id = payment

                company = CompanyOwner(
                    store_name=store_name,
                    order_number=order_number,
                    order_status=OrderStatus.get_status(order_status),
                    salla_total=salla_total,
                    total_profit=total_profit,
                    total_discount=total_discount,
                    total_demand=total_demand,
                    payment_id=payment_id,
                    payment_status=PaymentStatus.get_status(payment_status),
                    order_date=order_date,
                    payment_date=payment_date,
                    retrieved_order= retrieved_order ,
                    coupons_id=coupon_id,
                    shipping_id=shipping_id,
                    cost=cost,
                )
                session.add(company)
                session.commit()
                return company.id
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)
                return False
            finally:
                session.close()

    @staticmethod
    def update(updated: Dict):
        with get_session() as session:

            """
            Update a CompanyOwner instance and its relationships.
    
            Args:
                updated (Dict): Dictionary containing fields to update
    
            Returns:
                Union[bool, CompanyOwner]: Updated CompanyOwner instance or False if failed
            """
            try:
                # Query with eager loading of relationships
                stmt = (
                    select(CompanyOwner)
                    .where(CompanyOwner.id == updated["id"])
                    .options(
                        joinedload(CompanyOwner.payments),
                        joinedload(CompanyOwner.shippings),
                        joinedload(CompanyOwner.coupons)
                    )
                )

                result = session.execute(stmt)
                old = result.unique().scalars().first()

                if not old:
                    print(f"CompanyOwner with ID {updated['id']} not found.")
                    return False

                # Get valid column keys
                valid_keys = set(column.key for column in CompanyOwner.__table__.columns)

                # Handle Payments Update
                if 'payments' in updated:
                    payment_data = updated['payments']

                    payment = None
                    if payment_data.get('name'):
                        # Try to get existing payment
                        payment = Payment.get(payment_data['name'])
                        if payment:
                            old.payment_id = payment.id
                        else:
                            # Create new payment
                            new_payment = Payment.add(
                                name=payment_data['name'],
                                percentage=payment_data['percentage']
                            )
                            session.flush()  # Ensure ID is generated
                            old.payment_id = new_payment

                # Handle Shipping Update
                if 'shippings' in updated:
                    shipping_data = updated['shippings']

                    shipping = None
                    if shipping_data.get('name'):
                        # Try to get existing shipping using corrected get method
                        shipping = ShippingCompany.get(shipping_data['name'])
                        if shipping:
                            old.shipping_id = shipping.id
                        else:
                            # Create new shipping if it doesn't exist
                            new_shipping_id = ShippingCompany.add(
                                name=shipping_data['name'],
                                percentage=shipping_data['percentage']
                            )
                            if new_shipping_id:
                                old.shipping_id = new_shipping_id
                            else:
                                print("Failed to add new shipping company")
                                raise ValueError("Failed to add shipping company")

                # Handle Coupon Update
                if 'coupons' in updated:
                    coupon_data = updated['coupons']
                    coupon = None
                    if coupon_data.get('code'):
                        # Try to get existing coupon
                        coupon = Coupon.get(code=coupon_data['code'])
                        print("found old code ==> ", coupon)
                        if coupon:
                            print("linked it")
                            old.coupons_id = coupon.id
                        else:
                            # Create new coupon
                            new_coupon = Coupon.add(
                                code=coupon_data['code'],
                                discount=coupon_data['discount']
                            )
                            session.flush()  # Ensure ID is generated
                            old.coupons_id = new_coupon

                # Validate and update other fields
                for key in updated.keys():
                    if key not in valid_keys and key not in ["payments", "shippings", "coupons"]:
                        raise AttributeError(f"CompanyOwner has no attribute '{key}'")

                # Update regular fields
                for key, value in updated.items():
                    if value is not None:
                        if key not in ["payments", "shippings", "coupons"]:
                            setattr(old, key, value)

                # Commit changes
                session.commit()
                session.refresh(old)

                # Verify relationships after refresh
                # if 'payments' in updated:
                #     assert old.payments is not None, "Payment relationship not properly loaded"

                return old

            except Exception as e:
                session.rollback()
                print(f"Error updating CompanyOwner: {str(e)}")
                raise

            finally:
                session.close()

    @staticmethod
    def get_all():
        with get_session() as session:

            try:
                # Create the query with joinedload for the coupons relationship
                stmt = (
                    select(CompanyOwner)
                    .options(selectinload(CompanyOwner.coupons), selectinload(CompanyOwner.shippings),
                             selectinload(CompanyOwner.payments))  # Eager load coupons
                    .order_by(CompanyOwner.created_at)  # Order by creation date
                )
                # Execute the query and fetch all results
                result = session.execute(stmt)
                owners = result.scalars().all()  # Use .unique() to avoid duplicates
                return owners
            except Exception as e:
                logger.error(e, exc_info=True)  # Log the error
                return []
            finally:
                session.close()

    @staticmethod
    def remove(id: str):
        with get_session() as session:

            try:
                emp = CompanyOwner.get(id)
                if emp is None:
                    logger.debug("Empty  Companyowner ")
                    return False
                session.delete(emp)
                session.commit()
                # session.refresh(emp)
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    def search(self, column, value):
        with get_session() as session:
            return self.where(column, value, session)





class Company(Base, DynamicSearch):
    __tablename__ = "companys"
    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_amount = Column(DECIMAL(10, 2), nullable=True, default=0)
    date_of_debt = Column(Date, nullable=True, default=datetime.date.today)
    paid_amounts = Column(DECIMAL(10, 2), nullable=True, default=0)
    rem_amounts = Column(DECIMAL(10, 2), nullable=True, default=0)
    note = Column(String(250), nullable=True)
    monthly_payment_due_date = Column(Date)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    shipping_id = Column(Integer, ForeignKey("shipping_company.id"), nullable=True)
    shippings = relationship("ShippingCompany", back_populates="companys")

    @staticmethod
    def get(id: str):
        with get_session() as session:
            try:
                stmt = (
                    select(Company)
                    .where(Company.id == id)
                    .options(joinedload(Company.shippings))  # Ensures shippings is loaded immediately
                )
                result = session.execute(stmt)
                company = result.scalars().first()
                if company:
                    return company
                return None
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)


    @staticmethod
    def add(
            loan_amount: decimal.Decimal,
            date_of_debt: datetime.date,
            paid_amounts: decimal.Decimal,
            rem_amounts : decimal.Decimal ,
            note: str,
            monthly_payment_due_date: datetime.date,
            shipping_name: str = None,
            shipping_percentage: decimal.Decimal = None,
    ):
        with get_session() as session:
            try:
                shipping_id = None
                if shipping_name:
                    shipping = ShippingCompany.get(shipping_name)
                    if shipping:
                        print("Using existing shipping company")
                        shipping_id = shipping.id
                    else:
                        if shipping_percentage is None:
                            raise ValueError("shipping_percentage is required when creating a new shipping company")
                        new_shipping = ShippingCompany.add(
                            name=shipping_name,
                            percentage=shipping_percentage
                        )
                        session.flush()  # Ensure the shipping company has an ID
                        shipping_id = new_shipping
                        print("Added new shipping company")

                    # Create new company
                company = Company(
                    loan_amount=loan_amount,
                    date_of_debt=date_of_debt,
                    paid_amounts=paid_amounts,
                    rem_amounts=rem_amounts ,
                    note=note,
                    monthly_payment_due_date=monthly_payment_due_date,
                    shipping_id=shipping_id,

                )
                session.add(company)
                session.commit()
                session.refresh(company)
                return company.id


            except Exception as e:
                session.rollback()
                raise Exception(f"Error adding company: {str(e)}")

    @staticmethod
    def update(updated: dict):
        with get_session() as session:
            try:
                stmt = select(Company).where(Company.id == updated["id"]).options(joinedload(Company.shippings))
                result = session.execute(stmt)
                old = result.unique().scalars().first()
                if not old:
                    logger.debug(f"Event with ID {old} not found.")
                    return False

                if 'shippings' in updated:
                    shipping_data = updated['shippings']

                    shipping = None
                    if shipping_data.get('name'):
                        # Try to get existing shipping using corrected get method
                        shipping = ShippingCompany.get(shipping_data['name'])
                        if shipping:
                            old.shipping_id = shipping.id
                        else:
                            # Create new shipping if it doesn't exist
                            new_shipping_id = ShippingCompany.add(
                                name=shipping_data['name'],
                                percentage=shipping_data['percentage']
                            )
                            if new_shipping_id:
                                old.shipping_id = new_shipping_id
                            else:
                                print("Failed to add new shipping company")
                                raise ValueError("Failed to add shipping company")

                valid_keys = set(
                    column
                    for column in updated.keys()
                    if column in Company.__table__.columns
                )
                for key in updated.keys():
                    if key not in valid_keys and key not in ["shippings"]:
                        logger.debug(f"Invalid attribute '{key}' for Event model.")
                        raise AttributeError(f"Event has no attribute '{key}'")

                for key, value in updated.items():
                    if key not in ["shippings"]:
                        setattr(old, key, value)

                session.commit()
                session.refresh(old)
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    @staticmethod
    def get_all():
        with get_session() as session:
            try:
                stmt = select(Company).order_by(Company.created_at).options(selectinload(Company.shippings))
                result = session.execute(stmt)
                companys = result.scalars().all()
                for company in companys:
                    session.refresh(company)
                return companys
            except Exception as e:
                logger.error(e, exc_info=True)

    @staticmethod
    def remove(id: str):
        with get_session() as session:
            try:
                emp = Company.get(id)

                session.delete(emp)
                session.commit()
                # session.refresh(emp)
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    def search(self, column, value):
        with get_session() as session:
            return self.where(column, value, session)



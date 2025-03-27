import datetime
import decimal

from sqlalchemy import (
    String,
    Integer,
    Column,
    DECIMAL,
    Enum as Sqlenum,
    DateTime,
    Date,
    select,
    Index
)
from sqlalchemy.sql import func

from models import Base, get_session, run_in_thread
from models.alchemy import DynamicSearch
from models.constant import PaymentStatus
from utils.logger.logger import setup_logger

logger = setup_logger("employee_model", "logs/models.log")


class Employee(Base, DynamicSearch):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    salary = Column(DECIMAL(10, 2), nullable=False, default=0)
    loan_from_salary = Column(DECIMAL(10, 2), default=0, nullable=True)
    amount_settled = Column(DECIMAL(10, 2), default=0, nullable=True)
    loan_date = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=True)
    payment_status = Column(
        Sqlenum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING
    )
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    __table_args__ = (
        Index('idx_employee_name', 'name'),
        Index('idx_employee_payment_status', 'payment_status'),
        Index('idx_employee_payment_date', 'payment_date'),
        Index('idx_employee_created_at', 'created_at'),
    )

    @staticmethod
    @run_in_thread
    def get(id: str):
        with get_session() as session:
            try:
                stmt = select(Employee).where(Employee.id == id)
                result = session.execute(stmt)
                session.refresh(session)
                return result.scalars().first()
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    @staticmethod
    def add(
            name: str,
            salary: decimal.Decimal,
            loan_from_salary: decimal.Decimal,
            amount_settled: decimal.Decimal,
            loan_date: datetime.date,
            payment_date: datetime.date,
            payment_status: PaymentStatus,
    ):
        with get_session() as session:
            try:
                employee = Employee(
                    name=name,
                    salary=salary,
                    amount_settled=amount_settled,
                    loan_from_salary=loan_from_salary,
                    loan_date=loan_date,
                    payment_date=payment_date,
                    payment_status=PaymentStatus.get_status(payment_status),
                )
                session.add(employee)
                session.commit()
                session.refresh(employee)
                return employee
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)
                return False
            finally:
                session.close()

    @staticmethod
    def update(updated_employee: dict):
        with get_session() as session:
            try:
                stmt = select(Employee).where(Employee.id == updated_employee["id"])
                result = session.execute(stmt)
                old_emp = result.scalars().first()
                logger.debug(f"old emp {old_emp} ")
                if not old_emp:
                    logger.debug(f"Event with ID {old_emp} not found.")
                    return False
                valid_keys = set(
                    column
                    for column in updated_employee.keys()
                    if column in Employee.__table__.columns
                )
                print(valid_keys)
                for key in updated_employee.keys():
                    if key not in valid_keys:
                        logger.debug(f"Invalid attribute '{key}' for Event model.")
                        raise AttributeError(f"Event has no attribute '{key}'")

                for key, value in updated_employee.items():
                    setattr(old_emp, key, value)

                for col_name, column in Employee.__table__.columns.items():
                    if getattr(old_emp, col_name) is None and column.default is not None:
                        default_value = column.default.arg
                        if callable(default_value):
                            default_value = default_value()
                        setattr(old_emp, col_name, default_value)
                print(old_emp)
                logger.debug("updated sucessfully..")
                session.commit()
                session.refresh(old_emp)
            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)
            finally:
                session.close()

    @run_in_thread
    @staticmethod
    def get_all(session):
        try:
            stmt = select(Employee).order_by(Employee.created_at)
            result = session.execute(stmt)
            employees = result.scalars().all()
            for employee in employees:
                session.refresh(employee)
            return employees
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def get_column(column_name):
        with get_session() as session:
            try:
                column = getattr(Employee, column_name)
                stmt = column(Employee.payment_status).order_by(Employee.created_at)
                result = session.execute(stmt)
                all_employees = result.scalars().all()
                return all_employees
            except Exception as e:
                logger.error(e, exc_info=True)

    @staticmethod
    def remove(id: str):
        with get_session() as session:
            try:
                emp = Employee.get(id)
                session.delete(emp)
                session.commit()

            except Exception as e:
                session.rollback()
                logger.error(e, exc_info=True)

    def search(self, column, value, operator="eq", **kwargs):
        with get_session() as session:
            result = self.where(column, value, session, operator=operator, **kwargs)
            if len(result) == 0:
                result = self.where(column, value, session, operator=operator, **kwargs)
            return result

# Employee.search("name" , "")

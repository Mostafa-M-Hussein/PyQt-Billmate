import datetime
import decimal

from sqlalchemy import String, Integer, Column, DECIMAL, DateTime, Date, select
from sqlalchemy.sql import func

from models import Base, run_in_thread
from models.alchemy import DynamicSearch
from utils.logger.logger import setup_logger

logger = setup_logger("employee_model", "logs/employee.log")


class FreeLancer(Base, DynamicSearch):
    __tablename__ = "freelancers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    note = Column(String(250), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False, default=0)
    other_costs = Column(String(100), nullable=True)
    date = Column(Date, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    @run_in_thread
    @staticmethod
    def get(session , id: str):

        try:
            stmt = select(FreeLancer).where(FreeLancer.id == id)
            result = session.execute(stmt)
            freelancer = result.scalars().first()
            session.refresh(freelancer)
            return freelancer
        except Exception as e:
            session.rollback()
            logger.error(e, exc_info=True)

    @run_in_thread
    @staticmethod
    def add(session,
            note: str,
            amount: decimal.Decimal,
            other_costs: str,
            date: datetime.date = None,
            ):
        try:
            employee = FreeLancer(
                note=note, amount=amount, other_costs=other_costs, date=date
            )
            session.add(employee)
            session.commit()
            session.refresh(employee)
            return employee.id
        except Exception as e:
            session.rollback()
            logger.error(e, exc_info=True)
            return False

    @run_in_thread
    @staticmethod
    def update(session, updated_employee: dict):

        try:
            stmt = select(FreeLancer).where(FreeLancer.id == updated_employee["id"])
            result = session.execute(stmt)
            old = result.scalars().first()
            if not old:
                logger.debug(f"Event with ID {old} not found.")
                return False  # Indicate that the event was not found
            valid_keys = set(
                column
                for column in updated_employee.keys()
                if column in FreeLancer.__table__.columns
            )
            for key in updated_employee.keys():
                if key not in valid_keys:
                    logger.debug(f"Invalid attribute '{key}' for Event model.")
                    raise AttributeError(f"Event has no attribute '{key}'")

            for key, value in updated_employee.items():
                setattr(old, key, value)

            session.commit()
            session.refresh(old)
        except Exception as e:
            session.rollback()
            logger.error(e, exc_info=True)

    @run_in_thread
    @staticmethod
    def get_all(session):
        try:
            stmt = select(FreeLancer).order_by(FreeLancer.created_at)
            result = session.execute(stmt)
            freelancers = result.scalars().all()
            for freelancer in freelancers:
                session.refresh(freelancer)
            return freelancers
        except Exception as e:
            logger.error(e, exc_info=True)

    @run_in_thread
    @staticmethod
    def remove(session, o ,  id: str):

        try:
            emp = FreeLancer.get(id)
            if emp is not None:
                session.delete(emp)
                session.commit()
            else:
                logger.error("Empty FreeLancer obj")
        except Exception as e:
            session.rollback()
            logger.error(e, exc_info=True)

    @run_in_thread
    def search(self, session, column, value, operator="eq", **kwargs):
        result = self.where(column, value, session, operator=operator, **kwargs)
        if len(result) == 0:
            result = self.where(column, value, session, operator=operator, **kwargs)
        return result

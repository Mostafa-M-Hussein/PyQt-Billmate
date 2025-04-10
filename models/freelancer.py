import datetime
import decimal

from sqlalchemy import String, Integer, Column, DECIMAL, DateTime, Date, select, Index
from sqlalchemy.sql import func

from models import Base, run_in_thread, run_in_thread_search
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

    __table_args__ = (
        Index("idx_freelancer_name", "note"),
        Index("idx_freelancer_payment_amount", "amount"),
        Index("idx_freelancer_other_costs", "other_costs"),
        Index("idx_freelancer_date", "date"),
    )

    @run_in_thread
    @staticmethod
    def get(session, id: str):

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
    def add(
        session,
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
            return employee
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
    def remove(session, o, id: str):

        try:
            stmt = select(FreeLancer).where(FreeLancer.id == id)
            result = session.execute(stmt)
            freelancer = result.scalars().first()
            if freelancer is not None:
                session.delete(freelancer)
                session.commit()
            else:
                logger.error("Empty FreeLancer obj")
        except Exception as e:
            session.rollback()
            logger.error(e, exc_info=True)

    @run_in_thread_search
    def search(self, session, column, value, *args, **kwargs):
        print("type is ==>", type(session), type(column))
        result = self.where(column, value, session, *args, **kwargs)
        if len(result) == 0:
            result = self.where(column, value, session, *args, **kwargs)
        return result

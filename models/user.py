from sqlalchemy import String, Integer, Column, DateTime, select, Enum as SqlEnum
from sqlalchemy.sql import func, and_

from models import Base, run_in_thread
from models.alchemy import DynamicSearch
from models.constant import UserRoles
from utils.logger.logger import setup_logger

logger = setup_logger("employee_model", "logs/models.log")


class User(Base, DynamicSearch):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    role = Column(SqlEnum(UserRoles), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    @run_in_thread
    @staticmethod
    def get(session, name: str):
        try:
            stmt = select(User).where(User.name == name)
            result = session.execute(stmt)
            company = result.scalars().first()
            session.refresh(company)
        except Exception as e:
            session.rollback()
            logger.error(e, exc_info=True)

    @run_in_thread
    @staticmethod
    def add(session,
            name,
            password,
            role

            ):

        try:
            print("add new company")
            company = User(
                name=name,
                password=password,
                role=role
            )
            session.add(company)
            session.commit()
            session.refresh(company)
            return company.id
        except Exception as e:
            session.rollback()
            logger.error(e, exc_info=True)
            return False

    @run_in_thread
    @staticmethod
    def update(session, updated_user: dict):

        try:
            stmt = select(User).where(User.id == updated_user["id"])
            result = session.execute(stmt)
            old = result.scalars().first()
            if not old:
                logger.debug(f"Event with ID {old} not found.")
                return False
            valid_keys = set(
                column
                for column in updated_user.keys()
                if column in User.__table__.columns
            )
            for key in updated_user.keys():
                if key not in valid_keys:
                    logger.debug(f"Invalid attribute '{key}' for Event model.")
                    raise AttributeError(f"Event has no attribute '{key}'")

            for key, value in updated_user.items():
                setattr(old, key, value)
            print(old)
            session.commit()
            session.refresh(old)
        except Exception as e:
            session.rollback()
            logger.error(e, exc_info=True)

    @run_in_thread
    @staticmethod
    def get_all(session):
        try:
            stmt = select(User).order_by(User.created_at)
            result = session.execute(stmt)
            companys = result.scalars().all()
            for company in companys:
                session.refresh(company)
            return companys
        except Exception as e:
            logger.error(e, exc_info=True)

    @run_in_thread
    @staticmethod
    def remove(session, name: str):

        try:
            emp = User.get(name)
            session.delete(emp)
            session.commit()
            session.refresh(emp)
        except Exception as e:
            session.rollback()
            logger.error(e, exc_info=True)

    @run_in_thread
    @classmethod
    def verify(cls, session, name, password):
        return session.query(cls).where(and_(cls.name == name, cls.password == password)).first()

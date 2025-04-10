import datetime
import decimal

from sqlalchemy import (
    String,
    Integer,
    Column,
    DECIMAL,
    DateTime,
    Date,
    select,
    ForeignKey,
)
from sqlalchemy.orm import relationship, joinedload, selectinload
from sqlalchemy.sql import func

from models import Base, get_session
from models.alchemy import DynamicSearch
from models.company_owner import ShippingCompany
from utils.logger.logger import setup_logger

logger = setup_logger("employee_model", "logs/models.log")

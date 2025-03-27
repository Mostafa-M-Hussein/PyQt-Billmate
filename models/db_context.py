import os.path
from sqlalchemy import create_engine, inspect
from models import engine, logger, Base
from models.employee import Employee
from models.company_owner import Company
from models.freelancer import FreeLancer
from models.user import User

def ensure_tables():
    if not  os.path.exists('database.db') :
        Base.metadata.create_all(engine)

    # Base.metadata.create_all(engine)




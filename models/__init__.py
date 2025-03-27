import functools
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

from sqlalchemy import inspect , create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base  , sessionmaker


from utils.logger.logger import setup_logger

db_url = "sqlite:///database.db"
# db_url = f"mysql+pymysql://moado:P%40$$wOrd25@203.161.56.185:3306/app_db"
# engine = create_engine(
#     db_url,
#     echo=False,
#     pool_size=10,  # Reduced from 20 - start smaller and increase if needed
#     max_overflow=5,  # Reduced from 10
#     pool_timeout=10,  # Reduced from 30 - fail faster
#     pool_pre_ping=True,
#     pool_recycle=1800,  # Reduced from 3600 - recycle connections more frequently
#     connect_args={
#         "connect_timeout": 10,  # Set timeout for connection attempts
#         "read_timeout": 30,     # Set timeout for read operations
#         "write_timeout": 30     # Set timeout for write operations
#     }
# )
engine = create_engine(db_url, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine,  expire_on_commit=False)
logger = setup_logger("db", "logs/db.log")
db_executor = ThreadPoolExecutor(max_workers=5)


@contextmanager
def get_session() :
    with Session() as session:
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(e , exc_info=True )
        finally:
            session.close()


def run_in_thread(func):
    """
    Decorator to run database operations in a separate thread.
    This prevents UI freezing during database operations.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the callback if provided
        callback = kwargs.pop('callback', None)
        # Function to execute in thread
        def thread_task():
            try:

                with get_session() as session:

                    result = func(session, *args, **kwargs)


                if callback and callable(callback):
                    callback(result=result, error=None)

                return result
            except Exception as e:
                # Handle exceptions
                if callback and callable(callback):
                    callback(result=None, error=e)
                    raise e
                else:
                    # Re-raise if no callback
                    raise

        # Submit the task to the thread pool
        future = db_executor.submit(thread_task)
        return future

    return wrapper

# class DatabaseThreadManager:
#     _instance = None
#     _lock = threading.Lock()
#
#     def __new__(cls, *args, **kwargs):
#         with cls._lock:
#             if cls._instance is None:
#                 cls._instance = super().__new__(cls)
#                 cls._instance.thread_pool = ThreadPoolExecutor(max_workers=5)
#                 cls._instance.session_local = threading.local()
#         return cls._instance
#
#     def get_session(self):
#         if hasattr(self.session_local, 'session'):
#             self.session_local.session = session()
#         return self.session_local.session
#
#     def close_session(self):
#         if hasattr(self.session_local, 'session'):
#             self.session_local.session.close()
#             del self.session_local.session
#
#     def async_execute(self):
#         pass
#
#     def _execute_in_thread(self):
#         pass



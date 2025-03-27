import functools
import traceback
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

from sqlalchemy import inspect , create_engine , text
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base  , sessionmaker

from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSignal, QObject

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
#
# with engine.connect() as connection:
#     # Disable foreign key checks to allow dropping
#     connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
#
#     # Drop the database
#     connection.execute(text("DROP DATABASE IF EXISTS app_db"))
#
#     # Recreate the database
#     connection.execute(text("CREATE DATABASE app_db"))
#
#     # Re-enable foreign key checks
#     connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
#     print("done")


# def drop_and_create_database(engine):
#     try:
#         with engine.connect() as conn:
#             # Switch to system database to drop and create
#             conn.execute(text("USE mysql"))
#
#             # Drop database if exists
#             conn.execute(text("DROP DATABASE IF EXISTS app_db"))
#
#             # Create new database
#             conn.execute(text("CREATE DATABASE app_db"))
#
#             print("Database dropped and recreated successfully")
#     except Exception as e:
#         print(f"Error occurred: {e}")
#
#
# # Execute the function
# drop_and_create_database(engine)

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


class DatabaseSignals(QObject):
    """
    Signals class to handle database operation results
    """
    finished = pyqtSignal(object)  # Result signal
    error = pyqtSignal(Exception)  # Error signal


class DatabaseRunnable(QRunnable):
    """
    Runnable class to handle database operations in a thread pool
    """

    def __init__(self, func, session_factory, *args, **kwargs):
        """
        Initialize the runnable with function and arguments

        :param func: Database function to execute
        :param session_factory: Database session factory
        :param args: Positional arguments for the function
        :param kwargs: Keyword arguments for the function
        """
        super().__init__()

        self.func = func
        self.session_factory = session_factory
        self.args = args
        self.kwargs = kwargs

        # Signals for communication
        self.signals = DatabaseSignals()

        # Extract callback if provided
        self.callback = self.kwargs.pop('callback', None)

    def run(self):
        """
        Execute the database operation
        """
        try:
            # Create a new session
            with self.session_factory() as session:
                # Execute the function with the session
                result = self.func(session, *self.args, **self.kwargs)

                # Emit the result via signals
                self.signals.finished.emit(result)

                # Call callback if provided
                if self.callback and callable(self.callback):
                    self.callback(result=result, error=None)

        except Exception as e:
            # Capture full traceback for debugging
            error_traceback = traceback.format_exc()

            # Create exception with full traceback
            full_error = Exception(f"{str(e)}\n{error_traceback}")

            # Emit the error via signals
            self.signals.error.emit(full_error)

            # Call callback with error if provided
            if self.callback and callable(self.callback):
                self.callback(result=None, error=full_error)


def run_in_thread(func):
    """
    Decorator to run database operations in a QThreadPool

    :param func: Database function to be executed in a thread pool
    :return: Wrapped function that runs in a thread pool
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get global or create a new thread pool
        thread_pool = getattr(wrapper, 'thread_pool', QThreadPool.globalInstance())

        # Create the runnable
        runnable = DatabaseRunnable(
            func,
            get_session,  # Assumes get_session is defined elsewhere
            *args,
            **kwargs
        )

        # Start the runnable in the thread pool
        thread_pool.start(runnable)

        # Return the signals for advanced control if needed
        return runnable.signals

    # Attach a thread pool to the wrapper if needed
    wrapper.thread_pool = QThreadPool()
    # Optional: Set max thread count (default is typically CPU core count)
    wrapper.thread_pool.setMaxThreadCount(10)

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



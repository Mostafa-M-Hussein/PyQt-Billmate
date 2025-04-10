from abc import ABC, abstractmethod


class BaseView(ABC):

    @abstractmethod
    def get_column_headers(self, role):
        raise NotImplementedError(f"No Implemented {self.__name__}")

    @abstractmethod
    def update_table_data(self):
        raise NotImplementedError(f"No Implemented {self.__name__}")

    @abstractmethod
    def update_items(self, result=None, error=None):
        raise NotImplementedError(f"No Implemented {self.__name__}")

    @abstractmethod
    def create_table_item_widget(self, for_display, for_edit):
        raise NotImplementedError(f"No Implemented {self.__name__}")

    @abstractmethod
    def create_table_item_widgets(self, rows):
        raise NotImplementedError(f"No Implemented {self.__name__}")

    @abstractmethod
    def setup_table_widget(self):
        raise NotImplementedError(f"No Implemented {self.__name__}")

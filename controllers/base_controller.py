from abc import ABC, abstractmethod

from PyQt5.QtWidgets import QTableWidgetItem


class BaseController(ABC):

    @abstractmethod
    def on_item_changed(self, item: QTableWidgetItem):
        raise NotImplementedError(f"No Implemented {self.__name__}")

    def check_fields(self, fields: list) -> bool:
        """Check if all fields are instances of QTableWidgetItem."""
        return all(isinstance(field, QTableWidgetItem) for field in fields)


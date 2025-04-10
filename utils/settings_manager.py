from PyQt5.QtCore import QSettings, QVariant


class SettingManager:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(SettingManager, cls).__new__(cls)
            cls.__instance.settings = QSettings(
                QSettings.IniFormat, QSettings.SystemScope, "gear4", "app"
            )
        return cls.__instance

    def remove_value(self, key):
        self.settings.remove(key)

    def get_value(self, key, default=None):
        # Get value and convert QVariant to Python object
        value = self.settings.value(key)

        if value is None:
            return default

        # Convert QVariant to Python type if needed
        if isinstance(value, QVariant):
            value = value.toPyObject()

        # Handle special case for empty QVariant
        if value == QVariant():
            return default

        return value

    def set_value(self, key, value):
        self.settings.setValue(key, value)
        self.settings.sync()


# s = SettingManager()
#
# s.set_value("title" , "moado" )
# print(s.get_value('title'))
# ss = SettingManager()
# print(ss.get_value('title'))

from abc import ABC


class SingleTone(type, ABC):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def get_current_instance(cls):
        return cls._instances.get(cls)


class SingletonMixin:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


def singleton(cls):
    _instance = {}

    def _singleton(*args, **kwargs):
        print(_instance)
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton

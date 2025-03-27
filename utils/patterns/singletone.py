from abc import ABC, abstractmethod


class SingleTone(type, ABC):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def get_current_instance(cls):
        return cls._instances.get(cls)

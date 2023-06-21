from multiprocessing import Lock

from tinydb import Storage


def singleton(clazz):
    # noinspection PyUnusedLocal
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance') or cls._instance is None:
            cls._instance = super(cls, cls).__new__(cls)
        return cls._instance

    clazz.__new__ = __new__
    return clazz


class Lockable:
    def __init__(self):
        self._lock = Lock()


class AtomicDict(Lockable):
    def __init__(self):
        super().__init__()
        self._dict = {}

    def __contains__(self, item):
        return item in self._dict

    def __getitem__(self, k):
        return self._dict[k]

    def __setitem__(self, k, v):
        with self._lock:
            self._dict[k] = v

    def __delitem__(self, k):
        with self._lock:
            del self._dict[k]

    def __str__(self):
        return str(self._dict)

    def __repr__(self):
        return str(self)

    def get(self, __key, __default):
        return self._dict.get(__key, __default)

    def pop(self, __key):
        with self._lock:
            return self._dict.pop(__key)

    def clear(self):
        with self._lock:
            return self._dict.clear()

    @property
    def data(self):
        return self._dict

    @data.setter
    def data(self, __dict: dict):
        with self._lock:
            self._dict = __dict


@singleton
class AtomicMemoryDict(AtomicDict):
    pass


persistent_storage = AtomicMemoryDict()


class AtomicMemoryStorage(Storage):
    def read(self):
        return persistent_storage.data

    def write(self, data) -> None:
        persistent_storage.data = data

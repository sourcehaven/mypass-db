import abc
import os
from pathlib import Path

from tinydb import TinyDB, Storage

DB_PATH = Path.home().joinpath('.mypass', 'db', 'tinydb', 'db.json')


class TinyDao(abc.ABC):
    def __init__(self, path: str | os.PathLike = None, storage: Storage = None, *args, **kwargs):
        if path is None:
            path = DB_PATH
        path = Path(path)
        self._path = path
        self._storage = storage
        self._storage_args = args
        self._storage_kwargs = kwargs
        if storage is not None:
            self._storage_kwargs['storage'] = storage

    def init_db(self):
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True)
            self._path.touch()

    def get_connection(self):
        self.init_db()
        return TinyDB(self._path, *self._storage_args, **self._storage_kwargs)

    def unlink(self):
        unlink(self._path)

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def read_one(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def read(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def delete(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def delete_all(self, *args, **kwargs):
        ...


def unlink(path: str | os.PathLike = None):
    if path is None:
        path = DB_PATH
    path = Path(path)

    if path.exists():
        if path.is_file():
            path.unlink()
            return True
        else:
            print(f'USER WARNING :: Calling unlink on directory: {str(path)}')
            return False
    print('USER WARNING :: Calling unlink on non-existing db file.')
    return False

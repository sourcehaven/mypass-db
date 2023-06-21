import abc
import os
from pathlib import Path
from typing import Type

from tinydb import TinyDB, Storage


class TinyDao(abc.ABC):
    def __init__(self, path: str | os.PathLike = None, storage: Type[Storage] = None, *args, **kwargs):
        if path is not None:
            path = Path(path)
        self._path = path
        self._storage = storage
        self._storage_args = args
        self._storage_kwargs = kwargs
        if storage is not None:
            self._storage_kwargs['storage'] = storage
        if path is not None:
            self._storage_kwargs['path'] = path

    def init_db(self):
        if self._path is None:
            return

        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True)
            self._path.touch()

    def get_connection(self):
        self.init_db()
        return TinyDB(*self._storage_args, **self._storage_kwargs)

    def unlink(self):
        if self._path is not None:
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


def unlink(path: str | os.PathLike):
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

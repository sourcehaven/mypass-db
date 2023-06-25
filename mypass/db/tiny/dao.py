import os
from pathlib import Path
from typing import Type, Iterable, Mapping

from tinydb import TinyDB, Storage
from tinydb.queries import QueryLike
from tinydb.table import Document

import mypass.db.tiny.operations as ops


class TinyDao:
    def __init__(
            self,
            table: str,
            path: str | os.PathLike = None,
            storage: Type[Storage] = None,
            *args,
            **kwargs
    ):
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
        self.table = table

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

    def create(self, entity: Mapping):
        with self.get_connection() as conn:
            t = conn.table(self.table)
            return t.insert(entity)

    def read_one(self, *, cond: QueryLike = None, doc_id: int = None):
        assert doc_id is None or cond is None, 'Specifying both `doc_id` and `cond` is invalid.'
        assert doc_id is not None or cond is not None, 'Specify either `doc_id` or `cond`.'
        with self.get_connection() as conn:
            t = conn.table(self.table)
            doc: Document | None = t.get(doc_id=doc_id, cond=cond)
            return doc

    def read(self, *, cond: QueryLike = None, doc_ids: Iterable[int] = None):
        assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
        with self.get_connection() as conn:
            t = conn.table(self.table)
            if doc_ids is not None:
                docs: list[Document] = t.get(doc_ids=list(doc_ids))
                return docs
            elif cond is not None:
                return t.search(cond)
            return t.all()

    def update(
            self,
            entity: Mapping,
            *,
            cond: QueryLike = None,
            doc_ids: Iterable[int] = None
    ):
        assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
        with self.get_connection() as conn:
            t = conn.table(self.table)
            return t.update(ops.update(fields=entity), cond=cond, doc_ids=doc_ids)

    def delete(self, *, cond: QueryLike = None, doc_ids: Iterable[int] = None):
        assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
        with self.get_connection() as conn:
            t = conn.table(self.table)
            return t.remove(cond=cond, doc_ids=doc_ids)

    def delete_all(self):
        with self.get_connection() as conn:
            t = conn.table(self.table)
            return t.truncate()


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

from typing import Iterable, Mapping

from tinydb.queries import QueryLike
from tinydb.table import Document

import mypass.db.tiny.operations as ops
from mypass.db.tiny._dao import TinyDao


class VaultDao(TinyDao):
    table = 'vault'

    def create(self, **kwargs):
        with self.get_connection() as conn:
            t = conn.table(VaultDao.table)
            return t.insert(kwargs)

    def read_one(self, *, doc_id: int = None, cond: QueryLike = None):
        assert doc_id is None or cond is None, 'Specifying both `doc_id` and `cond` is invalid.'
        assert doc_id is not None or cond is not None, 'Specify either `doc_id` or `cond`.'
        with self.get_connection() as conn:
            t = conn.table(VaultDao.table)
            doc: Document | None = t.get(doc_id=doc_id, cond=cond)
            return doc

    def read(self, *, cond: QueryLike = None, doc_ids: Iterable[int] = None):
        assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
        with self.get_connection() as conn:
            t = conn.table(VaultDao.table)
            if doc_ids is not None:
                docs: list[Document] = t.get(doc_ids=doc_ids)
                return docs
            elif cond is not None:
                return t.search(cond)
            return t.all()

    def update(
            self,
            fields: Mapping = None,
            *,
            cond: QueryLike = None,
            doc_ids: Iterable[int] = None,
            remove_keys: Iterable[str] = None
    ):
        assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
        with self.get_connection() as conn:
            t = conn.table(VaultDao.table)
            updated_ids = []
            if fields is not None:
                updated_ids = t.update(fields=fields, cond=cond, doc_ids=doc_ids)
            if remove_keys is not None:
                removed_key_ids = t.update(ops.delete_keys(remove_keys), cond=cond, doc_ids=doc_ids)
            return list(set.union(set(updated_ids), set(removed_key_ids)))

    def delete(self, *, cond: QueryLike = None, doc_ids: Iterable[int] = None):
        assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
        with self.get_connection() as conn:
            t = conn.table(VaultDao.table)
            return t.remove(cond=cond, doc_ids=doc_ids)

    def delete_all(self):
        with self.get_connection() as conn:
            t = conn.table(VaultDao.table)
            return t.truncate()

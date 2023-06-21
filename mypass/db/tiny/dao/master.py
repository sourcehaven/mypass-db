from typing import Iterable

from tinydb.queries import QueryLike
from tinydb.table import Document

from mypass.db.tiny._dao import TinyDao


class MasterDao(TinyDao):
    table = 'master'

    def create(self, user: str, token: str, pw: str, salt: str):
        with self.get_connection() as conn:
            t = conn.table(MasterDao.table)
            return t.insert({'user': user, 'token': token, 'pw': pw, 'salt': salt})

    def read_one(self, *, cond: QueryLike = None, doc_id: int = None):
        assert doc_id is None or cond is None, 'Specifying both `doc_id` and `cond` is invalid.'
        assert doc_id is not None or cond is not None, 'Specify either `doc_id` or `cond`.'
        with self.get_connection() as conn:
            t = conn.table(MasterDao.table)
            doc: Document | None = t.get(doc_id=doc_id, cond=cond)
            return doc

    def read(self, *, cond: QueryLike = None, doc_ids: Iterable[int] = None):
        assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
        with self.get_connection() as conn:
            t = conn.table(MasterDao.table)
            if doc_ids is not None:
                docs: list[Document] = t.get(doc_ids=doc_ids)
                return docs
            elif cond is not None:
                return t.search(cond)
            return t.all()

    def update(self, token: str, pw: str, salt: str, *, cond: QueryLike = None, doc_ids: Iterable[int] = None):
        assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
        with self.get_connection() as conn:
            t = conn.table(MasterDao.table)
            return t.update(fields={'token': token, 'pw': pw, 'salt': salt}, cond=cond, doc_ids=doc_ids)

    def delete(self, *, cond: QueryLike = None, doc_ids: Iterable[int] = None):
        assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
        with self.get_connection() as conn:
            t = conn.table(MasterDao.table)
            return t.remove(cond=cond, doc_ids=doc_ids)

    def delete_all(self):
        with self.get_connection() as conn:
            t = conn.table(MasterDao.table)
            return t.truncate()

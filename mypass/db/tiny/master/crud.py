from typing import Iterable

from tinydb.queries import QueryLike
from tinydb.table import Document

from mypass.db.tiny.master._table import master


def create(user: str, token: str, pw: str, salt: str):
    with master() as t:
        return t.insert({'user': user, 'token': token, 'pw': pw, 'salt': salt})


def read_one(*, cond: QueryLike = None, doc_id: int = None):
    assert doc_id is None or cond is None, 'Specifying both `doc_id` and `cond` is invalid.'
    assert doc_id is not None or cond is not None, 'Specify either `doc_id` or `cond`.'
    with master() as t:
        doc: Document | None = t.get(doc_id=doc_id, cond=cond)
        return doc


def read(*, cond: QueryLike = None, doc_ids: Iterable[int] = None):
    assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
    with master() as t:
        if doc_ids is not None:
            docs: list[Document] = t.get(doc_ids=doc_ids)
            return docs
        elif cond is not None:
            return t.search(cond)
        return t.all()


def update(token: str, pw: str, salt: str, *, cond: QueryLike = None, doc_ids: Iterable[int] = None):
    assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
    with master() as t:
        return t.update(fields={'token': token, 'pw': pw, 'salt': salt}, cond=cond, doc_ids=doc_ids)


def delete(*, cond: QueryLike = None, doc_ids: Iterable[int] = None):
    assert doc_ids is None or cond is None, 'Specifying both `doc_ids` and `cond` is invalid.'
    with master() as t:
        return t.remove(cond=cond, doc_ids=doc_ids)


def delete_all():
    with master() as t:
        return t.truncate()

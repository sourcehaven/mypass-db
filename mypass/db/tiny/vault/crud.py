from typing import Iterable

from tinydb.queries import QueryLike
from tinydb.table import Document

from ._table import vault


def create(**kwargs):
    with vault() as t:
        return t.insert(kwargs)


def read_one(doc_id: int = None, cond: QueryLike = None):
    with vault() as t:
        doc: Document | None = t.get(doc_id=doc_id, cond=cond)
        return doc


def read(cond: QueryLike = None, doc_ids: Iterable[int] = None):
    with vault() as t:
        if doc_ids is not None:
            docs: list[Document] = t.get(doc_ids=doc_ids)
            return docs
        elif cond is not None:
            return t.search(cond)
        return t.all()


def update(
        cond: QueryLike = None,
        doc_ids: Iterable[int] = None,
        **kwargs
):
    with vault() as t:
        # TODO: consider the case of key deletion with tinydb.operations.delete
        return t.update(fields=kwargs, cond=cond, doc_ids=doc_ids)


def delete(cond: QueryLike = None, doc_ids: Iterable[int] = None):
    with vault() as t:
        return t.remove(cond=cond, doc_ids=doc_ids)


def delete_all():
    with vault() as t:
        return t.truncate()

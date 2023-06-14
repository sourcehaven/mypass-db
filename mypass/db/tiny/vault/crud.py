from typing import Iterable

from tinydb.queries import QueryLike

from ._table import vault


def create(**kwargs):
    with vault() as t:
        return t.insert(kwargs)


def read(cond: QueryLike = None, doc_ids: Iterable[int] = None):
    with vault() as t:
        docs = t.get(cond=cond, doc_ids=doc_ids)
        return [doc for doc in docs if doc is not None]


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

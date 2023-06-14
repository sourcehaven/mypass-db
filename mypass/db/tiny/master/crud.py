from typing import Iterable

from tinydb.queries import QueryLike

from mypass.db.tiny.master._table import master


def create(user: str, token: str, pw: str, salt: str):
    with master() as t:
        return t.insert({'user': user, 'token': token, 'pw': pw, 'salt': salt})


def read(cond: QueryLike = None):
    with master() as t:
        if cond is None:
            return t.all()
        return t.search(cond=cond)


def update(cond: QueryLike = None, doc_ids: Iterable[int] = None, *, token: str, pw: str, salt: str):
    with master() as t:
        return t.update(fields={'token': token, 'pw': pw, 'salt': salt}, cond=cond, doc_ids=doc_ids)


def delete(cond: QueryLike = None, doc_ids: Iterable[int] = None):
    with master() as t:
        return t.remove(cond=cond, doc_ids=doc_ids)


def delete_all():
    with master() as t:
        return t.truncate()

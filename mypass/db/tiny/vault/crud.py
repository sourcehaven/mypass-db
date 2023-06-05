from typing import Iterable

from tinydb.queries import QueryLike

from ._table import vault


def create(
        *,
        pw: str = None,
        salt: str = None,
        user: str = None,
        name: str = None,
        email: str = None,
        site: str = None,
        **kwargs
):
    d = kwargs
    if name is not None:
        d['name'] = name
    if pw is not None:
        d['pw'] = pw
    if salt is not None:
        d['salt'] = salt
    if user is not None:
        d['user'] = user
    if email is not None:
        d['email'] = email
    if site is not None:
        d['site'] = site
    with vault() as t:
        return t.insert(d)


def read(cond: QueryLike = None):
    with vault() as t:
        if cond is None:
            return t.all()
        return t.search(cond=cond)


def update(
        cond: QueryLike = None,
        doc_ids: Iterable[int] = None,
        *,
        pw: str = None,
        salt: str = None,
        user: str = None,
        name: str = None,
        email: str = None,
        site: str = None,
        **kwargs
):
    d = kwargs
    if name is not None:
        d['name'] = name
    if pw is not None:
        d['pw'] = pw
    if salt is not None:
        d['salt'] = salt
    if user is not None:
        d['user'] = user
    if email is not None:
        d['email'] = email
    if site is not None:
        d['site'] = site
    with vault() as t:
        return t.update(fields=d, cond=cond, doc_ids=doc_ids)


def delete(cond: QueryLike = None, doc_ids: Iterable[int] = None):
    with vault() as t:
        return t.remove(cond=cond, doc_ids=doc_ids)

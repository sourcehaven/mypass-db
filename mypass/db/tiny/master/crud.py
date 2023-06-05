from tinydb.queries import QueryLike

from ._table import master


def create(pw: str, salt: str):
    with master() as t:
        return t.insert({'pw': pw, 'salt': salt})


def read(cond: QueryLike = None):
    with master() as t:
        if cond is None:
            return t.all()
        return t.search(cond=cond)


def update(pw: str, salt: str):
    with master() as t:
        return t.update(fields={'pw': pw, 'salt': salt})


def delete():
    with master() as t:
        return t.truncate()

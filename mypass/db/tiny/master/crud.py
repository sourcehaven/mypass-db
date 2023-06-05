from tinydb.queries import QueryLike

from. import master


def create(password: str, salt: str):
    with master() as t:
        return t.insert({'password': password, 'salt': salt})


def read(cond: QueryLike = None):
    with master() as t:
        if cond is None:
            return t.all()
        return t.search(cond=cond)


def update(password: str, salt: str):
    with master() as t:
        return t.update(fields={'password': password, 'salt': salt})


def delete():
    with master() as t:
        return t.truncate()

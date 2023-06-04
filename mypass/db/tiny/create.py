from ._db import tinydb


def create():
    with tinydb() as db:
        pass

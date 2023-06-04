from pathlib import Path

from tinydb import TinyDB


class _DB:
    _tinydb: TinyDB = None

    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def instance():
        if _DB._tinydb is None:
            _DB._tinydb = TinyDB(Path.home().joinpath('.mypass', 'db', 'tinydb', 'db.json'))
        return _DB._tinydb


DB_PATH = Path.home().joinpath('.mypass', 'db', 'tinydb', 'db.json')


def tinydb():
    return TinyDB(DB_PATH)

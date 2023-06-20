import os
from pathlib import Path

from tinydb import TinyDB

DB_PATH = Path.home().joinpath('.mypass', 'db', 'tinydb', 'db.json')


def tinydb(path: str | os.PathLike = None):
    if path is None:
        path = DB_PATH
    if isinstance(path, str):
        path = Path(path)

    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    return TinyDB(path)


def unlink(path: str | os.PathLike = None):
    if path is None:
        path = DB_PATH
    if isinstance(path, str):
        path = Path(path)

    if path.exists():
        if path.is_file():
            path.unlink()
            return True
        else:
            print(f'USER WARNING :: Calling unlink on directory: {str(path)}')
            return False
    print('USER WARNING :: Calling unlink on non-existing db file.')
    return False

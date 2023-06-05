from pathlib import Path

from tinydb import TinyDB

DB_PATH = Path.home().joinpath('.mypass', 'db', 'tinydb', 'db.json')


def tinydb():
    if not DB_PATH.parent.exists():
        DB_PATH.parent.mkdir(parents=True)
    return TinyDB(DB_PATH)


def unlink():
    path = Path(DB_PATH)
    if path.exists():
        if path.is_file():
            path.unlink()
            return True
        else:
            print(f'USER WARNING :: Calling unlink on directory: {str(path)}')
            return False
    print('USER WARNING :: Calling unlink on non-existing db file.')
    return False

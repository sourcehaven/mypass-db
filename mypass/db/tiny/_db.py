from pathlib import Path

from tinydb import TinyDB

DB_PATH = Path.home().joinpath('.mypass', 'db', 'tinydb', 'db.json')


def tinydb():
    """
    Returns a TinyDB instance connected to the database file.

    The function creates the necessary directory structure for the database file if it doesn't exist.

    Returns:
        TinyDB: A TinyDB instance connected to the database file.

    Example usage:
        db = tinydb()
        # Perform operations on the TinyDB instance
    """
    return TinyDB(DB_PATH)

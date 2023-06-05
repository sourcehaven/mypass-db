from pathlib import Path

from mypass.db.tiny._db import DB_PATH


def delete_db():
    """
    Deletes the entire database by removing the database file.

    Returns:
        bool: True if the database file was successfully deleted, False if the file was not found.
    """
    try:
        Path(DB_PATH).unlink()
        return True
    except FileNotFoundError:
        return False

from ._db import tinydb


class TinyTable:
    def __init__(self, table: str):
        self.table_name = table

    def __enter__(self):
        self.db = tinydb()
        self.table = self.db.table(self.table_name)
        return self.table

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

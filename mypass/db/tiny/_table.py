from ._db import tinydb


class TinyTable:
    def __init__(self, table: str, *args, **kwargs):
        self.table_name = table
        self._db_args = args
        self._db_kwargs = kwargs

    def __enter__(self):
        self.db = tinydb(*self._db_args, **self._db_kwargs)
        self.table = self.db.table(self.table_name)
        return self.table

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

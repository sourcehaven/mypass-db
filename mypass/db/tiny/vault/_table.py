from mypass.db.tiny import tinydb


class Vault:
    def __enter__(self):
        self.db = tinydb()
        self.table = self.db.table('vault')
        return self.table

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


def vault():
    """
    Returns a context manager for accessing the 'vault' table where user credentials are stored.
    """
    return Vault()

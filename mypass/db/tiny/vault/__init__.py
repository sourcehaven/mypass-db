from mypass.db.tiny import TinyTable

from .crud import create, read, update, delete


def vault():
    return TinyTable('vault')

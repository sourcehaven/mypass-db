from mypass.db.tiny import TinyTable

from .crud import create, read, update, delete


def master():
    return TinyTable('master')

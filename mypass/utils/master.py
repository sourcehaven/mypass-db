from mypass.db.tiny.master import create, read, update
from mypass.exceptions import MasterPasswordExistsError, MultipleMasterPasswordsError


def create_master_password(pw: str, salt: str):
    items = read()
    if len(items) > 0:
        raise MasterPasswordExistsError('Trying to store multiple master passwords.')
    return create(pw, salt)


def read_master_password():
    items = read()
    if len(items) > 1:
        raise MultipleMasterPasswordsError(f'Using a corrupted database with {len(items)} master passwords.')
    return items[0]


def update_master_password(pw: str, salt: str):
    items = update(pw, salt)
    if len(items) > 1:
        raise MultipleMasterPasswordsError(f'Using a corrupted database with {len(items)} master passwords.')
    return items[0]

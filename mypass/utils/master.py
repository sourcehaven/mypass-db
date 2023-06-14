from tinydb import Query

from mypass.db.tiny.master import create, read, update
from mypass.exceptions import MasterPasswordExistsError, MultipleMasterPasswordsError


def create_master_password(user: str, token: str, pw: str, salt: str):
    q = Query()
    items = read(q.user == user)
    if len(items) > 0:
        raise MasterPasswordExistsError('Trying to store multiple master passwords for the same user.')
    return create(user, token, pw, salt)


def read_master_password(user: str):
    q = Query()
    items = read(q.user == user)
    if len(items) > 1:
        raise MultipleMasterPasswordsError(
            f'Using a corrupted database with\n'
            f'    user: {user}\n'
            f'    number of master passwords: {len(items)}.')
    # TODO: raise special exception if no items found (this only throws IndexError(0)
    return items[0]


def update_master_password(user: str, token: str, pw: str, salt: str):
    q = Query()
    items = update(q.user == user, token=token, pw=pw, salt=salt)
    if len(items) > 1:
        raise MultipleMasterPasswordsError(
            f'Using a corrupted database with\n'
            f'    user: {user}\n'
            f'    number of master passwords affected: {len(items)}.')
    # TODO: raise special exception if no items found (this only throws IndexError(0)
    return items[0]


def _main():
    doc_id = create_master_password('mypass', 'my-master-token', 'strong-pass', 'salted')
    doc = read_master_password('mypass')

    import json
    json_doc = json.dumps(doc)

    print('Doc id      :', doc_id)
    print('Doc         :', doc)
    print('JSON Doc    :', json_doc)


if __name__ == '__main__':
    _main()

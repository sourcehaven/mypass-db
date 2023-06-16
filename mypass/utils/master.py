from tinydb import Query

from mypass.db.tiny.master import create, read, read_one, update
from mypass.exceptions import MasterPasswordExistsError, MultipleMasterPasswordsError, UserNotExistsError


def create_master_password(user: str, token: str, pw: str, salt: str):
    q = Query()
    items = read(cond=q.user == user)
    if len(items) > 0:
        raise MasterPasswordExistsError('Trying to store multiple master passwords for the same user.')
    return create(user, token, pw, salt)


def read_master_password(user_or_id: str | int):
    q = Query()
    if isinstance(user_or_id, str):
        items = read(cond=q.user == user_or_id)
        if len(items) > 1:
            raise MultipleMasterPasswordsError(
                f'Using a corrupted database with\n'
                f'    user: {user_or_id}\n'
                f'    number of master passwords: {len(items)}.')
        try:
            return items[0]
        except IndexError:
            raise UserNotExistsError(f'User name `{user_or_id}` does not exist in the database.')
    else:
        item = read_one(doc_id=user_or_id)
        if item is not None:
            return item
        raise UserNotExistsError(f'User id `{user_or_id}` does not exist in the database.')


def update_master_password(user: str, token: str, pw: str, salt: str):
    q = Query()
    items = update(token=token, pw=pw, salt=salt, cond=q.user == user)
    if len(items) > 1:
        raise MultipleMasterPasswordsError(
            f'Using a corrupted database with\n'
            f'    user: {user}\n'
            f'    number of master passwords affected: {len(items)}.')
    try:
        return items[0]
    except IndexError:
        raise UserNotExistsError(f'User `{user}` does not exist in the database.')


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

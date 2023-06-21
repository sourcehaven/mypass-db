from tinydb import Query

from mypass.db.tiny.dao import MasterDao
from mypass.exceptions import MasterPasswordExistsError, MultipleMasterPasswordsError, UserNotExistsError


class MasterController:
    def __init__(self, dao: MasterDao = None, *args, **kwargs):
        assert dao is None or (len(args) == 0 and len(kwargs) == 0), \
            'When dao is specified, there should not be any arguments and/or keyword arguments present.'
        if dao is None:
            dao = MasterDao(*args, **kwargs)
        self.dao = dao

    def create_master_password(self, user: str, token: str, pw: str, salt: str):
        q = Query()
        items = self.dao.read(cond=q.user == user)
        if len(items) > 0:
            raise MasterPasswordExistsError('Trying to store multiple master passwords for the same user.')
        return self.dao.create(user, token, pw, salt)

    def read_master_password(self, user_or_id: str | int):
        q = Query()
        if isinstance(user_or_id, str):
            items = self.dao.read(cond=q.user == user_or_id)
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
            item = self.dao.read_one(doc_id=user_or_id)
            if item is not None:
                return item
            raise UserNotExistsError(f'User id `{user_or_id}` does not exist in the database.')

    def update_master_password(self, user: str, token: str, pw: str, salt: str):
        q = Query()
        items = self.dao.update(token=token, pw=pw, salt=salt, cond=q.user == user)
        if len(items) > 1:
            raise MultipleMasterPasswordsError(
                f'Using a corrupted database with\n'
                f'    user: {user}\n'
                f'    number of master passwords affected: {len(items)}.')
        try:
            return items[0]
        except IndexError:
            raise UserNotExistsError(f'User `{user}` does not exist in the database.')

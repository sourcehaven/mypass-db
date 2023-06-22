from tinydb import Query

from mypass.db.tiny.dao import MasterDao
from mypass.exceptions import MasterPasswordExistsError, MultipleMasterPasswordsError, UserNotExistsError
from mypass.utils import document_as_dict
from mypass.utils.tinydb import check_uid


_T_DAO = MasterDao


class MasterController:
    table = _T_DAO.table

    def __init__(self, dao: _T_DAO = None, *args, **kwargs):
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

    def read_master_password(self, user_or_uid: str | int):
        q = Query()
        if isinstance(user_or_uid, str):
            items = self.dao.read(cond=q.user == user_or_uid)
            if len(items) > 1:
                raise MultipleMasterPasswordsError(
                    f'Using a corrupted database with\n'
                    f'    user: {user_or_uid}\n'
                    f'    number of master passwords: {len(items)}.')
            try:
                return document_as_dict(items[0])
            except IndexError:
                raise UserNotExistsError(f'User name `{user_or_uid}` does not exist in the database.')
        else:
            check_uid(user_or_uid)
            item = self.dao.read_one(doc_id=user_or_uid)
            if item is not None:
                return document_as_dict(item)
            raise UserNotExistsError(f'User id `{user_or_uid}` does not exist in the database.')

    def update_master_password(self, user_or_uid: str | int, token: str, pw: str, salt: str):
        q = Query()
        if isinstance(user_or_uid, str):
            kwargs = {'cond': q.user == user_or_uid}
        else:
            kwargs = {'doc_ids': [user_or_uid]}
        try:
            items = self.dao.update(token=token, pw=pw, salt=salt, **kwargs)
        except KeyError:
            raise UserNotExistsError(f'User `{user_or_uid}` does not exist in the database.')
        if len(items) > 1:
            raise MultipleMasterPasswordsError(
                f'Using a corrupted database with\n'
                f'    user: {user_or_uid}\n'
                f'    number of master passwords affected: {len(items)}.')
        try:
            return items[0]
        except IndexError:
            raise UserNotExistsError(f'User `{user_or_uid}` does not exist in the database.')

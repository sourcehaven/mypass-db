from tinydb import Query

from mypass.db.tiny import TinyRepository, TinyDao
from mypass.exceptions import MasterPasswordExistsError, MultipleMasterPasswordsError, UserNotExistsError
from mypass.types import MasterVaultEntity
from mypass.utils import document_as_dict
from mypass.utils.tinydb import check_uid

_T = MasterVaultEntity


class MasterTinyRepository(TinyRepository[int, _T]):
    def __init__(self, dao: TinyDao = None, *args, **kwargs):
        super().__init__(dao, *args, **kwargs)

    def create_master_password(self, entity: _T):
        q = Query()
        items = self.dao.read(cond=q.user == entity.user)
        if len(items) > 0:
            raise MasterPasswordExistsError('Trying to store multiple master passwords for the same user.')
        return self.dao.create(entity=entity)

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

    def update_master_password(self, user_or_uid: str | int, update: _T):
        q = Query()
        if isinstance(user_or_uid, str):
            kwargs = {'cond': q.user == user_or_uid}
        else:
            kwargs = {'doc_ids': [user_or_uid]}
        try:
            items = self.dao.update(entity=update, **kwargs)
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

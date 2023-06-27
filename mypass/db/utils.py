from typing import Literal, Callable, Any, Iterable

from mypass.exceptions import MasterPasswordExistsError, UserNotExistsError, InvalidUpdateError, RequiresIdError, \
    EmptyRecordInsertionError, EmptyQueryError, RecordNotFoundError
from mypass.types import MasterEntity, VaultEntity
from mypass.types import const
from mypass.utils import gen_uuid
from .repository import CrudRepository
from ..types.op import DEL


def create_query_all(query_like: dict):
    """Missing keys will cause filter to return false."""
    return lambda q: all([q[k] == v if k in q else False for k, v in query_like.items()])


def create_query_any(query_like: dict):
    """Missing keys will evaluate to false."""
    return lambda q: any([q[k] == v if k in q else False for k, v in query_like.items()])


def create_query(query_like: dict, logic: Literal['and', 'or']) -> Callable[[Any], bool]:
    """Missing keys will evaluate to false."""
    if logic == 'and':
        return create_query_all(query_like)
    return create_query_any(query_like)


def create_query_with_uid(__uid: int | str = None, cond: dict = None):
    if cond is not None:
        if __uid is not None:
            cond[const.UID_FIELD] = __uid
        cond = create_query(cond, logic='and')
    elif __uid is not None:
        cond = create_query({const.UID_FIELD: __uid}, logic='and')
    return cond


class MasterDbSupport:
    def __init__(self, repo: CrudRepository):
        self.repo = repo

    def create_master_password(self, entity: MasterEntity):
        """
        Creates a master vault entry.

        Returns:
            The newly created id.
        Raises:
            MasterPasswordExistsError: Raises only if the user already exists in master vault.
        """

        item = self.repo.find_one(entity=MasterEntity(user=entity.user))
        if item is None:
            try:
                return self.repo.create(entity=entity)
            except RequiresIdError:
                entity.id = gen_uuid(self.repo.id_cls.__class__.__name__)
                return self.repo.create(entity=entity)
        raise MasterPasswordExistsError('Trying to store multiple master passwords for the same user.')

    def read_master_password(self, user_or_uid):
        """
        Reads the master password of a given user.

        Returns:
            str: Password part of the entity. Only a string is returned.
        Raises:
            UserNotExistsError - Raises only if the given user does not exist in the db.
        """

        if isinstance(user_or_uid, self.repo.id_cls):
            item: MasterEntity = self.repo.find_by_id(user_or_uid)
        elif isinstance(user_or_uid, str):
            item = self.repo.find_one(entity=MasterEntity(user=user_or_uid))
        else:
            raise TypeError(f'Parameter user_or_uid should be either of type {str} or {self.repo.id_cls}.')
        if item is None:
            raise UserNotExistsError(f'User with id {user_or_uid} could not be found.')
        pw: str = item.pw
        return pw

    def update_master_password(self, user_or_uid, update: MasterEntity):
        """
        Updates master password for a given user.

        Returns:
            Updated id.
        Raises:
            TypeError: Only if param user_or_uid is not an accepted user
        """

        if 'user' in update or 'token' in update:
            raise InvalidUpdateError('User and master token cannot be updated inside master vault.')
        if isinstance(user_or_uid, self.repo.id_cls):
            return self.repo.update_by_id(user_or_uid, update=update)
        elif isinstance(user_or_uid, str):
            items = self.repo.update_by_crit(
                crit=MasterEntity(user=user_or_uid), update=MasterEntity(user=user_or_uid))
            try:
                return list(items)[0]
            except IndexError:
                raise UserNotExistsError(f'User with id {user_or_uid} could not be found.')
        else:
            raise TypeError(f'Parameter user_or_uid should be either of type {str} or {self.repo.id_cls}.')


class VaultDbSupport:
    def __init__(self, repo: CrudRepository):
        self.repo = repo

    def create_vault_entry(self, __uid=None, *, entity: VaultEntity):
        """
        Creates an entry inside password vault db.
        If given, special UID field will be inserted inside entity.

        Raises:
            EmptyRecordInsertionError: Raises if trying to insert an empty record.
        """

        if entity.is_empty():
            raise EmptyRecordInsertionError('Cannot insert empty record into vault table.')
        entity[const.UID_FIELD] = __uid
        return self.repo.create(entity)

    def read_vault_entry(self, __uid=None, *, crit: VaultEntity = None, pk: Any = None):
        """
        Reads an entry from password vault.
        If given, special UID field will be inserted inside entity criteria.
        Accepts only one of crit or pk at a time.

        Raises:
            EmptyQueryError: Raises if trying to query without any conditions.
            RecordNotFoundError: Raises if record could not be found in vault.
        """

        assert crit is None or pk is None, 'Only one of `crit` or `pk` should be passed.'
        if crit is None and pk is None:
            raise EmptyQueryError('Both params `crit` and `pk` should not be None.')
        if __uid is not None:
            crit[const.UID_FIELD] = __uid
        if pk is None:
            item = self.repo.find_by_id(pk)
            if item[const.UID_FIELD] != __uid:
                raise RecordNotFoundError(f'Requested record with criteria {crit} and pk {pk} not found.')
            return item
        return self.repo.find_one(crit)

    def read_vault_entries(self, __uid=None, *, crit: VaultEntity = None, pks: Iterable = None):
        """
        Reads multiple entries from password vault based on given conditions.
        If given, special UID field will be inserted inside entity criteria.

        Raises:
            EmptyQueryError: Raises if trying to query without any conditions.
        """

        if crit is None and pks is None:
            raise EmptyQueryError('Both params `crit` and `pks` should not be None.')
        if __uid is not None:
            crit[const.UID_FIELD] = __uid
        return self.repo.find(pks, crit=crit)

    def update_vault_entry( self, __uid=None, *, update: VaultEntity, pk: Any):
        """
        Updates entry based on given conditions and update object.
        If given, special UID field will be inserted inside entity criteria.
        Also, responsible for removing specified keys with a value of operator.DEL.

        Returns:
            Updated id.

        Raises:
            RecordNotFoundError: Raises only if no record found based on given conditions.
            TypeError: Raises only if trying to update special UID field.
        """

        if const.UID_FIELD in update:
            raise TypeError('Update object cannot contain a new user id field.')

        item = self.repo.find_by_id(pk)
        if item[const.UID_FIELD] != __uid:
            raise RecordNotFoundError(f'Requested record with pk {pk} not found.')

        del_fields = set([k for k, v in item.items() if v == DEL])
        protected_fields = item.get(const.PROTECTED_FIELD, [])
        protected_fields = [pf for pf in protected_fields if pf not in del_fields]
        if len(protected_fields) <= 0:
            update[const.PROTECTED_FIELD] = DEL
        else:
            update[const.PROTECTED_FIELD] = protected_fields

        return self.repo.update_by_id(pk, update=update)

    def update_vault_entries(
            self,
            __uid=None,
            *,
            update: VaultEntity,
            crit: VaultEntity = None,
            pks: Iterable = None
    ):
        """
        Updates multiple entries from password vault based on given conditions.
        If given, special UID field will be inserted inside entity criteria.
        Also, responsible for removing specified keys with a value of operator.DEL.

        Returns:
            Iterable of updated id.

        Raises:
            TypeError: Raises only if trying to update special UID field.
        """

        items = self.read_vault_entries(__uid, crit=crit, pks=pks)
        ids = [item.id for item in items]
        updated_ids = [self.update_vault_entry(update=update, pk=pk) for pk in ids]
        return [pk for pk in updated_ids if pk is not None]

    def delete_vault_entry(self, __uid=None, *, pk: Any):
        # check_uid(__uid)
        # cond = create_query_with_uid(__uid, cond)
        # if doc_ids is None:
        #     items = self.dao.delete(cond=cond)
        # else:
        #     docs = self.read_vault_entries(__uid, cond=cond, doc_ids=doc_ids)
        #     items = self.dao.delete(doc_ids=[d[ID_FIELD] for d in docs])
        # return items

        pass

    def delete_vault_entries(self, __uid=None, *, crit: VaultEntity = None, pks: Iterable = None):
        # check_uid(__uid)
        # cond = create_query_with_uid(__uid, cond)
        # if cond is not None:
        #     # check the conditions first, and only delete matching items
        #     item = self.read_vault_entry(__uid, doc_id=doc_id, cond=cond)
        #     if item is not None:
        #         items = self.dao.delete(doc_ids=[doc_id])
        #     else:
        #         items = []
        # else:
        #     items = self.dao.delete(doc_ids=[doc_id])
        # try:
        #     return items[0]
        # except IndexError:
        #     return None

        pass

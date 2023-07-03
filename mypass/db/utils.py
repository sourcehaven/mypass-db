from typing import Literal, Callable, Any, Iterable

from mypass.exceptions import MasterPasswordExistsError, UserNotExistsError, InvalidUpdateError, RequiresIdError, \
    EmptyRecordInsertionError, EmptyQueryError, RecordNotFoundError
from mypass.types import MasterEntity, VaultEntity
from mypass.types import const
from mypass.utils import gen_uuid
from .repository import CrudRepository


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
    def __init__(self, repo: CrudRepository, nosafe: bool = False):
        self.repo = repo
        self._nosafe = nosafe

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

    def read_master_password(self, __uid):
        """
        Reads the master password of a given user.

        Returns:
            str: Password part of the entity. Only a string is returned.
        Raises:
            UserNotExistsError - Raises only if the given user does not exist in the db.
        """

        if isinstance(__uid, self.repo.id_cls):
            item = self.repo.find_by_id(__uid)
            if item is None:
                raise UserNotExistsError(f'User with id {__uid} could not be found.')
            return item.pw
        raise TypeError(f'Parameter __uid should be of type {self.repo.id_cls}.')

    def update_master_password(self, __uid, update: MasterEntity):
        """
        Updates master password for a given user id.

        Returns:
            str | int: Updated id.
        Raises:
            TypeError: Only if param user_or_uid is not an accepted user
        """

        if 'user' in update or 'token' in update:
            raise InvalidUpdateError('User and master token cannot be updated inside master vault.')
        if isinstance(__uid, self.repo.id_cls):
            item = self.repo.update_by_id(__uid, update=update)
            if item is None:
                raise UserNotExistsError(f'User with id {__uid} could not be found.')
            return item
        raise TypeError(f'Parameter __uid should be of type {self.repo.id_cls}.')


class VaultDbSupport:
    def __init__(self, repo: CrudRepository, nosafe: bool = False):
        self.repo = repo
        self._nosafe = nosafe

    def create_vault_entry(self, __uid=None, *, entity: VaultEntity):
        """
        Creates an entry inside password vault db.
        If given, special UID field will be inserted inside entity.

        Raises:
            EmptyRecordInsertionError: Raises if trying to insert an empty record.

        Returns:
            str | int: Identification of the created entry.
        """

        if entity.is_empty():
            raise EmptyRecordInsertionError('Cannot insert empty record into vault table.')
        if __uid is not None:
            entity[const.UID_FIELD] = __uid
        try:
            return self.repo.create(entity=entity)
        except RequiresIdError:
            entity.id = gen_uuid(self.repo.id_cls.__class__.__name__)
            return self.repo.create(entity=entity)

    def read_vault_entry(self, __uid=None, *, crit: VaultEntity = None, pk: Any = None):
        """
        Reads an entry from password vault.
        If given, special UID field will be inserted inside entity criteria.
        Accepts only one of crit or pk at a time.

        Raises:
            EmptyQueryError: Raises if trying to query without any conditions.
            RecordNotFoundError: Raises if record could not be found in vault.

        Returns:
            VaultEntity: Vault entity.
        """

        assert crit is None or pk is None, 'Only one of `crit` or `pk` should be passed.'
        if crit is None and pk is None:
            raise EmptyQueryError('Both params `crit` and `pk` should not be None.')
        if __uid is not None:
            if crit is None:
                crit = VaultEntity()
            crit[const.UID_FIELD] = __uid
        if pk is not None:
            item = self.repo.find_by_id(pk)
            if item is None or (__uid is not None and item[const.UID_FIELD] != __uid):
                raise RecordNotFoundError(f'Requested record with criteria {crit} and pk {pk} not found.')
            return item
        item = self.repo.find_one(crit)
        if item is None:
            raise RecordNotFoundError(f'Requested record with criteria {crit} not found.')
        return item

    def read_vault_entries(self, __uid=None, *, crit: VaultEntity = None, pks: Iterable = None):
        """
        Reads multiple entries from password vault based on given conditions.
        If given, special UID field will be inserted inside entity criteria.

        Raises:
            EmptyQueryError: Raises if trying to query without any conditions.

        Returns:
            Iterable[VaultEntity]: The vault entities found based on given conditions.
        """

        if crit is None and pks is None:
            raise EmptyQueryError('Both params `crit` and `pks` should not be None.')
        if __uid is not None:
            if crit is None:
                crit = VaultEntity()
            crit[const.UID_FIELD] = __uid
        if pks is not None and crit is not None:
            return self.repo.find(pks, crit=crit)
        if pks is not None:
            return self.repo.find_by_ids(pks)
        if crit is not None:
            return self.repo.find_by_crit(crit=crit)

    def update_vault_entry(self, __uid=None, *, update: VaultEntity, pk: Any):
        """
        Updates entry based on given conditions and update object.
        If given, special UID field will be inserted inside entity criteria.
        Also, responsible for removing specified keys with a value of operator.DEL.

        Returns:
            str | int: Updated id.

        Raises:
            RecordNotFoundError: Raises only if no record found based on given conditions.
            TypeError: Raises only if trying to update special UID field.
        """

        if const.UID_FIELD in update:
            raise TypeError('Update object cannot contain a new user id field.')

        item = self.repo.find_by_id(pk)
        if item is None or (__uid is not None and item[const.UID_FIELD] != __uid):
            raise RecordNotFoundError(f'Requested record with pk {pk} not found.')

        item = self.repo.update_by_id(pk, update=update)
        if item is None:
            raise RecordNotFoundError(f'Requested record with pk {pk} not found.')
        return item

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
            Iterable[str] | Iterable[int]: Iterable of updated ids.

        Raises:
            TypeError: Raises only if trying to update special UID field.
        """

        if const.UID_FIELD in update:
            raise TypeError('Update object cannot contain a new user id field.')

        if __uid is not None:
            if crit is None:
                crit = VaultEntity()
            crit[const.UID_FIELD] = __uid

        if crit is not None and pks is not None:
            return self.repo.update(pks, crit=crit, update=update)
        if crit is not None:
            return self.repo.update_by_crit(crit=crit, update=update)
        if pks is not None:
            return self.repo.update_by_ids(pks, update=update)
        return self.repo.update_all(update)

    def delete_vault_entry(self, __uid=None, *, pk: Any):
        """
        Deletes a single vault entry.

        Returns:
            str | int: Deleted record's id.

        Raises:
            RecordNotFoundError: If requested record to be deleted does not exist.
        """
        item = self.repo.find_by_id(pk)
        if item is None or (__uid is not None and item[const.UID_FIELD] != __uid):
            raise RecordNotFoundError(f'Requested record with pk {pk} not found.')
        return self.repo.remove_by_id(pk)

    def delete_vault_entries(self, __uid=None, *, crit: VaultEntity = None, pks: Iterable = None):
        """
        Deletes multiple entries from vault based on given conditions.

        Returns:
            Iterable[str] | Iterable[int]: Ids of successfully deleted items.

        Raises:
            TypeError: Raises only if operation is unsafe, or not allowed.
        """

        if __uid is not None:
            if crit is None:
                crit = VaultEntity()
            crit[const.UID_FIELD] = __uid

        if crit is not None and pks is not None:
            return self.repo.remove(pks, crit=crit)
        if crit is not None:
            return self.repo.remove_by_crit(crit=crit)
        if pks is not None:
            return self.repo.remove_by_ids(pks)
        if self._nosafe:
            self.repo.remove_all()
        else:
            raise TypeError('Deleting multiple entries without any criteria (truncation) is not allowed.')

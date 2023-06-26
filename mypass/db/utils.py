from typing import Literal, Callable, Any, TypeVar, Iterable

from mypass.exceptions import MasterPasswordExistsError, UserNotExistsError, InvalidUpdateError, RequiresIdError
from mypass.types import MasterEntity, VaultEntity
from .repository import CrudRepository
from ..utils import gen_uuid


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


_T = TypeVar('_T')


class MasterDbSupport:
    def __init__(self, repo: CrudRepository):
        self.repo = repo

    def create_master_password(self, entity: MasterEntity) -> None:
        item = self.repo.find_one(entity=MasterEntity(user=entity.user))
        if item is None:
            try:
                self.repo.create(entity=entity)
            except RequiresIdError:
                entity.id = gen_uuid(self.repo.id_cls.__class__.__name__)
        raise MasterPasswordExistsError('Trying to store multiple master passwords for the same user.')

    def read_master_password(self, user_or_uid):
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

    def update_master_password(self, user_or_uid, update: MasterEntity) -> None:
        if 'user' in update or 'token' in update:
            raise InvalidUpdateError('User and master token cannot be updated inside master vault.')
        if isinstance(user_or_uid, self.repo.id_cls):
            self.repo.update_by_id(user_or_uid, update=update)
        elif isinstance(user_or_uid, str):
            self.repo.update_by_crit(
                crit=MasterEntity(user=user_or_uid), update=MasterEntity(user=user_or_uid))
        else:
            raise TypeError(f'Parameter user_or_uid should be either of type {str} or {self.repo.id_cls}.')


class VaultDbSupport:
    def create_vault_entry(self, __uid: int = None, *, entity: VaultEntity):
        pass

    def read_vault_entries(self, __uid: int | str = None, *, crit: VaultEntity = None, doc_ids: Iterable[int] = None):
        pass

    def read_vault_entry(self, __uid: int = None, *, crit: VaultEntity = None, doc_id: int = None):
        pass

    def update_vault_entry(
            self,
            __uid: int = None,
            *,
            update: VaultEntity,
            crit: VaultEntity = None,
            doc_id: int
    ):
        pass

    def update_vault_entries(
            self,
            __uid: int = None,
            *,
            update: VaultEntity,
            crit: VaultEntity = None,
            doc_ids: Iterable[int] = None
    ):
        pass

    def delete_vault_entry(self, __uid: int = None, *, crit: VaultEntity = None, doc_id: int):
        pass

    def delete_vault_entries(self, __uid: int = None, *, crit: VaultEntity = None, doc_ids: Iterable[int] = None):
        pass

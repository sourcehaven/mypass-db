from typing import Literal, Callable, Any, TypeVar, Mapping, Iterable

from mypass.db import CrudRepository
from mypass.exceptions import MasterPasswordExistsError
from mypass.types import MasterVaultEntity


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


class DbSupport:
    def __init__(self, repo: CrudRepository):
        self.repo = repo

    def create_master_password(self, entity: MasterVaultEntity):
        item = self.repo.find(entity=MasterVaultEntity(user=entity.user))
        if item is None:
            return self.repo.create(entity=entity)
        raise MasterPasswordExistsError('Trying to store multiple master passwords for the same user.')

    def read_master_password(self, user_or_uid: str | int) -> _T:
        pass

    def update_master_password(self, user_or_uid: str | int, update: _T) -> int:
        pass

    def create_vault_entry(
            self,
            __uid: int = None,
            *,
            pw: str = None,
            salt: str = None,
            user: str = None,
            label: str = None,
            email: str = None,
            site: str = None,
            **kwargs
    ):
        pass

    def read_vault_entries(self, __uid: int | str = None, *, cond: dict = None, doc_ids: Iterable[int] = None):
        pass

    def read_vault_entry(self, __uid: int = None, *, cond: dict = None, doc_id: int = None):
        pass

    def update_vault_entries(
            self,
            __uid: int = None,
            *,
            fields: Mapping,
            cond: dict = None,
            doc_ids: Iterable[int] = None
    ):
        pass

    def update_vault_entry(
            self,
            __uid: int = None,
            *,
            fields: Mapping,
            cond: dict = None,
            doc_id: int
    ):
        pass

    def delete_vault_entries(self, __uid: int = None, *, cond: dict = None, doc_ids: Iterable[int] = None):
        pass

    def delete_vault_entry(self, __uid: int = None, *, cond: dict = None, doc_id: int):
        pass

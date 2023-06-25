import abc
from typing import TypeVar, Generic, Iterable, Optional

_T = TypeVar('_T')
_ID = TypeVar('_ID')


class CrudRepository(abc.ABC, Generic[_ID, _T]):
    @abc.abstractmethod
    def create(self, entity: _T) -> _ID:
        ...

    @abc.abstractmethod
    def find(self, entity: _T) -> Optional[_T]:
        ...

    @abc.abstractmethod
    def find_by_id(self, __id: _ID) -> Optional[_T]:
        ...

    @abc.abstractmethod
    def find_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_T]:
        ...

    @abc.abstractmethod
    def find_where(self, __ids: Iterable[_ID], entity: _T) -> Iterable[_T]:
        ...

    @abc.abstractmethod
    def update_by_id(self, __id: _ID, update: _T) -> _ID:
        ...

    @abc.abstractmethod
    def update_by_ids(self, __ids: Iterable[_ID], update: _T) -> Iterable[_ID]:
        ...

    @abc.abstractmethod
    def update(self, __ids: Iterable[_ID], entity: _T, update: _T) -> Iterable[_ID]:
        ...

    @abc.abstractmethod
    def remove_by_id(self, __id: _ID) -> _ID:
        ...

    @abc.abstractmethod
    def remove_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_ID]:
        ...

    @abc.abstractmethod
    def remove(self, __ids: Iterable[_ID], entity: _T) -> Iterable[_ID]:
        ...

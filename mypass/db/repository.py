import abc
from typing import TypeVar, Generic, Iterable, Optional

_T = TypeVar('_T')
_ID = TypeVar('_ID')


class CrudRepository(abc.ABC, Generic[_ID, _T]):
    def __init__(self):
        # noinspection PyUnresolvedReferences
        # insane hacking -> get stored entity type from original bases
        generic_info = self.__class__.__orig_bases__[0]
        # by convention, the first parameter will be the type of the id
        self._id_cls: type = generic_info.__args__[0]
        # the second parameter will be the contained type
        self._entity_cls: type = generic_info.__args__[1]

    @property
    def id_cls(self):
        return self._id_cls

    @property
    def entity_cls(self):
        return self._entity_cls

    @abc.abstractmethod
    def create(self, entity: _T) -> _ID:
        """
        Saves the specified entity inside an arbitrary db implementation.
        Implementations requiring an id to be given on creation,
        should raise RequiresIdError, if id is not given with the entity.

        Raises:
            RequiresIdError: raises only if implementation needs an id to be created manually.
        """

    @abc.abstractmethod
    def find_one(self, entity: _T) -> Optional[_T]:
        """Returns exactly one entity based on the specified conditions."""
        ...

    @abc.abstractmethod
    def find_by_id(self, __id: _ID) -> Optional[_T]:
        """Finds an entity by its corresponding id."""
        ...

    @abc.abstractmethod
    def find_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_T]:
        """Finds multiple documents by their ids, and returns them in an iterable."""
        ...

    @abc.abstractmethod
    def find_by_crit(self, crit: _T) -> Iterable[_T]:
        """Finds multiple documents by a given criteria, and returns them in an iterable."""
        ...

    @abc.abstractmethod
    def find(self, __ids: Iterable[_ID], crit: _T) -> Iterable[_T]:
        """Finds multiple documents based on their ids and a given criteria, and returns them in an iterable."""
        ...

    def find_all(self) -> Iterable[_T]:
        """Finds all documents, and returns them in an iterable."""
        ...

    @abc.abstractmethod
    def update_by_id(self, __id: _ID, update: _T) -> Optional[_ID]:
        """Updates an entity by its corresponding id."""
        ...

    @abc.abstractmethod
    def update_by_ids(self, __ids: Iterable[_ID], update: _T) -> Iterable[_ID]:
        """
        Updates multiple documents by given ids,
        and returns the updated ids in an iterable.
        """
        ...

    @abc.abstractmethod
    def update_by_crit(self, crit: _T, update: _T) -> Iterable[_ID]:
        """
        Updates multiple documents by a given criteria,
        and returns the updated ids in an iterable.
        """
        ...

    @abc.abstractmethod
    def update(self, __ids: Iterable[_ID], crit: _T, update: _T) -> Iterable[_ID]:
        """
        Updates multiple documents by given ids and a given criteria,
        and returns the updated ids in an iterable.
        """
        ...

    def update_all(self, update: _T) -> Iterable[_ID]:
        """Updates all documents unconditionally."""
        ...

    @abc.abstractmethod
    def remove_by_id(self, __id: _ID) -> Optional[_ID]:
        """Removes an entity by its corresponding id."""
        ...

    @abc.abstractmethod
    def remove_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_ID]:
        """
        Removes multiple documents by given ids,
        and returns the removed ids in an iterable.
        """
        ...

    @abc.abstractmethod
    def remove_by_crit(self, crit: _T) -> Iterable[_ID]:
        """
        Removes multiple documents by a given criteria,
        and returns the removed ids in an iterable.
        """
        ...

    @abc.abstractmethod
    def remove(self, __ids: Iterable[_ID], crit: _T) -> Iterable[_ID]:
        """
        Removes multiple documents by given ids and a given criteria,
        and returns the removed ids in an iterable.
        """
        ...

    @abc.abstractmethod
    def remove_all(self) -> None:
        """
        Removes all documents.
        """
        ...

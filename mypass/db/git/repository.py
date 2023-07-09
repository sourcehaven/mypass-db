from typing import Iterable, Optional, Generic, TypeVar

from mypass.db.repository import CrudRepository
from mypass.utils import GitSupport

_ID = TypeVar('_ID')
_T = TypeVar('_T')


class GitRepository(CrudRepository, Generic[_ID, _T]):
    def __init__(
            self,
            dao: CrudRepository,
            **git_config
    ):
        super().__init__()
        self.dao = dao
        self.git = GitSupport(**git_config)

    def create(self, entity: _T) -> _ID:
        _id = self.dao.create(entity)
        self.git.stage_commit_push()
        return _id

    def find_one(self, entity: _T) -> Optional[_T]:
        return self.dao.find_one(entity)

    def find_by_id(self, __id: _ID) -> Optional[_T]:
        return self.dao.find_by_id(__id)

    def find_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_T]:
        return self.dao.find_by_ids(__ids)

    def find_by_crit(self, crit: _T) -> Iterable[_T]:
        return self.dao.find_by_crit(crit)

    def find(self, __ids: Iterable[_ID], crit: _T) -> Iterable[_T]:
        return self.dao.find(__ids, crit)

    def find_all(self) -> Iterable[_T]:
        return self.dao.find_all()

    def update_by_id(self, __id: _ID, update: _T) -> Optional[_ID]:
        _id = self.dao.update_by_id(__id, update)
        self.git.stage_commit_push()
        return _id

    def update_by_ids(self, __ids: Iterable[_ID], update: _T) -> Iterable[_ID]:
        _ids = self.dao.update_by_ids(__ids, update)
        self.git.stage_commit_push()
        return _ids

    def update_by_crit(self, crit: _T, update: _T) -> Iterable[_ID]:
        _ids = self.dao.update_by_crit(crit, update)
        self.git.stage_commit_push()
        return _ids

    def update(self, __ids: Iterable[_ID], crit: _T, update: _T) -> Iterable[_ID]:
        _ids = self.dao.update(__ids, crit, update)
        self.git.stage_commit_push()
        return _ids

    def remove_by_id(self, __id: _ID) -> Optional[_ID]:
        _id = self.dao.remove_by_id(__id)
        self.git.stage_commit_push()
        return _id

    def remove_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_ID]:
        _ids = self.dao.remove_by_ids(__ids)
        self.git.stage_commit_push()
        return _ids

    def remove_by_crit(self, crit: _T) -> Iterable[_ID]:
        _id = self.dao.remove_by_crit(crit)
        self.git.stage_commit_push()
        return _id

    def remove(self, __ids: Iterable[_ID], crit: _T) -> Iterable[_ID]:
        _ids = self.dao.remove(__ids, crit)
        self.git.stage_commit_push()
        return _ids

    def remove_all(self) -> None:
        self.dao.remove_all()
        self.git.stage_commit_push()

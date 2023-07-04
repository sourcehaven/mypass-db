from functools import wraps
from os import PathLike
from pathlib import Path

from typing import Iterable, Optional, Generic, TypeVar, Mapping

from mypass.db import CrudRepository
from mypass.exceptions import RequiresIdError
from mypass.types.entity import Entity

from .dao import FileSystemDao

_PATH = TypeVar('_PATH', bound=str)
_T = TypeVar('_T', bound=Mapping)


def requires_id(f):

    def wrapper(self, entity, *args, **kwargs):
        if entity.id:
            return f(self, entity, *args, **kwargs)
        raise RequiresIdError

    return wrapper


def full_path(entity=False):
    def func_dec(fun):
        def get_full_path(root_folder: Path, path: Path):
            if not path.is_absolute():
                path = root_folder / path

            if not path.suffix:
                path = path.with_suffix('.json')
            return path

        @wraps(fun)
        def entity_wrapper(self, e: Entity, *args, **kwargs):
            e.id = get_full_path(self.root_folder, Path(e.id))
            return fun(self, e, *args, **kwargs)

        @wraps(fun)
        def path_wrapper(self, path, *args, **kwargs):
            if isinstance(path, Iterable) and not isinstance(path, (str, bytes)):
                abs_paths = (get_full_path(self.root_folder, Path(p)) for p in path)
                return [fun(self, abs_path, *args, **kwargs) for abs_path in abs_paths]

            path = get_full_path(self.root_folder, Path(path))
            return fun(self, path, *args, **kwargs)

        return entity_wrapper if entity else path_wrapper
    return func_dec


class FileSystemRepository(CrudRepository, Generic[_PATH, _T]):

    def __init__(self, root_folder: str | PathLike, dao: FileSystemDao):
        super().__init__()
        self.root_folder = Path(root_folder)
        assert self.root_folder.is_dir(), f'Path {root_folder} is not a directory!'
        self.dao = dao

    @requires_id
    @full_path(entity=True)
    def create(self, entity: _T) -> _PATH:
        self.dao.create(path=entity.id, data=entity)
        return entity.id

    @full_path(entity=True)
    def find_one(self, crit: _T) -> Optional[_T]:
        entities = self.find_by_crit(crit)
        try:
            return list(entities)[0]
        except IndexError:
            return

    @full_path()
    def find_by_id(self, path: _PATH) -> Optional[_T]:
        return self.dao.read_one(path, into=self.entity_cls)

    @full_path()
    def find_by_ids(self, paths: Iterable[_PATH]) -> Iterable[_T]:
        return self.dao.read(paths, into=self.entity_cls)

    def find_by_crit(self, crit: _T) -> Iterable[_T]:
        paths = self.dao.find_in_folder(self.root_folder, crit=crit)
        return self.dao.read(paths, into=self.entity_cls)

    @full_path()
    def find(self, paths: Iterable[_PATH], crit: _T) -> Iterable[_T]:
        paths = self.dao.find(paths, crit=crit)
        return self.dao.read(paths, into=self.entity_cls)

    @full_path()
    def update_by_id(self, path: _PATH, update: _T) -> Optional[_PATH]:
        self.dao.update_one(path, data=update)
        return path

    @full_path()
    def update_by_ids(self, paths: Iterable[_PATH], update: _T) -> Iterable[_PATH]:
        self.dao.update(paths, data=update)
        return paths

    def update_by_crit(self, crit: _T, update: _T) -> Iterable[_PATH]:
        files_to_update = self.dao.find_in_folder(self.root_folder, crit=crit)
        deleted = self.dao.update(files_to_update, update)
        return [path for path, is_deleted in zip(files_to_update, deleted) if is_deleted]

    @full_path()
    def update(self, paths: Iterable[_PATH], crit: _T, update: _T) -> Iterable[_PATH]:
        files_to_update = self.dao.find(paths, crit=crit)
        deleted = self.dao.update(files_to_update, data=update)
        return [path for path, is_deleted in zip(files_to_update, deleted) if is_deleted]

    @full_path()
    def remove_by_id(self, path: _PATH) -> Optional[_PATH]:
        if self.dao.delete_one(path):
            return path

    @full_path()
    def remove_by_ids(self, paths: Iterable[_PATH]) -> Iterable[_PATH]:
        paths = list(paths)
        deleted = self.dao.delete(paths)
        return [p for d, p in zip(deleted, paths) if d]

    def remove_by_crit(self, crit: _T) -> Iterable[_PATH]:
        files_to_remove = self.dao.find_in_folder(self.root_folder, crit=crit)
        deleted = self.dao.delete(files_to_remove)
        return [path for path, is_deleted in zip(files_to_remove, deleted) if is_deleted]

    @full_path()
    def remove(self, paths: Iterable[_PATH], crit: _T) -> Iterable[_PATH]:
        files_to_remove = self.dao.find(paths, crit=crit)
        deleted = self.dao.delete(files_to_remove)
        return [path for path, is_deleted in zip(paths, deleted) if is_deleted]

    def remove_all(self) -> None:
        self.dao.delete_all(self.root_folder)

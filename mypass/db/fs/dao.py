import json
from os import PathLike
from pathlib import Path
from typing import Iterable, Mapping, Any, Type

from mypass.types import op


def is_subset(dict1, dict2):
    return all(item in dict2.items() for item in dict1.items())


def read(path: str | PathLike, into: Type[Mapping] = None) -> Mapping[str, Any]:
    with open(path, 'r') as f:
        ret: dict[str, Any] = json.load(f)
        assert isinstance(ret, dict), 'The loaded JSON data is not a dictionary.'
    if into:
        ret = into(path, **ret)
    return ret


def find_all_files(path: str | PathLike):
    path_obj = Path(path)
    return [file for file in path_obj.rglob('*') if file.is_file()]


def find_files_by_crit(paths: Iterable[str | PathLike], crit: Mapping):
    data = (read(path) for path in paths)

    return [path for path, data in data if is_subset(crit, data)]


def delete(path: str | PathLike, secure=False):
    path = Path(path)
    if path.is_file():
        if secure:
            with open(path, 'wb') as f:
                f.write(b'\x00' * path.stat().st_size)

        path.unlink()
        return True
    return False


def write(path: str | PathLike, data: Mapping, overwrite=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not overwrite and path.is_file():
        raise FileExistsError(f'File {path.absolute()} already exists and parameter overwrite is False.')

    with open(path, 'w') as f:
        return json.dump(dict(data), f)


def update(path: str | PathLike, new: Mapping):
    path = Path(path)
    curr = read(path)
    curr.update(new)
    curr = {k: v for k, v in curr.items() if v != op.DEL}

    return write(path, curr, overwrite=True)


def update_by_crit(path, crit, data):
    all_file = find_all_files(path)
    files_to_update = find_files_by_crit(all_file, crit=crit)
    for file in files_to_update:
        update(file, data)


class FileSystemDao:

    def create(self, path: str | PathLike[str], data: Mapping):
        return write(path, data, overwrite=False)

    def read_one(self, path: str | PathLike[str], into: Type[Mapping] | None = None):
        return read(path, into=into)

    def read(self, paths: Iterable[str | PathLike[str]], into: Type[Mapping] | None = None):
        return [self.read_one(path, into=into) for path in paths]

    def find_all_files(self, folder: str | PathLike):
        return find_all_files(folder)

    def find(self, paths: Iterable[str | PathLike], crit: Mapping):
        return find_files_by_crit(paths, crit=crit)

    def find_in_folder(self, folder: str | PathLike, crit: Mapping):
        return self.find(self.find_all_files(folder), crit=crit)

    def update_one(self, path: str | PathLike[str], data: Mapping):
        return update(path, data)

    def update(self, paths: Iterable[str | PathLike[str]], data: Mapping):
        return [self.update_one(path, data) for path in paths]

    def delete_one(self, path: str | PathLike[str], secure=False):
        return delete(path, secure=secure)

    def delete(self, paths: Iterable[str | PathLike[str]], secure=False):
        return [self.delete_one(path, secure=secure) for path in paths]

    def delete_all(self, folder: str | PathLike, secure=False, delete_directories=True):
        folder = Path(folder)
        for file_path in folder.glob('*'):
            if file_path.is_file():
                delete(file_path, secure=secure)

        if delete_directories:
            for file_path in folder.glob('*'):
                if file_path.is_dir():
                    file_path.rmdir()

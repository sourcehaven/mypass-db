import os
from typing import TypedDict, Iterable, Optional, Generic
from urllib.parse import urlparse

from git import InvalidGitRepositoryError, Repo

from mypass.db.repository import CrudRepository, _ID, _T


_T_AUTH = TypedDict('_T_AUTH', {'username': str, 'access_token': str})


def get_staged_files(repo: Repo):
    git_cmd = repo.git
    statuses = git_cmd.status('--porcelain')

    def split_status(lines: str):
        for line in lines.splitlines():
            status, path = line.split(maxsplit=1)
            yield path, status

    return dict(split_status(statuses))


def configure_remote_with_auth(remote_url: str, auth: _T_AUTH):
    if auth is not None:
        remote_url = urlparse(remote_url)
        if remote_url.scheme != '':
            remote_url = ''.join(
                [f'{remote_url[0]}://{auth["username"]}:{auth["access_token"]}@'] + remote_url[1:])
        remote_url = str(remote_url)
    return remote_url


class GitRepository(CrudRepository, Generic[_ID, _T]):

    @staticmethod
    def is_git_repo(path: str | os.PathLike):
        try:
            Repo(path)
            return True
        except InvalidGitRepositoryError:
            return False

    @staticmethod
    def init(
            path: str | os.PathLike,
            name: str,
            email: str,
            branch='main'
    ):
        repo = Repo.init(path, initial_branch=branch)

        with repo.config_writer() as conf:
            conf.set_value('user', 'name', name)
            conf.set_value('user', 'email', email)

    def __init__(
            self,
            db: CrudRepository,
            path: str | os.PathLike,
    ):
        super().__init__()
        self.db = db
        self.repo = Repo(path)

    def rm_cached(self):
        self.repo.git.rm('--cached', '-r', self.repo.working_dir)

    def add_remote(self, url: str, name: str = 'origin', auth: _T_AUTH = None):
        remote_url = configure_remote_with_auth(url, auth)
        self.repo.create_remote(name=name, url=remote_url)

    def add_all(self):
        untracked_files = self.repo.untracked_files
        changed_files = [item.a_path for item in self.repo.index.diff(None)]
        self.repo.index.add(untracked_files + changed_files)

    def commit(self):
        staged_files = get_staged_files(self.repo)
        message = f"Committed changes:\n" + "\n".join(f"{status} {path}" for path, status in staged_files.items())
        self.repo.index.commit(message)

    def push(self):
        for remote in self.repo.remotes:
            remote.push(refspec=f'{self.active_branch}:{remote.name}')

    def stage_commit_push(self):
        self.add_all()
        self.commit()
        self.push()

    @property
    def active_branch(self):
        return self.repo.active_branch

    def __enter__(self):
        return self.repo

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.repo.close()

    def create(self, entity: _T) -> _ID:
        _id = self.db.create(entity)
        self.stage_commit_push()
        return _id

    def find_one(self, entity: _T) -> Optional[_T]:
        return self.db.find_one(entity)

    def find_by_id(self, __id: _ID) -> Optional[_T]:
        return self.db.find_by_id(__id)

    def find_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_T]:
        return self.db.find_by_ids(__ids)

    def find_by_crit(self, crit: _T) -> Iterable[_T]:
        return self.db.find_by_crit(crit)

    def find(self, __ids: Iterable[_ID], crit: _T) -> Iterable[_T]:
        return self.db.find(__ids, crit)

    def update_by_id(self, __id: _ID, update: _T) -> Optional[_ID]:
        _id = self.db.update_by_id(__id, update)
        self.stage_commit_push()
        return _id

    def update_by_ids(self, __ids: Iterable[_ID], update: _T) -> Iterable[_ID]:
        _ids = self.db.update_by_ids(__ids, update)
        self.stage_commit_push()
        return _ids

    def update_by_crit(self, crit: _T, update: _T) -> Iterable[_ID]:
        _ids = self.db.update_by_crit(crit, update)
        self.stage_commit_push()
        return _ids

    def update(self, __ids: Iterable[_ID], crit: _T, update: _T) -> Iterable[_ID]:
        _ids = self.db.update(__ids, crit, update)
        self.stage_commit_push()
        return _ids

    def remove_by_id(self, __id: _ID) -> Optional[_ID]:
        _id = self.db.remove_by_id(__id)
        self.stage_commit_push()
        return _id

    def remove_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_ID]:
        _ids = self.db.remove_by_ids(__ids)
        self.stage_commit_push()
        return _ids

    def remove_by_crit(self, crit: _T) -> Iterable[_ID]:
        _id = self.db.remove_by_crit(crit)
        self.stage_commit_push()
        return _id

    def remove(self, __ids: Iterable[_ID], crit: _T) -> Iterable[_ID]:
        _ids = self.db.remove(__ids, crit)
        self.stage_commit_push()
        return _ids

    def remove_all(self) -> None:
        self.db.remove_all()
        self.stage_commit_push()

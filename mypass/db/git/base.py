import os
from pathlib import Path
from typing import Sequence, TypedDict
from urllib.parse import urlparse

from git import InvalidGitRepositoryError, Repo

REPO_PATH = '.db'
NAME = 'db-agent'
EMAIL = 'db.agent@mail.com'
INITIAL_BRANCH = 'main'

_T_AUTH = TypedDict('_T_AUTH', {'username': str, 'access_token': str})


def configure_remote_with_auth(remote_url: str, auth: _T_AUTH):
    if auth is not None:
        remote_url = urlparse(remote_url)
        if remote_url.scheme != '':
            remote_url = ''.join(
                [f'{remote_url[0]}://{auth["username"]}:{auth["access_token"]}@'] + remote_url[1:])
        remote_url = str(remote_url)
    return remote_url


class GitRepoBase:
    def __init__(
            self,
            path: str | os.PathLike = None,
            name: str = None,
            email: str = None,
            branch: str = None,
            remote: str = None,
            remote_url: str = None,
            auth: _T_AUTH = None
    ):
        if REPO_PATH is None:
            path = REPO_PATH
        if name is None:
            name = NAME
        if email is None:
            email = EMAIL
        if branch is None:
            branch = INITIAL_BRANCH

        repo_path = Path(path)
        try:
            self.repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            self.repo = Repo.init(repo_path, initial_branch=branch)

        with self.repo.config_writer() as conf:
            conf.set_value('user', 'name', name)
            conf.set_value('user', 'email', email)

        assert remote is None or remote_url is not None, 'Specifying `remote` without `remote_url` is invalid.'
        if remote_url is not None and remote is None:
            remote = 'origin'
            print(f'USER WARNING :: Only `remote_url` specified. Defaulting remote to {remote}.')
        if remote_url is not None:
            remote_url = configure_remote_with_auth(remote_url, auth)
            self.repo.create_remote(remote, remote_url)

    def commit(self, paths: Sequence[str]):
        self.repo.index.add(paths)
        changed_files = ', '.join([path for path in paths])
        self.repo.index.commit(f'Committing changes for {changed_files}.')

    def push(self):
        remote = self.repo.remote()
        remote.push()

    def __enter__(self):
        return self.repo

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.repo.close()

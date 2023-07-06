import os
from typing import TypedDict
from urllib.parse import urlparse

from git import InvalidGitRepositoryError, Repo

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
    def __init__(self, path=None, name=None, email=None, *, branch=None, remote=None, remote_url=None, auth=None):
        """
        Simple utility class for adding, committing, and optionally pushing to a remote repository.
        Helps with the management of repositories.

        Parameters:
            path (str | os.PathLike): Path of the local repository.
                If `None` is given, will try to read the path from os environment 'GIT_DIR'.
                Defaults to `None`.
            name (str): Config param for **git config user.name {name}**.
                Defaults to 'db-agent' (`NAME`).
            email (str): Config param for **git config user.email {email}**.
                Defaults to 'db.agent@mail.com' (`EMAIL`).
            branch (str): Root branch to use. Defaults to 'main' (`INITIAL_BRANCH`).
            remote (str): Name of the remote. Usually 'origin', which is also the default if not specified.
            remote_url (str): Remote repository url.
            auth (_T_AUTH): Authorization information. Contains your username, and access_token.
        """

        if name is None:
            name = NAME
        if email is None:
            email = EMAIL
        if branch is None:
            branch = INITIAL_BRANCH
        self.remote = remote

        try:
            self.repo = Repo(path)
        except InvalidGitRepositoryError:
            self.repo = Repo.init(path, initial_branch=branch)

        with self.repo.config_writer() as conf:
            conf.set_value('user', 'name', name)
            conf.set_value('user', 'email', email)

        assert remote is None or remote_url is not None, 'Specifying `remote` without `remote_url` is invalid.'
        if remote_url is not None and remote is None:
            self.remote = 'origin'
            print(f'USER WARNING :: Only `remote_url` specified. Defaulting remote to {self.remote}.')
        if remote_url is not None and self.remote not in self.repo.remotes:
            if auth is not None:
                remote_url = configure_remote_with_auth(remote_url, auth)
            self.repo.create_remote(self.remote, remote_url)

    def rm_cached(self):
        self.repo.git.rm('--cached', '-r', self.repo.working_dir)

    def add_commit(self):
        untracked_files = self.repo.untracked_files
        diffs = self.repo.index.diff(None)
        diff_files = [diff.a_path for diff in diffs]  # TODO: should store change type?
        changed_files = untracked_files + diff_files
        self.repo.git.add(all=True)
        changed_files_repr = ', '.join([ufile for ufile in changed_files])
        self.repo.index.commit(f'Committing changes for: {changed_files_repr}.')

    def push(self):
        remote = self.repo.remote(self.remote)
        remote.push(refspec=f'{self.active_branch}:{remote.name}')

    @property
    def active_branch(self):
        return self.repo.active_branch

    def __enter__(self):
        return self.repo

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.repo.close()

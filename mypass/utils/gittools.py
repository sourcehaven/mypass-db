import os
from typing import TypedDict, overload, NotRequired
from urllib.parse import urlparse

from git import InvalidGitRepositoryError, Repo


class _Auth(TypedDict):
    username: str
    access_token: str


class _RemoteConfSingle(TypedDict, total=False):
    name: NotRequired[str]
    url: str
    auth: NotRequired[_Auth]


class _RemoteConfMulty(TypedDict, total=False):
    name: str
    url: str
    auth: NotRequired[_Auth]


NAME = 'db-agent'
EMAIL = 'db.agent@mail.com'
INITIAL_BRANCH = 'main'
REMOTE = 'origin'


def get_staged_files(repo: Repo):
    statuses = repo.git.status('--porcelain').splitlines()
    return dict([status.split(maxsplit=1)[::-1] for status in statuses])


def configure_remote_with_auth(remote_url: str, auth: _Auth):
    assert auth is not None, 'Parameter `auth` should not be None.'
    parsed_url = urlparse(remote_url)
    if parsed_url.scheme != '':
        remote_url_with_auth = ''.join(
            [f'{parsed_url[0]}://{auth["username"]}:{auth["access_token"]}@'] + parsed_url[1:])
        return remote_url_with_auth
    return remote_url


def init_or_get_repo(path, branch=None):
    """
    Initializes a new repo if it does not exist under the specified path,
    returns the found repository otherwise.

    Parameters:
        path (str): Path of the new or the existing repository.
        branch (str): Initial branch name for the new repository.

    Returns:
        Newly initialized or existing repository.
    """
    try:
        repo = Repo(path)
        if branch is not None and repo.active_branch != branch:
            print(f'USER WARNING :: Existing repository branch {repo.active_branch} != {branch}.')
        return repo
    except InvalidGitRepositoryError:
        return Repo.init(path, initial_branch=branch)


class GitSupport:
    @overload
    def __init__(
            self,
            path=None,
            name=None,
            email=None,
            *,
            branch=None,
            remote_config: _RemoteConfSingle = None
    ):
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
            remote_config (_RemoteConfSingle): Configuration dictionary for remote.
        """

    @overload
    def __init__(
            self,
            path=None,
            name=None,
            email=None,
            *,
            branch=None,
            remote_configs: list[_RemoteConfMulty] = None
    ):
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
            remote_configs (list[_RemoteConfMulty]): List of remote configuration dictionaries.
        """

    def __init__(self, path=None, name=None, email=None, *, branch=None, remote_config=None, remote_configs=None):
        assert remote_config is None or remote_configs is None, \
            'Parameters remote_config and remote_configs cannot be specified at the same time.'

        if name is None:
            name = NAME
        if email is None:
            email = EMAIL
        if branch is None:
            branch = INITIAL_BRANCH

        if isinstance(remote_config, dict):
            if remote_config.get('name', None) is None:
                remote_config['name'] = REMOTE
            remote_configs = [remote_config]
        if remote_configs is None:
            remote_configs = []

        self.repo = init_or_get_repo(path, branch)
        self._config_user(name=name, email=email)
        for cfg in remote_configs:
            if cfg['name'] not in self.repo.remotes:
                self.add_remote(cfg['name'], cfg['url'], auth=cfg.get('auth', None))

    def _config_user(self, name, email):
        with self as r:
            with r.config_writer() as conf:
                conf.set_value('user', 'name', name)
                conf.set_value('user', 'email', email)

    def rm_cached(self):
        with self as r:
            r.git.rm('--cached', '-r', self.repo.working_dir)

    def add_remote(self, name: str, url: str, auth: _Auth = None):
        if auth is not None:
            url = configure_remote_with_auth(url, auth)
        with self as r:
            r.create_remote(name=name, url=url)

    def add_all(self):
        with self as r:
            r.git.add(all=True)

    def commit(self):
        with self as r:
            staged_files = get_staged_files(r)
            message = 'Committed changes:\n' + '\n'.join(
                f'    {path} -- {status}' for path, status in staged_files.items())
            r.index.commit(message)

    def add_commit(self):
        self.add_all()
        self.commit()

    def push(self):
        with self as r:
            for remote in r.remotes:
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

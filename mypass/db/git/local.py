import os
from typing import Sequence

from git import Repo, InvalidGitRepositoryError


class GitRepo:

    def __init__(self, path=os.getcwd(), user_email: str = None, user_name: str = None):
        try:
            self.repo = Repo(path)
        except InvalidGitRepositoryError:
            self.repo = Repo.init(path)

        if user_email is not None:
            self.user_email = user_email
        if user_name is not None:
            self.user_name = user_name

    def commit(self, rel_paths: Sequence[str]):
        self.repo.index.add(rel_paths)

        changed_files = ', '.join([path for path in rel_paths])
        self.repo.index.commit(f'Committing changes for {changed_files}')

    @property
    def user_name(self) -> str:
        return self.repo.config_reader().get_value('user', 'name')

    @user_name.setter
    def user_name(self, value: str):
        self.repo.config_writer().set_value('user', 'name', value)

    @property
    def user_email(self) -> str:
        return self.repo.config_reader().get_value('user', 'email')

    @user_email.setter
    def user_email(self, value: str):
        self.repo.config_writer().set_value('user', 'email', value)

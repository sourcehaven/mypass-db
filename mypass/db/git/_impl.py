from typing import Any

from mypass.types import MasterEntity, VaultEntity
from .repository import GitRepository


class MasterGitRepository(GitRepository[int | str, MasterEntity]):
    pass


class VaultGitRepository(GitRepository[int | str, VaultEntity]):
    pass

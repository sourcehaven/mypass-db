from typing import Any

from mypass.types import MasterEntity, VaultEntity
from .repository import GitRepository


class MasterGitRepository(GitRepository[Any, MasterEntity]):
    pass


class VaultGitRepository(GitRepository[Any, VaultEntity]):
    pass

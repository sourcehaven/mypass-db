from mypass.types import MasterEntity, VaultEntity
from .repository import TinyRepository


class MasterTinyRepository(TinyRepository[int, MasterEntity]):
    pass


class VaultTinyRepository(TinyRepository[int, VaultEntity]):
    pass

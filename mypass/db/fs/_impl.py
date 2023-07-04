from mypass.types import MasterEntity, VaultEntity
from .repository import FileSystemRepository


class MasterFileSystemRepository(FileSystemRepository[str, MasterEntity]):
    pass


class VaultFileSystemRepository(FileSystemRepository[str, VaultEntity]):
    pass

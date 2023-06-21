import shutil
from pathlib import Path

# noinspection PyPackageRequirements
from assertpy import assert_that
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from mypass.db.tiny import MasterDao, VaultDao
from tests._utils import AtomicMemoryStorage, persistent_storage

DB_PATH = str(Path.home().joinpath('.mypass/tests/db/tiny/db.json'))


class TestTinyDao:
    def test_connection(self):
        dao = MasterDao(storage=AtomicMemoryStorage)
        with dao.get_connection() as db:
            assert_that(db).is_instance_of(TinyDB)

    def test_init_db(self):
        dao = MasterDao(storage=AtomicMemoryStorage)
        dao.init_db()

    def test_db_unlink(self):
        dao = MasterDao(storage=AtomicMemoryStorage)
        dao.unlink()


class TestMasterDao:
    def test_create(self):
        entry_id1 = self.dao.create('mypass-user1', 'secret-token-1', 'secret-pw-1', 'salt')
        assert_that(entry_id1).is_type_of(int)
        entry_id2 = self.dao.create('mypass-user2', 'secret-token-2', 'secret-pw-2', 'salt')
        assert_that(entry_id2).is_type_of(int)
        assert_that(persistent_storage.data).contains_key('master')
        master_table = persistent_storage['master']
        assert_that(master_table).contains_key(str(entry_id1))
        assert_that(master_table).contains_key(str(entry_id2))

    @classmethod
    def setup_class(cls):
        cls.dao = MasterDao(storage=AtomicMemoryStorage)


class TestVaultDao:
    def test_create(self):
        vault_crud.create()

    @classmethod
    def setup_class(cls):
        cls.dao = VaultDao(storage=MemoryStorage)

    @classmethod
    def teardown_class(cls):
        if Path(DB_PATH).exists():
            shutil.rmtree(DB_PATH)

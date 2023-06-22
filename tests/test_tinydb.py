# noinspection PyPackageRequirements
from assertpy import assert_that
from tinydb import TinyDB

from mypass.db.tiny import MasterDao, VaultDao
# noinspection PyProtectedMember
from mypass.db.tiny._dao import TinyDao
from tests._utils import AtomicMemoryStorage, persistent_storage


class TinyDaoImpl(TinyDao):
    def create(self, *args, **kwargs):
        pass

    def read_one(self, *args, **kwargs):
        pass

    def read(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def delete_all(self, *args, **kwargs):
        pass


class TestTinyDao:
    def test_connection(self):
        dao = TinyDaoImpl(storage=AtomicMemoryStorage)
        with dao.get_connection() as db:
            assert_that(db).is_instance_of(TinyDB)

    def test_init_db(self):
        dao = TinyDaoImpl(storage=AtomicMemoryStorage)
        dao.init_db()

    def test_db_unlink(self):
        dao = TinyDaoImpl(storage=AtomicMemoryStorage)
        dao.unlink()


class TestMasterDao:
    def test_create(self):
        entry_id1 = self.dao.create('mypass-user1', 'secret-token-1', 'secret-pw-1', 'salt')
        assert_that(entry_id1).is_type_of(int)
        entry_id2 = self.dao.create('mypass-user2', 'secret-token-2', 'secret-pw-2', 'salt')
        assert_that(entry_id2).is_type_of(int)
        assert_that(persistent_storage.data).contains_key(self.dao.table)
        master_table = persistent_storage[self.dao.table]
        assert_that(master_table).contains_key(str(entry_id1))
        assert_that(master_table).contains_key(str(entry_id2))

    @classmethod
    def setup_class(cls):
        cls.dao = MasterDao(storage=AtomicMemoryStorage)

    @classmethod
    def teardown_class(cls):
        persistent_storage.clear()


class TestVaultDao:
    def test_create(self):
        entry_id1 = self.dao.create(user='mypass-user1', pw='secret-pw-1', _salt='salt')
        assert_that(entry_id1).is_type_of(int)
        entry_id2 = self.dao.create(
            user='mypass-user2', pw='secret-pw-2', _salt='salt', email='user@mail.com', site='http://localhost/app')
        assert_that(entry_id2).is_type_of(int)
        assert_that(persistent_storage.data).contains_key(self.dao.table)
        master_table = persistent_storage[self.dao.table]
        assert_that(master_table).contains_key(str(entry_id1))
        assert_that(master_table).contains_key(str(entry_id2))

    @classmethod
    def setup_class(cls):
        cls.dao = VaultDao(storage=AtomicMemoryStorage)

    @classmethod
    def teardown_class(cls):
        persistent_storage.clear()

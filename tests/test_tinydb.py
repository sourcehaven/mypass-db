# noinspection PyPackageRequirements
from assertpy import assert_that
from tinydb import TinyDB

from mypass.db.tiny import TinyDao
from mypass.types.op import DEL
from tests._utils import AtomicMemoryStorage, persistent_storage


class TestTinyDao:
    def test_connection(self):
        dao = TinyDao(table='test-table', storage=AtomicMemoryStorage)
        with dao.get_connection() as db:
            assert_that(db).is_instance_of(TinyDB)

    def test_init_db(self):
        dao = TinyDao(table='test-table', storage=AtomicMemoryStorage)
        dao.init_db()

    def test_db_unlink(self):
        dao = TinyDao(table='test-table', storage=AtomicMemoryStorage)
        dao.unlink()

    def test_create(self):
        entry_id1 = self.dao.create(entity=dict(
            user='mypass-user1', token='secret-token-1', pw='secret-pw-1', salt='salt'))
        assert_that(entry_id1).is_type_of(int)
        entry_id2 = self.dao.create(entity=dict(
            user='mypass-user2', token='secret-token-2', pw='secret-pw-2', salt='salt'))
        assert_that(entry_id2).is_type_of(int)
        assert_that(persistent_storage.data).contains_key(self.dao.table)
        table = persistent_storage[self.dao.table]
        assert_that(table).contains_key(str(entry_id1))
        assert_that(table).contains_key(str(entry_id2))

    def test_update(self):
        entry_id1 = self.dao.update(entity=dict(
            user='mypass-user3', token='secret-token-3', pw=DEL), doc_ids=[1])[0]
        assert_that(entry_id1).is_type_of(int)
        entry_id2 = self.dao.update(entity=dict(
            user='mypass-user4', token='secret-token-4', pw='secret-pw-4', salt='salted'), doc_ids=[2])[0]
        assert_that(entry_id2).is_type_of(int)
        doc1 = self.dao.read(doc_ids=[1])[0]
        assert_that(doc1).does_not_contain_key('pw')

    @classmethod
    def setup_class(cls):
        cls.dao = TinyDao('test-table', storage=AtomicMemoryStorage)

    @classmethod
    def teardown_class(cls):
        persistent_storage.clear()

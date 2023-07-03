# noinspection PyPackageRequirements
import pytest
# noinspection PyPackageRequirements
from assertpy import assert_that

from _utils import AtomicMemoryStorage, persistent_storage
from mypass.db import MasterDbSupport, VaultDbSupport
from mypass.db.tiny import MasterTinyRepository, VaultTinyRepository
from mypass.exceptions import MasterPasswordExistsError, UserNotExistsError, InvalidUpdateError, \
    EmptyRecordInsertionError, RecordNotFoundError, EmptyQueryError
from mypass.types import MasterEntity, VaultEntity
from mypass.types.const import UID_FIELD
from mypass.types.op import DEL


class TestMasterDbSupport:
    @pytest.mark.dependency()
    def test_create(self):
        pk1 = self.dbsupport.create_master_password(self.objects[0])
        assert_that(pk1).is_type_of(self.dbsupport.repo.id_cls)
        pk2 = self.dbsupport.create_master_password(self.objects[1])
        assert_that(pk2).is_not_equal_to(pk1)
        self.dbsupport.create_master_password(self.objects[2])

    @pytest.mark.dependency(depends=['TestMasterDbSupport::test_create'])
    def test_records(self):
        assert_that(persistent_storage).contains_key('test-table')
        table = persistent_storage['test-table']
        assert_that(table).contains_key(str(self.objects[0].id), str(self.objects[1].id), str(self.objects[2].id))
        assert_that(table[str(self.objects[0].id)]).is_equal_to(dict(self.objects[0]))
        assert_that(table[str(self.objects[1].id)]).is_equal_to(dict(self.objects[1]))
        assert_that(table[str(self.objects[2].id)]).is_equal_to(dict(self.objects[2]))

    @pytest.mark.dependency(depends=['TestMasterDbSupport::test_create'])
    def test_create_throws(self):
        assert_that(self.dbsupport.create_master_password).raises(MasterPasswordExistsError).when_called_with(
            self.objects[0])

    @pytest.mark.dependency(depends=['TestMasterDbSupport::test_create'])
    def test_read(self):
        pw1 = self.dbsupport.read_master_password(self.objects[0].id)
        assert_that(pw1).is_equal_to(self.objects[0].pw)

    @pytest.mark.dependency(depends=['TestMasterDbSupport::test_create'])
    def test_read_throws(self):
        assert_that(self.dbsupport.read_master_password).raises(UserNotExistsError).when_called_with(5)
        assert_that(self.dbsupport.read_master_password).raises(TypeError).when_called_with('5')

    @pytest.mark.dependency()
    @pytest.mark.dependency(depends=['TestMasterDbSupport::test_create'])
    def test_update(self):
        pk1 = self.dbsupport.update_master_password(self.objects[0].id, MasterEntity(pw='EverChanging'))
        pk2 = self.dbsupport.update_master_password(
            self.objects[1].id, MasterEntity(pw='Another-Password', salt='new-salt'))
        assert_that(pk1).is_equal_to(self.objects[0].id)
        assert_that(pk2).is_equal_to(self.objects[1].id)

    @pytest.mark.dependency(depends=['TestMasterDbSupport::test_create'])
    def test_update_throws(self):
        assert_that(self.dbsupport.update_master_password).raises(UserNotExistsError).when_called_with(
            5, MasterEntity(pw='dummy'))
        assert_that(self.dbsupport.update_master_password).raises(TypeError).when_called_with(
            '5', MasterEntity(pw='dummy'))
        assert_that(self.dbsupport.update_master_password).raises(InvalidUpdateError).when_called_with(
            2, MasterEntity(user='invalid', pw='dummy'))
        assert_that(self.dbsupport.update_master_password).raises(InvalidUpdateError).when_called_with(
            1, MasterEntity(token='invalid', pw='dummy'))

    @pytest.mark.dependency(depends=['TestMasterDbSupport::test_update'])
    def test_records_after_update(self):
        table = persistent_storage['test-table']
        changed1 = dict(self.objects[0])
        changed1['pw'] = 'EverChanging'
        changed2 = dict(self.objects[1])
        changed2['pw'] = 'Another-Password'
        changed2['salt'] = 'new-salt'
        assert_that(table[str(self.objects[0].id)]).is_equal_to(changed1)
        assert_that(table[str(self.objects[1].id)]).is_equal_to(changed2)

    @classmethod
    def setup_class(cls):
        repo = MasterTinyRepository(table='test-table', storage=AtomicMemoryStorage)
        cls.repo = repo
        cls.dbsupport = MasterDbSupport(repo=repo)
        cls.objects = [
            MasterEntity(1, user='mypass-user', token='secret-token', pw='password', salt='salty'),
            MasterEntity(2, user='db-user', token='secret-token', pw='secret', salt='sugar'),
            MasterEntity(3, user='whoami', token='cant-see', pw='move-along', salt='pepper')
        ]

    @classmethod
    def teardown_class(cls):
        persistent_storage.clear()


class TestVaultDbSupport:
    @pytest.mark.dependency()
    def test_create(self):
        pk1 = self.dbsupport.create_vault_entry(self.objects[0].pop(UID_FIELD, None), entity=self.objects[0])
        assert_that(pk1).is_type_of(self.dbsupport.repo.id_cls)
        pk2 = self.dbsupport.create_vault_entry(self.objects[1].pop(UID_FIELD, None), entity=self.objects[1])
        assert_that(pk2).is_not_equal_to(pk1)
        self.dbsupport.create_vault_entry(self.objects[2].pop(UID_FIELD, None), entity=self.objects[2])
        for obj in self.objects[3:]:
            self.dbsupport.create_vault_entry(obj.pop(UID_FIELD, None), entity=obj)

    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_create'])
    def test_records(self):
        assert_that(persistent_storage).contains_key('test-table')
        table = persistent_storage['test-table']
        assert_that(table).contains_key(str(self.objects[0].id), str(self.objects[1].id), str(self.objects[2].id))
        assert_that(table[str(self.objects[0].id)]).is_equal_to(dict(self.objects[0]))
        assert_that(table[str(self.objects[1].id)]).is_equal_to(dict(self.objects[1]))
        assert_that(table[str(self.objects[2].id)]).is_equal_to(dict(self.objects[2]))
        assert_that(table).is_length(len(self.objects))

    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_create'])
    def test_create_throws(self):
        assert_that(self.dbsupport.create_vault_entry).raises(EmptyRecordInsertionError).when_called_with(
            entity=VaultEntity())
        assert_that(self.dbsupport.create_vault_entry).raises(EmptyRecordInsertionError).when_called_with(
            4, entity=VaultEntity(4))

    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_create'])
    def test_read(self):
        for obj in self.objects:
            e = self.dbsupport.read_vault_entry(pk=obj.id)
            assert_that(e).is_equal_to(obj)
        for obj in self.objects:
            e = self.dbsupport.read_vault_entry(crit=obj)
            assert_that(e).is_equal_to(obj)

    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_create'])
    def test_read_throws(self):
        assert_that(self.dbsupport.read_vault_entry).raises(RecordNotFoundError).when_called_with(
            11, pk=self.objects[3].id)
        assert_that(self.dbsupport.read_vault_entry).raises(RecordNotFoundError).when_called_with(pk=15)
        assert_that(self.dbsupport.read_vault_entry).raises(EmptyQueryError).when_called_with()

    @pytest.mark.dependency()
    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_create'])
    def test_update(self):
        pk1 = self.dbsupport.update_vault_entry(pk=self.objects[0].id, update=VaultEntity(pw='EverChanging'))
        pk2 = self.dbsupport.update_vault_entry(
            pk=self.objects[1].id, update=VaultEntity(pw='Another-Password', salt='new-salt', site=DEL))
        assert_that(pk1).is_equal_to(self.objects[0].id)
        assert_that(pk2).is_equal_to(self.objects[1].id)

    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_create'])
    def test_update_throws(self):
        assert_that(self.dbsupport.update_vault_entry).raises(TypeError).when_called_with(
            update={UID_FIELD: 3}, pk=14)
        assert_that(self.dbsupport.update_vault_entry).raises(RecordNotFoundError).when_called_with(
            pk=15, update=VaultEntity(six=6))

    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_update'])
    def test_records_after_update(self):
        table = persistent_storage['test-table']
        changed1 = dict(self.objects[0])
        changed1['pw'] = 'EverChanging'
        changed2 = dict(self.objects[1])
        changed2['pw'] = 'Another-Password'
        changed2['salt'] = 'new-salt'
        del changed2['site']
        assert_that(table[str(self.objects[0].id)]).is_equal_to(changed1)
        assert_that(table[str(self.objects[1].id)]).is_equal_to(changed2)

    @pytest.mark.dependency()
    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_create'])
    def test_delete(self):
        pass

    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_create'])
    def test_delete_throws(self):
        pass

    @pytest.mark.dependency(depends=['TestVaultDbSupport::test_delete'])
    def test_records_after_delete(self):
        pass

    @classmethod
    def setup_class(cls):
        repo = VaultTinyRepository(table='test-table', storage=AtomicMemoryStorage)
        cls.repo = repo
        cls.dbsupport = VaultDbSupport(repo=repo)
        objects = [
            VaultEntity(1, user='mypass-user', pw='password', _salt='salty'),
            VaultEntity(2, site='https://codehaven.com'),
            VaultEntity(3, user='whoami', pw='move-along', salt='pepper', site='https://youtube.com'),
            VaultEntity(4, user='goBoy', pw='shhhh...', salt_='****'),
            VaultEntity(5, api_key='5sd56afd458caa5', **{UID_FIELD: 14}),
            VaultEntity(6, **{'value-with': 'hyphen', 'cheese': 'cake'}),
            VaultEntity(7, somethingElseEntirely='dont do this')
        ]
        objects[2]._UID = 3
        objects[4]._UID = 14
        objects[5]._UID = 7
        objects[6]._UID = 14
        cls.objects = objects

    @classmethod
    def teardown_class(cls):
        persistent_storage.clear()

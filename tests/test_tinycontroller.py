from typing import Mapping

# noinspection PyPackageRequirements
import assertpy
# noinspection PyPackageRequirements
import pytest
# noinspection PyPackageRequirements
from assertpy import assert_that

from mypass.db.tiny import MasterController, MasterDao, VaultController, VaultDao
from mypass.exceptions import MasterPasswordExistsError, UserNotExistsError, MultipleMasterPasswordsError
from mypass.utils.tinydb import UID_FIELD, PROTECTED_FIELDS
from tests._utils import AtomicMemoryStorage, persistent_storage


@pytest.fixture(scope='function')
def patch_document_as_dict(monkeypatch):
    from mypass.utils import tinydb

    # noinspection PyUnusedLocal
    def new_document_as_dict(document, keep_id=True, remove_special=False):
        return tinydb.document_as_dict(document, keep_id=True, remove_special=False)

    # noinspection PyUnusedLocal
    def new_documents_as_dict(documents, keep_id=True, remove_special=False):
        return tinydb.documents_as_dict(documents, keep_id=True, remove_special=False)

    monkeypatch.setattr('mypass.db.tiny.controller.vault.document_as_dict', new_document_as_dict)
    monkeypatch.setattr('mypass.db.tiny.controller.vault.documents_as_dict', new_documents_as_dict)


class _CorruptedStorage:
    def __enter__(self):
        persistent_storage[MasterController.table]['4'] = {'user': 'my-user', 'pw': 'corrupt-pw', 'corruption': 42}

    def __exit__(self, exc_type, exc_val, exc_tb):
        del persistent_storage[MasterController.table]['4']


class TestTinyMasterController:
    def test_magic_init(self):
        MasterController(dao=MasterDao(storage=AtomicMemoryStorage))
        MasterController(storage=AtomicMemoryStorage)
        assert_that(MasterController).raises(AssertionError).when_called_with(
            dao=MasterDao(storage=AtomicMemoryStorage),
            storage=AtomicMemoryStorage)

    @pytest.mark.dependency()
    def test_create_master_password(self):
        entry_id1 = self.controller.create_master_password('my-user', 'my-token', 'my-PW', 'salted')
        assert_that(entry_id1).is_type_of(int)
        assert_that(entry_id1).is_equal_to(1)
        assert_that(self.controller.create_master_password).raises(MasterPasswordExistsError).when_called_with(
            'my-user', 'my-token', 'my-PW', 'salted')
        entry_id2 = self.controller.create_master_password(
            user='someone else', token='my-token', pw='PW', salt='salted')
        entry_id3 = self.controller.create_master_password(
            user='someone else again', token='another-token', pw='PW22', salt='salty')
        assert_that(entry_id2).is_type_of(int)
        assert_that(entry_id1).is_not_equal_to(entry_id2)
        assert_that(entry_id2).is_equal_to(2)
        assert_that(entry_id3).is_type_of(int)
        assert_that(entry_id2).is_not_equal_to(entry_id3)
        assert_that(entry_id3).is_equal_to(3)

    @pytest.mark.dependency(depends=['TestTinyMasterController::test_create_master_password'])
    def test_read_master_password(self):
        record1 = self.controller.read_master_password(1)
        assert_that(record1).is_type_of(dict)
        assert_that(record1).contains_key('user', 'token', 'pw', 'salt')
        record2 = self.controller.read_master_password(2)
        assert_that(record2).is_equal_to(dict(user='someone else', token='my-token', pw='PW', salt='salted'))
        record3 = self.controller.read_master_password('someone else again')
        assert_that(record3).is_equal_to(
            dict(user='someone else again', token='another-token', pw='PW22', salt='salty'))

    @pytest.mark.dependency(depends=['TestTinyMasterController::test_create_master_password'])
    def test_read_master_password_fails(self):
        assert_that(self.controller.read_master_password).raises(AssertionError).when_called_with(-1)
        assert_that(self.controller.read_master_password).raises(UserNotExistsError).when_called_with(158)
        assert_that(self.controller.read_master_password).raises(UserNotExistsError).when_called_with('non-existing')
        # corrupt db
        with _CorruptedStorage():
            assert_that(self.controller.read_master_password).raises(
                MultipleMasterPasswordsError).when_called_with('my-user')

    @pytest.mark.dependency(depends=['TestTinyMasterController::test_create_master_password'])
    def test_update_master_password(self):
        entry_id1 = self.controller.update_master_password(
            'my-user', 'my-changed-token', 'my-changed-PW', 'salt-changed')
        assert_that(entry_id1).is_equal_to(1)
        entry_id2 = self.controller.update_master_password(
            user_or_uid=2, token='change-2', pw='pw-PW2', salt='sugar')
        assert_that(entry_id2).is_equal_to(2)

    @pytest.mark.dependency(depends=['TestTinyMasterController::test_create_master_password'])
    def test_update_master_password_fails(self):
        assert_that(self.controller.update_master_password).raises(UserNotExistsError).when_called_with(
            'non-existent', 'my-changed-token', 'my-changed-PW', 'salt-changed')
        assert_that(self.controller.update_master_password).raises(UserNotExistsError).when_called_with(
            198, 'my-changed-token', 'my-changed-PW', 'salt-changed')
        with _CorruptedStorage():
            assert_that(self.controller.update_master_password).raises(MultipleMasterPasswordsError).when_called_with(
                'my-user', 'my-changed-token', 'my-changed-PW', 'salt-changed')

    @classmethod
    def setup_class(cls):
        dao = MasterDao(storage=AtomicMemoryStorage)
        cls.controller = MasterController(dao=dao)

    @classmethod
    def teardown_class(cls):
        persistent_storage.clear()


class TestTinyVaultController:
    def test_magic_init(self):
        VaultController(dao=VaultDao(storage=AtomicMemoryStorage))
        VaultController(storage=AtomicMemoryStorage)
        assert_that(MasterController).raises(AssertionError).when_called_with(
            dao=VaultDao(storage=AtomicMemoryStorage),
            storage=AtomicMemoryStorage)

    @pytest.mark.dependency()
    def test_create_vault_entry(self):
        entry_id1 = self.controller.create_vault_entry(item='first item', anyonim=True)
        assert_that(entry_id1).is_equal_to(1)
        entry_id2 = self.controller.create_vault_entry(
            1, item='second item', pw='strong-pw', key='someProtectedKey', key2='other-protected',
            _protected_fields=['pw', 'key'])
        assert_that(entry_id2).is_equal_to(2)
        entry_id3 = self.controller.create_vault_entry(1, some='some', _any='any')
        entry_id4 = self.controller.create_vault_entry(2)
        assert_that(entry_id3).is_not_equal_to(entry_id4)

    @pytest.mark.dependency(depends=['TestTinyVaultController::test_create_vault_entry'])
    def test_read_vault_entry(self, patch_document_as_dict):
        doc1 = self.controller.read_vault_entry(doc_id=1)
        assert_that(doc1).is_instance_of(Mapping)
        if UID_FIELD in doc1 and doc1[UID_FIELD] is not None:
            assertpy.fail(f'Expected doc to NOT contain a valid {UID_FIELD}.')
        doc2 = self.controller.read_vault_entry(doc_id=2)
        assert_that(doc2).is_instance_of(Mapping)
        assert_that(doc2).contains_key(UID_FIELD)
        assert_that(doc2[UID_FIELD]).is_equal_to(1)

    @pytest.mark.dependency(depends=['TestTinyVaultController::test_create_vault_entry'])
    def test_read_vault_entries(self, patch_document_as_dict):
        docs1 = self.controller.read_vault_entries(1)
        assert_that(all(UID_FIELD in doc for doc in docs1)).is_true()

    @pytest.mark.dependency(depends=['TestTinyVaultController::test_create_vault_entry'])
    def test_update_vault_entry(self):
        doc1 = self.controller.read_vault_entry(doc_id=2)
        assert_that(doc1).contains_key('item', 'pw')
        entry_id1 = self.controller.update_vault_entry(doc_id=2, remove_keys=['item', 'pw', 'key2'])
        assert_that(entry_id1).is_equal_to(2)
        new_doc1 = self.controller.read_vault_entry(doc_id=2)
        assert_that(new_doc1).does_not_contain_key('item', 'pw', 'key2')
        assert_that(new_doc1).contains_key('key')
        if PROTECTED_FIELDS in new_doc1 and new_doc1[PROTECTED_FIELDS] is not None:
            assert_that(new_doc1).contains_key(*new_doc1[PROTECTED_FIELDS])
        self.controller.update_vault_entry(doc_id=2, remove_keys=['pw', 'key'])
        new_doc2 = self.controller.read_vault_entry(doc_id=2)
        assert_that(new_doc2).does_not_contain_key(PROTECTED_FIELDS)

    @pytest.mark.dependency(depends=['TestTinyVaultController::test_create_vault_entry'])
    def test_update_vault_entries(self):
        pass

    @pytest.mark.dependency(depends=['TestTinyVaultController::test_create_vault_entry'])
    def test_delete_vault_entry(self):
        entry_id1 = self.controller.create_vault_entry(delthis='first item', anyonim=True)
        entry_id2 = self.controller.create_vault_entry(
            1, item='delete this', pw='strong-pw', key='someProtectedKey', _protected_fields=['pw', 'key'])

    @pytest.mark.dependency(depends=['TestTinyVaultController::test_create_vault_entry'])
    def test_delete_vault_entries(self):
        entry_id1 = self.controller.create_vault_entry(delthis='first item', anyonim=True)
        entry_id2 = self.controller.create_vault_entry(
            1, item='delete this', pw='strong-pw', key='someProtectedKey', _protected_fields=['pw', 'key'])

    @classmethod
    def setup_class(cls):
        dao = VaultDao(storage=AtomicMemoryStorage)
        cls.controller = VaultController(dao=dao)

    @classmethod
    def teardown_class(cls):
        persistent_storage.clear()

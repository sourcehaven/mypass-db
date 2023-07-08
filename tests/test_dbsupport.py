import abc

# noinspection PyPackageRequirements
import pytest
# noinspection PyPackageRequirements
from assertpy import assert_that

from _utils import AtomicMemoryStorage, persistent_storage, seed_uuid
from mypass.db import MasterDbSupport, VaultDbSupport
from mypass.db.tiny import MasterTinyRepository, VaultTinyRepository
from mypass.exceptions import MasterPasswordExistsError, UserNotExistsError, InvalidUpdateError, \
    EmptyRecordInsertionError, RecordNotFoundError, EmptyQueryError
from mypass.types import MasterEntity, VaultEntity
from mypass.types.const import UID_FIELD
from mypass.types.op import DEL
from mypass.utils import gen_uuid


class MasterDbSupportTester(abc.ABC):
    dbsupport: MasterDbSupport
    objects: list[MasterEntity]

    @pytest.mark.dependency(name='self::test_create')
    def test_create(self):
        pk1 = self.dbsupport.create_master_password(self.objects[0])
        assert_that(pk1).is_type_of(self.dbsupport.repo.id_cls)
        pk2 = self.dbsupport.create_master_password(self.objects[1])
        assert_that(pk2).is_not_equal_to(pk1)
        self.dbsupport.create_master_password(self.objects[2])

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_records(self):
        assert_that(persistent_storage).contains_key('test-table')
        table = persistent_storage['test-table']
        assert_that(table).contains_key(str(self.objects[0].id), str(self.objects[1].id), str(self.objects[2].id))
        assert_that(table[str(self.objects[0].id)]).is_equal_to(dict(self.objects[0]))
        assert_that(table[str(self.objects[1].id)]).is_equal_to(dict(self.objects[1]))
        assert_that(table[str(self.objects[2].id)]).is_equal_to(dict(self.objects[2]))

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_create_throws(self):
        assert_that(self.dbsupport.create_master_password).raises(MasterPasswordExistsError).when_called_with(
            self.objects[0])

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_read(self):
        pw1 = self.dbsupport.read_master_password(self.objects[0].id)
        assert_that(pw1).is_equal_to(self.objects[0].pw)

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_read_throws(self):
        assert_that(self.dbsupport.read_master_password).raises(UserNotExistsError).when_called_with(5)
        assert_that(self.dbsupport.read_master_password).raises(TypeError).when_called_with('5')

    @pytest.mark.dependency(name='self::test_update', depends=['self::test_create'])
    def test_update(self):
        pk1 = self.dbsupport.update_master_password(self.objects[0].id, MasterEntity(pw='EverChanging'))
        pk2 = self.dbsupport.update_master_password(
            self.objects[1].id, MasterEntity(pw='Another-Password', salt='new-salt'))
        assert_that(pk1).is_equal_to(self.objects[0].id)
        assert_that(pk2).is_equal_to(self.objects[1].id)

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_update_throws(self):
        assert_that(self.dbsupport.update_master_password).raises(UserNotExistsError).when_called_with(
            gen_uuid(self.objects[0].id.__class__.__name__), MasterEntity(pw='dummy'))
        assert_that(self.dbsupport.update_master_password).raises(TypeError).when_called_with(
            object(), MasterEntity(pw='dummy'))
        assert_that(self.dbsupport.update_master_password).raises(InvalidUpdateError).when_called_with(
            self.objects[1].id, MasterEntity(user='invalid', pw='dummy'))

    @pytest.mark.dependency(depends=['self::test_update'])
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
    @abc.abstractmethod
    def setup_class(cls):
        ...

    @classmethod
    def teardown_class(cls):
        persistent_storage.clear()


class VaultDbSupportTester(abc.ABC):
    dbsupport: VaultDbSupport
    objects: list[VaultEntity]

    @pytest.mark.dependency(name='self::test_create')
    def test_create(self):
        pk1 = self.dbsupport.create_vault_entry(self.objects[0].pop(UID_FIELD, None), entity=self.objects[0])
        assert_that(pk1).is_type_of(self.dbsupport.repo.id_cls)
        pk2 = self.dbsupport.create_vault_entry(self.objects[1].pop(UID_FIELD, None), entity=self.objects[1])
        assert_that(pk2).is_not_equal_to(pk1)
        self.dbsupport.create_vault_entry(self.objects[2].pop(UID_FIELD, None), entity=self.objects[2])
        for obj in self.objects[3:]:
            self.dbsupport.create_vault_entry(obj.pop(UID_FIELD, None), entity=obj)

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_records(self):
        assert_that(persistent_storage).contains_key('test-table')
        table = persistent_storage['test-table']
        assert_that(table).contains_key(str(self.objects[0].id), str(self.objects[1].id), str(self.objects[2].id))
        assert_that(table[str(self.objects[0].id)]).is_equal_to(dict(self.objects[0]))
        assert_that(table[str(self.objects[1].id)]).is_equal_to(dict(self.objects[1]))
        assert_that(table[str(self.objects[2].id)]).is_equal_to(dict(self.objects[2]))
        assert_that(table).is_length(len(self.objects))

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_create_throws(self):
        assert_that(self.dbsupport.create_vault_entry).raises(EmptyRecordInsertionError).when_called_with(
            entity=VaultEntity())
        entity_id = gen_uuid(self.objects[0].id.__class__.__name__)
        assert_that(self.dbsupport.create_vault_entry).raises(EmptyRecordInsertionError).when_called_with(
            entity_id, entity=VaultEntity(entity_id))

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_read(self):
        for obj in self.objects:
            e = self.dbsupport.read_vault_entry(pk=obj.id)
            assert_that(e).is_equal_to(obj)
        for obj in self.objects:
            e = self.dbsupport.read_vault_entry(crit=obj)
            assert_that(e).is_equal_to(obj)

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_read_throws(self):
        assert_that(self.dbsupport.read_vault_entry).raises(RecordNotFoundError).when_called_with(
            gen_uuid(self.objects[3].id.__class__.__name__), pk=self.objects[3].id)
        assert_that(self.dbsupport.read_vault_entry).raises(RecordNotFoundError).when_called_with(
            pk=gen_uuid(self.objects[3].id.__class__.__name__))
        assert_that(self.dbsupport.read_vault_entry).raises(EmptyQueryError).when_called_with()

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_reads(self):
        es = list(self.dbsupport.read_vault_entries())
        assert_that(es).is_length(len(self.objects))
        assert_that(es).is_equal_to(self.objects)
        allowed_pks = [self.objects[7].id, self.objects[8].id, self.objects[9].id]
        es = list(self.dbsupport.read_vault_entries(
            crit=VaultEntity(user='mypass-user'), pks=allowed_pks))
        for e in es:
            assert_that(e.user).is_equal_to('mypass-user')
            assert_that(allowed_pks).contains(e.id)
        allowed_pks = [self.objects[1].id, self.objects[7].id, self.objects[8].id, self.objects[9].id]
        es = list(self.dbsupport.read_vault_entries(pks=allowed_pks))
        for e in es:
            assert_that(allowed_pks).contains(e.id)
        es = list(self.dbsupport.read_vault_entries(crit=VaultEntity(user='mypass-user')))
        for e in es:
            assert_that(e.user).is_equal_to('mypass-user')
        es = list(self.dbsupport.read_vault_entries(crit=VaultEntity(pw='password')))
        for e in es:
            assert_that(e.pw).is_equal_to('password')
        es = list(self.dbsupport.read_vault_entries(self.objects[4][UID_FIELD]))
        for e in es:
            assert_that(e[UID_FIELD]).is_equal_to(self.objects[4][UID_FIELD])

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_reads_throws(self):
        assert_that(self.dbsupport.read_vault_entry).raises(RecordNotFoundError).when_called_with(
            gen_uuid(self.objects[3].id.__class__.__name__), pk=self.objects[3].id)
        assert_that(self.dbsupport.read_vault_entry).raises(RecordNotFoundError).when_called_with(
            pk=gen_uuid(self.objects[3].id.__class__.__name__))
        assert_that(self.dbsupport.read_vault_entry).raises(EmptyQueryError).when_called_with()

    @pytest.mark.dependency(name='self::test_update', depends=['self::test_create'])
    def test_update(self):
        pk1 = self.dbsupport.update_vault_entry(pk=self.objects[0].id, update=VaultEntity(pw='EverChanging'))
        pk2 = self.dbsupport.update_vault_entry(
            pk=self.objects[1].id, update=VaultEntity(pw='Another-Password', salt='new-salt', site=DEL))
        assert_that(pk1).is_equal_to(self.objects[0].id)
        assert_that(pk2).is_equal_to(self.objects[1].id)

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_update_throws(self):
        assert_that(self.dbsupport.update_vault_entry).raises(TypeError).when_called_with(
            update={UID_FIELD: self.objects[4][UID_FIELD]}, pk=self.objects[4].id)
        assert_that(self.dbsupport.update_vault_entry).raises(RecordNotFoundError).when_called_with(
            pk=gen_uuid(self.objects[0].id.__class__.__name__), update=VaultEntity(six=6))

    @pytest.mark.dependency(depends=['self::test_update'])
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

    @pytest.mark.dependency(name='self::test_updates', depends=['self::test_create'])
    def test_updates(self):
        update_pks = [self.objects[2].id, self.objects[4].id]
        pks = self.dbsupport.update_vault_entries(
            pks=update_pks, update=VaultEntity(pw='EverChanging'))
        for pk in pks:
            assert_that(update_pks).contains(pk)
        self.dbsupport.update_vault_entries(
            crit=VaultEntity(user='mypass-user'), update=VaultEntity(pw='Another-Password', salt='new-salt', site=DEL))
        self.dbsupport.update_vault_entries(update=VaultEntity(extra_field='EXTRA'))
        self.dbsupport.update_vault_entries(self.objects[4][UID_FIELD], update=VaultEntity(extra_field='EXTRA_UID'))

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_updates_throws(self):
        assert_that(self.dbsupport.update_vault_entries).raises(TypeError).when_called_with(
            update={UID_FIELD: self.objects[4][UID_FIELD]})

    @pytest.mark.dependency(depends=['self::test_updates'])
    def test_records_after_updates(self):
        table = persistent_storage['test-table']
        changed1 = dict(self.objects[2])
        changed1['pw'] = 'EverChanging'
        changed2 = dict(self.objects[4])
        changed2['pw'] = 'EverChanging'
        assert_that(table[str(self.objects[2].id)]['pw']).is_equal_to('EverChanging')
        assert_that(table[str(self.objects[4].id)]['pw']).is_equal_to('EverChanging')
        for k, v in table.items():
            assert_that(v).contains_key('extra_field')
            if UID_FIELD in v and v[UID_FIELD] == self.objects[4][UID_FIELD]:
                assert_that(v['extra_field']).is_equal_to('EXTRA_UID')
            else:
                assert_that(v['extra_field']).is_equal_to('EXTRA')

    @pytest.mark.dependency(name='self::test_delete', depends=['self::test_create'])
    def test_delete(self):
        deleted_id = self.dbsupport.delete_vault_entry(pk=self.objects[4].id)
        assert_that(deleted_id).is_equal_to(self.objects[4].id)
        deleted_id = self.dbsupport.delete_vault_entry(pk=self.objects[7].id)
        assert_that(deleted_id).is_equal_to(self.objects[7].id)

    @pytest.mark.dependency(depends=['self::test_create'])
    def test_delete_throws(self):
        assert_that(self.dbsupport.delete_vault_entry).raises(RecordNotFoundError).when_called_with(
            pk=gen_uuid(self.objects[0].id.__class__.__name__))
        assert_that(self.dbsupport.delete_vault_entry).raises(RecordNotFoundError).when_called_with(
            pk=gen_uuid(self.objects[0].id.__class__.__name__))

    @pytest.mark.dependency(depends=['self::test_delete'])
    def test_records_after_delete(self):
        table = persistent_storage['test-table']
        assert_that(table).is_length(len(self.objects) - 2)
        assert_that(table).does_not_contain_key(*[self.objects[4].id, self.objects[7].id])

    @pytest.mark.dependency(name='self::test_deletes', depends=['self::test_create'])
    def test_deletes(self):
        delete_pks = [self.objects[8].id, self.objects[9].id]
        deleted_ids = self.dbsupport.delete_vault_entries(pks=delete_pks)
        assert_that(delete_pks).is_equal_to(deleted_ids)

    @pytest.mark.dependency(depends=['self::test_deletes'])
    def test_records_after_deletes(self):
        table = persistent_storage['test-table']
        assert_that(table).is_length(len(self.objects) - 4)
        assert_that(table).does_not_contain_key(*[
            self.objects[4].id, self.objects[7].id, self.objects[8].id, self.objects[9].id])

    @classmethod
    @abc.abstractmethod
    def setup_class(cls): ...

    @classmethod
    def teardown_class(cls):
        persistent_storage.clear()


class TestTinyMasterDbSupport(MasterDbSupportTester):
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


class TestTinyVaultDbSupport(VaultDbSupportTester):
    @classmethod
    def setup_class(cls):
        seed_uuid(42)
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
            VaultEntity(7, somethingElseEntirely='dont do this'),
            VaultEntity(8, user='mypass-user', pw='another-pass', _salt='wasd'),
            VaultEntity(9, user='mypass-user', token='my-secret-token'),
            VaultEntity(10, user='mypass-user', recipie='Potatoes')
        ]
        objects[2][UID_FIELD] = 3
        objects[4][UID_FIELD] = 14
        objects[5][UID_FIELD] = 7
        objects[6][UID_FIELD] = 14
        cls.objects = objects

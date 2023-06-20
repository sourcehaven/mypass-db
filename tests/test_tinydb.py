import json
import shutil
from pathlib import Path

# noinspection PyPackageRequirements
from assertpy import assert_that
from tinydb import TinyDB

from mypass.db.tiny import tinydb
# noinspection PyProtectedMember
from mypass.db.tiny._db import unlink
from mypass.db.tiny.master import crud as master_crud
from mypass.db.tiny.vault import crud as vault_crud


DB_PATH = str(Path.home().joinpath('.mypass/tests/db/tiny/db.json'))


class TestTinyDb:
    def test_db_creation(self):
        db = tinydb(DB_PATH)
        assert_that(db).is_type_of(TinyDB)
        assert_that(DB_PATH).exists()

    def test_db_unlink(self):
        unlink(DB_PATH)
        assert_that(DB_PATH).does_not_exist()

    @classmethod
    def teardown_class(cls):
        if Path(DB_PATH).exists():
            shutil.rmtree(DB_PATH)


class TestTinyDbMasterCrud:
    def test_create(self):
        entry_id1 = master_crud.create('mypass-user1', 'secret-token-1', 'secret-pw-1', 'salt')
        assert_that(entry_id1).is_type_of(int)
        entry_id2 = master_crud.create('mypass-user2', 'secret-token-2', 'secret-pw-2', 'salt')
        assert_that(entry_id2).is_type_of(int)
        with open(DB_PATH, 'r') as fp:
            db_content: dict = json.load(fp)
        assert_that(db_content).is_type_of(dict)
        assert_that(db_content).contains_key('test-master')
        master_table = db_content['test-master']
        assert_that(master_table).contains_key(str(entry_id1))
        assert_that(master_table).contains_key(str(entry_id2))

    @classmethod
    def setup_class(cls):
        from mypass.db.tiny.master._table import _db_opts
        _db_opts['name'] = 'test-master'
        _db_opts['db_kwargs']['path'] = DB_PATH

    @classmethod
    def teardown_class(cls):
        if Path(DB_PATH).exists():
            shutil.rmtree(Path(DB_PATH).parent)


class TestTinyDbVaultCrud:
    def test_create(self):
        vault_crud.create()

    @classmethod
    def setup_class(cls):
        from mypass.db.tiny.vault._table import _db_opts
        _db_opts['name'] = 'test-vault'
        _db_opts['db_kwargs']['path'] = DB_PATH

    @classmethod
    def teardown_class(cls):
        if Path(DB_PATH).exists():
            shutil.rmtree(DB_PATH)

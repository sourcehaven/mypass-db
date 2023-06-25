from typing import Mapping, Iterable

from mypass.db.tiny import TinyDao, TinyRepository
from mypass.exceptions import EmptyRecordInsertionError
from mypass.types import PasswordVaultEntity
from mypass.utils.tinydb import UID_FIELD, ID_FIELD, PROTECTED_FIELDS
from mypass.utils.tinydb import create_query_with_uid, documents_as_dict, filter_doc_ids, document_as_dict, check_uid

_T = PasswordVaultEntity


class VaultTinyRepository(TinyRepository[int, _T]):
    def __init__(self, dao: TinyDao = None, *args, **kwargs):
        super().__init__(dao, *args, **kwargs)

    def create_vault_entry(
            self,
            __uid: int = None,
            *,
            pw: str = None,
            salt: str = None,
            user: str = None,
            label: str = None,
            email: str = None,
            site: str = None,
            **kwargs
    ):
        """`__uid` will be stored under a special `_UID` field"""

        check_uid(__uid)

        d = kwargs
        d[UID_FIELD] = __uid
        if label is not None:
            d['label'] = label
        if pw is not None:
            d['pw'] = pw
        if salt is not None:
            d['salt'] = salt
        if user is not None:
            d['user'] = user
        if email is not None:
            d['email'] = email
        if site is not None:
            d['site'] = site
        if any(d):
            # _UID will be inserted, even if its None
            # only ones with direct access to this function (or this api) should be able to
            return self.dao.create(**d)
        raise EmptyRecordInsertionError('Cannot insert empty record into vault table.')

    def read_vault_entries(self, __uid: int | str = None, *, cond: dict = None, doc_ids: Iterable[int] = None):
        check_uid(__uid)
        cond = create_query_with_uid(__uid, cond)
        items = self.dao.read(cond=cond)
        return documents_as_dict(filter_doc_ids(items, doc_ids), keep_id=True)

    def read_vault_entry(self, __uid: int = None, *, cond: dict = None, doc_id: int = None):
        check_uid(__uid)
        assert doc_id is not None or cond is not None, \
            'Querying a specific password without either `doc_id` or `cond` is meaningless.'
        cond = create_query_with_uid(__uid, cond)
        if doc_id is not None:
            item = self.dao.read_one(doc_id=doc_id)
            if item is None:
                return None
            if cond is None:
                return document_as_dict(item, keep_id=True)
            if cond(item):
                return document_as_dict(item, keep_id=True)
            return None
        else:
            item = self.dao.read_one(cond=cond)
            if item is None:
                return None
            return document_as_dict(item, keep_id=True)

    def update_vault_entries(
            self,
            __uid: int = None,
            *,
            fields: Mapping,
            cond: dict = None,
            doc_ids: Iterable[int] = None
    ):
        # TODO: implement remove keys -> dao has changed
        if remove_keys is None or len(list(remove_keys)) <= 0:
            check_uid(__uid)
            cond = create_query_with_uid(__uid, cond)
            if doc_ids is None:
                items = self.dao.update(fields, cond=cond)
            else:
                docs = self.read_vault_entries(__uid, cond=cond, doc_ids=doc_ids)
                items = self.dao.update(fields, doc_ids=[d[ID_FIELD] for d in docs])
            return items

        remove_keys: Iterable[int] | None
        entries = self.read_vault_entries(__uid, cond=cond, doc_ids=doc_ids)
        items: list[int] = list(filter(lambda x: x is not None, [
            self.update_vault_entry(__uid, fields, doc_id=entry['_id'], remove_keys=remove_keys)
            for entry in entries]))
        return items

    def update_vault_entry(
            self,
            __uid: int = None,
            *,
            fields: Mapping,
            cond: dict = None,
            doc_id: int
    ):
        # TODO: implement remove keys -> dao has changed
        check_uid(__uid)
        cond = create_query_with_uid(__uid, cond)
        if cond is not None:
            # check the conditions first, and only update matching items
            item = self.read_vault_entry(__uid, doc_id=doc_id, cond=cond)
            if item is not None:
                if remove_keys is not None and PROTECTED_FIELDS in item:
                    rm_keys = list(set(remove_keys).intersection(set(item.keys())))
                    remaining_protected_keys = list(set(item[PROTECTED_FIELDS]).difference(rm_keys))
                    if len(remaining_protected_keys) <= 0:
                        remove_keys = [PROTECTED_FIELDS, *remove_keys]
                    if fields is None:
                        fields = {}
                    fields[PROTECTED_FIELDS] = remaining_protected_keys

                items = self.dao.update(fields, doc_ids=[doc_id])
            else:
                items = []
        else:
            item = self.read_vault_entry(__uid, doc_id=doc_id)
            if remove_keys is not None and PROTECTED_FIELDS in item:
                rm_keys = list(set(remove_keys).intersection(set(item.keys())))
                remaining_protected_keys = list(set(item[PROTECTED_FIELDS]).difference(rm_keys))
                if len(remaining_protected_keys) <= 0:
                    remove_keys = [PROTECTED_FIELDS, *remove_keys]
                if fields is None:
                    fields = {}
                fields[PROTECTED_FIELDS] = remaining_protected_keys
            items = self.dao.update(fields, doc_ids=[doc_id])

        try:
            return items[0]
        except IndexError:
            return None

    def delete_vault_entries(self, __uid: int = None, *, cond: dict = None, doc_ids: Iterable[int] = None):
        check_uid(__uid)
        cond = create_query_with_uid(__uid, cond)
        if doc_ids is None:
            items = self.dao.delete(cond=cond)
        else:
            docs = self.read_vault_entries(__uid, cond=cond, doc_ids=doc_ids)
            items = self.dao.delete(doc_ids=[d[ID_FIELD] for d in docs])
        return items

    def delete_vault_entry(self, __uid: int = None, *, cond: dict = None, doc_id: int):
        check_uid(__uid)
        cond = create_query_with_uid(__uid, cond)
        if cond is not None:
            # check the conditions first, and only delete matching items
            item = self.read_vault_entry(__uid, doc_id=doc_id, cond=cond)
            if item is not None:
                items = self.dao.delete(doc_ids=[doc_id])
            else:
                items = []
        else:
            items = self.dao.delete(doc_ids=[doc_id])
        try:
            return items[0]
        except IndexError:
            return None

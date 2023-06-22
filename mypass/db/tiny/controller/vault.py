from typing import Mapping, Iterable

from mypass.db.tiny.dao import VaultDao
from mypass.exceptions import EmptyRecordInsertionError
from mypass.utils.tinydb import UID_FIELD, ID_FIELD
from mypass.utils.tinydb import create_query_with_uid, documents_as_dict, filter_doc_ids, document_as_dict, check_uid

_T_DAO = VaultDao


class VaultController:
    table = _T_DAO.table

    def __init__(self, dao: _T_DAO = None, *args, **kwargs):
        assert dao is None or (len(args) == 0 and len(kwargs) == 0), \
            'When dao is specified, there should not be any arguments and/or keyword arguments present.'
        if dao is None:
            dao = VaultDao(*args, **kwargs)
        self.dao = dao

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

    def read_vault_entry(self, __uid: int | str = None, *, cond: dict = None, doc_id: int = None):
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
        return document_as_dict(item, keep_id=True)

    def update_vault_entries(
            self,
            __uid: int | str = None,
            fields: Mapping = None,
            *,
            cond: dict = None,
            doc_ids: Iterable[int] = None,
            remove_keys: Iterable[int] = None
    ):
        check_uid(__uid)
        cond = create_query_with_uid(__uid, cond)
        if doc_ids is None:
            items = self.dao.update(fields, cond=cond, remove_keys=remove_keys)
        else:
            docs = self.read_vault_entries(__uid, cond=cond, doc_ids=doc_ids)
            items = self.dao.update(fields, doc_ids=[d[ID_FIELD] for d in docs], remove_keys=remove_keys)
        return items

    def update_vault_entry(
            self,
            __uid: int | str = None,
            fields: Mapping = None,
            *,
            cond: dict = None,
            doc_id: int,
            remove_keys: Iterable[str] = None
    ):
        check_uid(__uid)
        cond = create_query_with_uid(__uid, cond)
        if cond is not None:
            # check the conditions first, and only update matching items
            self.read_vault_entry()
            item = self.read_vault_entry(__uid, doc_id=doc_id, cond=cond)
            if item is not None:
                items = self.dao.update(fields, doc_ids=[doc_id], remove_keys=remove_keys)
            else:
                items = []
        else:
            items = self.dao.update(fields, doc_ids=[doc_id], remove_keys=remove_keys)
        try:
            return items[0]
        except IndexError:
            return None

    def delete_vault_entries(self, __uid: int | str = None, *, cond: dict = None, doc_ids: Iterable[int] = None):
        check_uid(__uid)
        cond = create_query_with_uid(__uid, cond)
        if doc_ids is None:
            items = self.dao.delete(cond=cond)
        else:
            docs = self.read_vault_entries(__uid, cond=cond, doc_ids=doc_ids)
            items = self.dao.delete(doc_ids=[d[ID_FIELD] for d in docs])
        return items

    def delete_vault_entry(self, __uid: int | str = None, *, cond: dict = None, doc_id: int):
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

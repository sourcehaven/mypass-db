from functools import wraps
from typing import Iterable

from tinydb import Query
from tinydb.table import Document

from mypass.db import create_query
from mypass.db.tiny.vault import create, read, read_one, update, delete
from mypass.db.tiny.master import read as get_master
from mypass.exceptions import EmptyRecordInsertionError, MultipleMasterPasswordsError, UserNotExistsError


ID_FIELD = '_id'
UID_FIELD = '_UID'


def _convert_name_to_id(__user: str):
    q = Query()
    items = get_master(q.user == __user)
    if len(items) > 1:
        raise MultipleMasterPasswordsError(
            f'Using a corrupted database with\n'
            f'    user: {__user}\n'
            f'    number of master passwords: {len(items)}.')
    try:
        return items[0].doc_id
    except IndexError:
        raise UserNotExistsError(f'Given user `{__user}` has no associated user_id in the database.')


def _check_uid(f):
    @wraps(f)
    def wrapper(__uid, *args, **kwargs):
        if __uid is None:
            return f(__uid, *args, **kwargs)
        if isinstance(__uid, str):
            __uid = _convert_name_to_id(__uid)
        assert (isinstance(__uid, int) and __uid >= 0), 'User id should be non-negative integer.'
        return f(__uid, *args, **kwargs)
    return wrapper


def is_protected_key(k: str):
    return k.startswith('_') and k.upper() == k


def filter_doc_ids(documents: list[Document], doc_ids: Iterable[int] = None):
    if doc_ids is not None:
        doc_ids = set(doc_ids)
        documents = [doc for doc in documents if doc.doc_id in doc_ids]
    return documents


def create_query_with_uid(__uid: int | str = None, cond: dict = None):
    if cond is not None:
        if __uid is not None:
            cond[UID_FIELD] = __uid
        cond = create_query(cond, logic='and')
    elif __uid is not None:
        cond = create_query({UID_FIELD: __uid}, logic='and')
    return cond


def document_as_dict(document: Document, keep_id: bool = False, remove_special: bool = True) -> dict:
    if remove_special:
        # remove every special field except `ID_FIELD` which will be inserted when finishing up
        for k in document.copy():
            if is_protected_key(k):
                del document[k]
    if keep_id:
        return {ID_FIELD: document.doc_id, **document}
    return dict(document)


def documents_as_dict(documents: Iterable[Document], keep_id: bool = False, remove_special: bool = True):
    return [document_as_dict(doc, keep_id=keep_id, remove_special=remove_special) for doc in documents]


@_check_uid
def create_vault_password(
        __uid: int | str = None,
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
        return create(**d)
    raise EmptyRecordInsertionError('Cannot insert empty record into vault table.')


@_check_uid
def read_vault_passwords(__uid: int | str = None, *, cond: dict = None, doc_ids: Iterable[int] = None):
    cond = create_query_with_uid(__uid, cond)
    items = read(cond=cond)
    return documents_as_dict(filter_doc_ids(items, doc_ids), keep_id=True)


@_check_uid
def read_vault_password(__uid: int | str = None, *, doc_id: int = None, cond: dict = None):
    assert doc_id is not None or cond is not None, \
        'Querying a specific password without either `doc_id` or `cond` is meaningless.'
    cond = create_query_with_uid(__uid, cond)
    if doc_id is not None:
        item = read_one(doc_id=doc_id)
        if item is None:
            return None
        if cond is None:
            return document_as_dict(item, keep_id=True)
        if cond(item):
            return document_as_dict(item, keep_id=True)
        return None
    else:
        item = read_one(cond=cond)
    return document_as_dict(item, keep_id=True)


@_check_uid
def update_vault_passwords(
        __uid: int | str = None,
        *,
        cond: dict = None,
        doc_ids: Iterable[int] = None,
        pw: str = None,
        salt: str = None,
        user: str = None,
        name: str = None,
        email: str = None,
        site: str = None,
        **kwargs
):
    cond = create_query_with_uid(__uid, cond)
    update_kwargs = dict(pw=pw, salt=salt, user=user, label=name, email=email, site=site, **kwargs)
    if doc_ids is None:
        items = update(cond, None, **update_kwargs)
    else:
        docs = read_vault_passwords(__uid, cond=cond, doc_ids=doc_ids)
        items = update(None, [d[ID_FIELD] for d in docs], **update_kwargs)
    return items


@_check_uid
def update_vault_password(
        __uid: int | str = None,
        *,
        doc_id: int,
        cond: dict = None,
        pw: str = None,
        salt: str = None,
        user: str = None,
        name: str = None,
        email: str = None,
        site: str = None,
        **kwargs
):
    cond = create_query_with_uid(__uid, cond)
    update_kwargs = dict(pw=pw, salt=salt, user=user, label=name, email=email, site=site, **kwargs)
    if cond is not None:
        # check the conditions first, and only update matching items
        item = read_vault_password(__uid, doc_id=doc_id, cond=cond)
        if item is not None:
            items = update(None, [doc_id], **update_kwargs)
        else:
            items = []
    else:
        items = update(None, [doc_id], **update_kwargs)
    try:
        return items[0]
    except IndexError:
        return None


@_check_uid
def delete_vault_passwords(__uid: int | str = None, *, cond: dict = None, doc_ids: Iterable[int] = None):
    cond = create_query_with_uid(__uid, cond)
    if doc_ids is None:
        items = delete(cond, None)
    else:
        docs = read_vault_passwords(__uid, cond=cond, doc_ids=doc_ids)
        items = delete(None, [d[ID_FIELD] for d in docs])
    return items


@_check_uid
def delete_vault_password(__uid: int | str = None, *, doc_id: int, cond: dict = None):
    cond = create_query_with_uid(__uid, cond)
    if cond is not None:
        # check the conditions first, and only delete matching items
        item = read_vault_password(__uid, doc_id=doc_id, cond=cond)
        if item is not None:
            items = delete(None, [doc_id])
        else:
            items = []
    else:
        items = delete(None, [doc_id])
    try:
        return items[0]
    except IndexError:
        return None


def _main():
    doc = Document({'a': 5, 'c': 'six', 'k': '854', 'sss': 78666, '_UID': 1}, 1)
    cond = create_query_with_uid(1, {'a': 5, 'z': 'six'})
    val = cond(doc)
    print(val)

    pw = read_vault_password('mypass', doc_id=1)
    print(pw)
    pw = read_vault_passwords(1)
    print(pw)


if __name__ == '__main__':
    _main()

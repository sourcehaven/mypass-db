from typing import Iterable

from tinydb import Query
from tinydb.table import Document

from mypass.db import create_query
from mypass.db.tiny.vault import create, read, read_one, update, delete
from mypass.db.tiny.master import read as get_master
from mypass.exceptions import EmptyRecordInsertionError, MultipleMasterPasswordsError, UserNotExistsError


def document_as_dict(document: Document, keep_id: bool = False, remove_special: bool = True) -> dict:
    if remove_special:
        for k in document.copy():
            if k.startswith('_'):
                del document[k]
    if keep_id:
        return dict(_id=document.doc_id, **document)
    return dict(document)


def documents_as_dict(documents: Iterable[Document], keep_id: bool = False, remove_special: bool = True):
    return [document_as_dict(doc, keep_id=keep_id, remove_special=remove_special) for doc in documents]


def create_vault_password(
        __user_id: int | str,
        *,
        pw: str = None,
        salt: str = None,
        user: str = None,
        label: str = None,
        email: str = None,
        site: str = None,
        **kwargs
):
    if isinstance(__user_id, str):
        q = Query()
        items = get_master(q.user == __user_id)
        if len(items) > 1:
            raise MultipleMasterPasswordsError(
                f'Using a corrupted database with\n'
                f'    user: {user}\n'
                f'    number of master passwords: {len(items)}.')
        try:
            __user_id = items[0].doc_id
        except IndexError:
            raise UserNotExistsError(f'Given user `{__user_id}` has no associated user_id in the database.')
    assert (isinstance(__user_id, int) and __user_id >= 0), \
        'User id should be non-negative integer or a string (username).'
    d = kwargs
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
        return create(_user_id=__user_id, **d)
    raise EmptyRecordInsertionError('Cannot insert empty record into vault table.')


def read_vault_passwords(cond: dict = None, doc_ids: Iterable[int] = None):
    if cond is not None:
        cond = create_query(cond, logic='and')
    items = read(cond, doc_ids=doc_ids)
    return items


def read_vault_password(doc_id: int, cond: dict = None):
    if cond is not None:
        cond = create_query(cond, logic='and')
    return read_one(doc_id=doc_id, cond=cond)


def update_vault_passwords(
        cond: dict = None,
        doc_ids: Iterable[int] = None,
        *,
        pw: str = None,
        salt: str = None,
        user: str = None,
        name: str = None,
        email: str = None,
        site: str = None,
        **kwargs):
    if cond is not None:
        cond = create_query(cond, logic='and')
    # do not allow updating the value of special _user_id field
    _user_id = kwargs.pop('_user_id', None)
    items = update(cond, doc_ids, pw=pw, salt=salt, user=user, label=name, email=email, site=site, **kwargs)
    return items


def update_vault_password(
        doc_id: int,
        *,
        pw: str = None,
        salt: str = None,
        user: str = None,
        name: str = None,
        email: str = None,
        site: str = None,
        **kwargs):
    items = update_vault_passwords(
        None, doc_ids=[doc_id], pw=pw, salt=salt, user=user, name=name, email=email, site=site, **kwargs)
    try:
        return items[0]
    except IndexError:
        return None


def delete_vault_passwords(cond: dict = None, doc_ids: Iterable[int] = None):
    if cond is not None:
        cond = create_query(cond, logic='and')
    items = delete(cond, doc_ids)
    return items


def delete_vault_password(doc_id: int):
    items = delete_vault_passwords(None, doc_ids=[doc_id])
    try:
        return items[0]
    except IndexError:
        return None

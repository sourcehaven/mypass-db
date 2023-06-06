from typing import Iterable

from mypass.db import create_query
from mypass.db.tiny.vault import read, update, delete


def read_vault_passwords(cond: dict = None):
    if cond is not None:
        cond = create_query(cond, logic='and')
    items = read(cond)
    return items


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
    items = update(cond, doc_ids, pw=pw, salt=salt, user=user, name=name, email=email, site=site, **kwargs)
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

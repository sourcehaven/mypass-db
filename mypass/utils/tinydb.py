from typing import Iterable

from tinydb.table import Document

from mypass.db import create_query

ID_FIELD = '_id'
UID_FIELD = '_UID'


def check_uid(__uid: int, assert_err: bool = True):
    if __uid is None:
        return True
    if isinstance(__uid, int) and __uid >= 0:
        return True
    if assert_err:
        assert False, 'User id should be non-negative integer.'
    return False


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

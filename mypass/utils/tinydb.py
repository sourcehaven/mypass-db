from typing import Iterable

from tinydb.table import Document

from mypass.types import const
from .common import is_protected_key


def check_uid(__uid: int, assert_err: bool = True):
    if __uid is None:
        return True
    if isinstance(__uid, int) and __uid >= 0:
        return True
    if assert_err:
        assert False, 'User id should be non-negative integer.'
    return False


def filter_doc_ids(documents: list[Document], doc_ids: Iterable[int] = None):
    if doc_ids is not None:
        doc_ids = set(doc_ids)
        documents = [doc for doc in documents if doc.doc_id in doc_ids]
    return documents


def document_as_dict(document: Document, keep_id: bool = False, remove_special: bool = True) -> dict:
    if remove_special:
        # remove every special field except `ID_FIELD` which will be inserted when finishing up
        for k in document.copy():
            if is_protected_key(k):
                del document[k]
    if keep_id:
        return {const.ID_FIELD: document.doc_id, **document}
    return dict(document)


def documents_as_dict(documents: Iterable[Document], keep_id: bool = False, remove_special: bool = True):
    return [document_as_dict(doc, keep_id=keep_id, remove_special=remove_special) for doc in documents]

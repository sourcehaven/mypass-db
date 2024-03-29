from typing import Iterable, Optional, Generic, TypeVar

from tinydb.table import Document

from mypass.db.repository import CrudRepository
from mypass.db.tiny.dao import TinyDao
from mypass.db.utils import create_query

_ID = TypeVar('_ID')
_T = TypeVar('_T')


class TinyRepository(CrudRepository, Generic[_ID, _T]):
    def __init__(self, dao: TinyDao = None, *args, **kwargs):
        assert dao is None or (len(args) == 0 and len(kwargs) == 0), \
            'When dao is specified, there should not be any arguments and/or keyword arguments present.'
        super().__init__()
        if dao is None:
            try:
                dao = TinyDao(*args, **kwargs)
            except TypeError:
                dao = TinyDao(table=self.entity_cls.table, *args, **kwargs)
        self.dao = dao

    def get_table_name(self):
        return self.dao.table

    def create(self, entity: _T) -> _ID:
        if entity.id is not None:
            entity = Document(dict(entity), doc_id=entity.id)
        return self.dao.create(entity=entity)

    def find_one(self, entity: _T) -> Optional[_T]:
        return self.dao.read_one(cond=create_query(dict(entity), 'and'))

    def find_by_id(self, __id: _ID) -> Optional[_T]:
        document = self.dao.read_one(doc_id=__id)
        if document is not None:
            return self.entity_cls(document.doc_id, **document)

    def find_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_T]:
        documents = self.dao.read(doc_ids=__ids)
        return [self.entity_cls(document.doc_id, **document) for document in documents]

    def find_by_crit(self, crit: _T) -> Iterable[_T]:
        documents = self.dao.read(cond=create_query(dict(crit), 'and'))
        return [self.entity_cls(document.doc_id, **document) for document in documents]

    def find(self, __ids: Iterable[_ID], crit: _T) -> Iterable[_T]:
        cond_documents = self.dao.read(cond=create_query(dict(crit), 'and'))
        allowed_ids = set(__ids)
        return [
            self.entity_cls(document.doc_id, **document)
            for document in cond_documents if document.doc_id in allowed_ids
        ]

    def find_all(self) -> Iterable[_T]:
        documents = self.dao.read()
        return [self.entity_cls(document.doc_id, **document) for document in documents]

    def update_by_id(self, __id: _ID, update: _T) -> Optional[_ID]:
        try:
            return self.dao.update(entity=update, doc_ids=[__id])[0]
        except KeyError:
            return None

    def update_by_ids(self, __ids: Iterable[_ID], update: _T) -> Iterable[_ID]:
        # filter out invalid ids first (prevent throwing KeyError)
        __ids = [pk for pk in __ids if self.find_by_id(pk) is not None]
        return self.dao.update(entity=update, doc_ids=__ids)

    def update_by_crit(self, crit: _T, update: _T) -> Iterable[_ID]:
        return self.dao.update(entity=update, cond=create_query(dict(crit), 'and'))

    def update(self, __ids: Iterable[_ID], crit: _T, update: _T) -> Iterable[_ID]:
        cond_documents = self.dao.read(cond=create_query(dict(crit), 'and'))
        allowed_ids = set(__ids)
        document_ids_to_update = [doc.doc_id for doc in cond_documents if doc.doc_id in allowed_ids]
        return self.dao.update(entity=update, doc_ids=document_ids_to_update)

    def update_all(self, update: _T) -> Iterable[_ID]:
        return self.dao.update(entity=update)

    def remove_by_id(self, __id: _ID) -> Optional[_ID]:
        items = self.dao.delete(doc_ids=[__id])
        try:
            return items[0]
        except IndexError:
            return None

    def remove_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_ID]:
        return self.dao.delete(doc_ids=__ids)

    def remove_by_crit(self, crit: _T) -> Iterable[_ID]:
        return self.dao.delete(cond=crit)

    def remove(self, __ids: Iterable[_ID], crit: _T) -> Iterable[_ID]:
        cond_documents = self.dao.read(cond=create_query(dict(crit), 'and'))
        allowed_ids = set(__ids)
        document_ids_to_delete = [doc.doc_id for doc in cond_documents if doc.doc_id in allowed_ids]
        return self.dao.delete(doc_ids=document_ids_to_delete)

    def remove_all(self):
        self.dao.delete_all()

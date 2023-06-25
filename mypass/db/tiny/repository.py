from typing import Iterable, Optional, Generic, TypeVar

from mypass.db import CrudRepository, create_query

from .dao import TinyDao

_ID = TypeVar('_ID')
_T = TypeVar('_T')


class TinyRepository(CrudRepository, Generic[_ID, _T]):
    def __init__(self, dao: TinyDao = None, *args, **kwargs):
        assert dao is None or (len(args) == 0 and len(kwargs) == 0), \
            'When dao is specified, there should not be any arguments and/or keyword arguments present.'
        # noinspection PyUnresolvedReferences
        # insane hacking -> get stored entity type from original bases
        generic_info = self.__class__.__orig_bases__[0]
        # by convention, the second parameter will be the contained type
        self.entity_cls = generic_info.__args__[1]
        if dao is None:
            try:
                dao = TinyDao(*args, **kwargs)
            except TypeError:
                dao = TinyDao(table=self.entity_cls.table, *args, **kwargs)
        self.dao = dao

    def get_table_name(self):
        return self.dao.table

    def create(self, entity: _T) -> _ID:
        return self.dao.create(entity=entity)

    def find(self, entity: _T) -> Optional[_T]:
        return self.dao.read_one(cond=create_query(dict(entity), 'and'))

    def find_by_id(self, __id: _ID) -> Optional[_T]:
        document = self.dao.read_one(doc_id=__id)
        if document is not None:
            return self.entity_cls(document.doc_id, **document)

    def find_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_T]:
        documents = self.dao.read(doc_ids=__ids)
        return [self.entity_cls(document.doc_id, **document) for document in documents]

    def find_where(self, __ids: Iterable[_ID], entity: _T) -> Iterable[_T]:
        cond_documents = self.dao.read(cond=create_query(dict(entity), 'and'))
        allowed_ids = set(__ids)
        return [
            self.entity_cls(document.doc_id, **document)
            for document in cond_documents if document.doc_id in allowed_ids
        ]

    def update_by_id(self, __id: _ID, update: _T) -> _ID:
        return self.dao.update(entity=update, doc_ids=[__id])

    def update_by_ids(self, __ids: Iterable[_ID], update: _T) -> Iterable[_ID]:
        return self.dao.update(entity=update, doc_ids=__ids)

    def update(self, __ids: Iterable[_ID], entity: _T, update: _T) -> Iterable[_ID]:
        cond_documents = self.dao.read(cond=create_query(dict(entity), 'and'))
        allowed_ids = set(__ids)
        document_ids_to_update = [doc.doc_id for doc in cond_documents if doc.doc_id in allowed_ids]
        return self.dao.update(entity=update, doc_ids=document_ids_to_update)

    def remove_by_id(self, __id: _ID) -> _ID:
        return self.dao.delete(doc_ids=[__id])

    def remove_by_ids(self, __ids: Iterable[_ID]) -> Iterable[_ID]:
        return self.dao.delete(doc_ids=__ids)

    def remove(self, __ids: Iterable[_ID], entity: _T) -> Iterable[_ID]:
        cond_documents = self.dao.read(cond=create_query(dict(entity), 'and'))
        allowed_ids = set(__ids)
        document_ids_to_delete = [doc.doc_id for doc in cond_documents if doc.doc_id in allowed_ids]
        return self.dao.delete(doc_ids=document_ids_to_delete)


if __name__ == '__main__':
    class Dog:
        table = 'dogs'

        def __init__(self):
            self.name = 'name'
            self.tag = 52

    class MyRepo(TinyRepository[int, Dog]):
        pass

    repo = MyRepo()

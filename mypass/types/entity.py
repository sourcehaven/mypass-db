from typing import Optional, Generic, TypeVar, Mapping

from .elastic import ElasticClass

_ID = TypeVar('_ID', str, int)
_T = TypeVar('_T')


def table(t: str):
    def entity_wrapper(cls: Generic[_T]):
        cls.table = t
        return cls

    return entity_wrapper


class Entity(ElasticClass, Generic[_ID]):
    def __init__(self, __id: _ID, value: Mapping):
        super().__init__(**value)
        self.__id = __id

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, __id: _ID):
        self.__id = __id


@table('master')
class MasterEntity(Entity[int | str]):
    user: Optional[str]
    token: Optional[str]
    pw: Optional[str]
    salt: Optional[str]

    def __init__(
            self,
            __id: Optional[int | str] = None,
            *,
            user: str = None,
            token: str = None,
            pw: str = None,
            salt: str = None
    ):
        super().__init__(__id, value=dict(user=user, token=token, pw=pw, salt=salt))


@table('vault')
class VaultEntity(Entity[int | str]):
    pw: Optional[str]
    salt: Optional[str]
    user: Optional[str]
    label: Optional[str]
    email: Optional[str]
    site: Optional[str]

    def __init__(
            self,
            __id: Optional[int | str] = None,
            *,
            pw: str = None,
            salt: str = None,
            user: str = None,
            label: str = None,
            email: str = None,
            site: str = None,
            **kwargs
    ):
        super().__init__(__id, value=dict(user=user, pw=pw, salt=salt, label=label, email=email, site=site, **kwargs))

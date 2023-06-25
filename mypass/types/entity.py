from typing import Optional, Generic, TypeVar

from mypass.types.elastic import ElasticClass
from mypass.utils import GetSetDescriptor, GetDescriptor


T = TypeVar('T')


def entity(table: str):
    def entity_wrapper(cls: Generic[T]):
        cls.__table = table
        cls.id = GetSetDescriptor('__id')
        cls.table = GetDescriptor('__table')
        return cls
    return entity_wrapper


@entity('master')
class MasterVaultEntity(ElasticClass):
    user: Optional[str]
    token: Optional[str]
    pw: Optional[str]
    salt: Optional[str]

    def __init__(
            self,
            __id: Optional[int] = None,
            *,
            user: str = None,
            token: str = None,
            pw: str = None,
            salt: str = None
    ):
        super().__init__(user=user, token=token, pw=pw, salt=salt)
        self.id = __id


@entity('vault')
class PasswordVaultEntity(ElasticClass):
    pw: Optional[str]
    salt: Optional[str]
    user: Optional[str]
    label: Optional[str]
    email: Optional[str]
    site: Optional[str]

    def __init__(
            self,
            __id: Optional[int] = None,
            *,
            pw: str = None,
            salt: str = None,
            user: str = None,
            label: str = None,
            email: str = None,
            site: str = None,
            **kwargs
    ):
        super().__init__(user=user, pw=pw, salt=salt, label=label, email=email, site=site, **kwargs)
        self.id = __id


if __name__ == '__main__':
    vault_entry = PasswordVaultEntity(1, user='mypass-user', pw='mypass_pw')
    myid = vault_entry.id
    print(vault_entry)

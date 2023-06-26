from typing import Iterable

from mypass.types import const


def is_protected_key(k: str):
    return k.startswith('_') and k.upper() == k


def entity_as_dict(entity, keep_id: bool = False, remove_special: bool = True) -> dict:
    if remove_special:
        # remove every special field except `ID_FIELD` which will be inserted when finishing up
        for k in entity.copy():
            if is_protected_key(k):
                del entity[k]
    if keep_id:
        return {const.ID_FIELD: entity.id, **entity}
    return dict(entity)


def entities_as_dict(entities: Iterable, keep_id: bool = False, remove_special: bool = True):
    return [entity_as_dict(entity, keep_id=keep_id, remove_special=remove_special) for entity in entities]

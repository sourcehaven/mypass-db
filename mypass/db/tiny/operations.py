from typing import Iterable, Mapping

from mypass.types.op import DEL


def delete_keys(keys: Iterable[str], ignore_keyerr: bool = True):
    keys = set(keys)

    def operation(document):
        for k in document.copy():
            if k in keys:
                try:
                    del document[k]
                except KeyError as e:
                    if not ignore_keyerr:
                        raise e
    return operation


def update(fields: Mapping, ignore_keyerr: bool = True):
    # operation will get the original document
    def operation(document):
        for k in document.copy():
            if k in fields:
                if fields[k] == DEL:
                    try:
                        del document[k]
                    except KeyError as e:
                        if not ignore_keyerr:
                            raise e
                else:
                    document[k] = fields[k]

    return operation

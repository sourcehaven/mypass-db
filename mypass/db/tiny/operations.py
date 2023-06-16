from typing import Iterable


def delete_keys(keys: Iterable[str], ignore_keyerr: bool = True):
    keys = set(keys)

    def operation(document):
        for k in document:
            if k in keys:
                try:
                    del document[k]
                except KeyError as e:
                    if not ignore_keyerr:
                        raise e
    return operation

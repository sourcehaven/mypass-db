import base64
import hashlib
import uuid
from typing import Literal


def hash_fn(key: str):
    secret = hashlib.sha3_512(key.encode('utf-8')).digest()
    secret = base64.urlsafe_b64encode(secret)
    return secret


def gen_uuid(t: Literal['str', 'int', 'bytes', 'bytes_le']):
    identity = uuid.uuid4()
    if t == 'str':
        return identity.hex
    if t == 'int':
        return identity.int
    if t == 'bytes_le':
        return identity.bytes_le
    raise TypeError(f'Generating unique identifier of type {t} is not supported.')

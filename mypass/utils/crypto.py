import base64
import hashlib


def hash_fn(key: str):
    secret = hashlib.sha3_512(key.encode('utf-8')).digest()
    secret = base64.urlsafe_b64encode(secret)
    return secret

from werkzeug.exceptions import UnsupportedMediaType

from mypass.persistence.blacklist.memory import blacklist


# noinspection PyUnusedLocal
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklist


def base_error_handler(err: Exception):
    return {'msg': f'{err.__class__.__name__} :: {err}'}, 500


def unsupported_media_type_handler(err: UnsupportedMediaType):
    return {'msg': str(err)}, 415

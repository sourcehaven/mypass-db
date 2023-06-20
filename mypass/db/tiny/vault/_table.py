from mypass.db.tiny import TinyTable

_db_opts = {
    'name': 'vault',
    'db_args': [],
    'db_kwargs': {}
}


def vault():
    return TinyTable(_db_opts['name'], *_db_opts['db_args'], **_db_opts['db_kwargs'])

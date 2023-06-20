from mypass.db.tiny import TinyTable

_db_opts = {
    'name': 'master',
    'db_args': [],
    'db_kwargs': {}
}


def master():
    return TinyTable(_db_opts['name'], *_db_opts['db_args'], **_db_opts['db_kwargs'])

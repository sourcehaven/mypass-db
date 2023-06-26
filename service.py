import logging
from argparse import ArgumentParser, Namespace
from datetime import timedelta
from pathlib import Path

import waitress
from flask import Flask
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import UnsupportedMediaType

from mypass import hooks
from mypass.api import AuthApi, TinyDbApi
from mypass.db.tiny import MasterTinyRepository, VaultTinyRepository
from mypass.public import IndexTemplate
from mypass.utils import hash_fn

HOST = 'localhost'
PORT = 5758
JWT_KEY = 'sourcehaven-db'


class MyPassArgs(Namespace):
    debug: bool
    host: str
    port: int
    jwt_key: str


def run(debug=False, host=HOST, port=PORT, jwt_key=JWT_KEY, api_key=None):
    db_path = Path.home().joinpath('.mypass', 'db', 'tinydb', 'db.json')

    if api_key is not None:
        api_key = hash_fn(api_key)

    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = jwt_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app.config['API_KEY'] = api_key
    app.config['master_controller'] = MasterTinyRepository(path=db_path)
    app.config['vault_controller'] = VaultTinyRepository(path=db_path)
    app.config.from_object(__name__)

    # register api endpoints
    app.register_blueprint(AuthApi)
    app.register_blueprint(TinyDbApi)
    # add public templates
    app.register_blueprint(IndexTemplate)

    app.register_error_handler(UnsupportedMediaType, hooks.unsupported_media_type_handler)
    app.register_error_handler(Exception, hooks.base_error_handler)

    jwt = JWTManager(app)
    jwt.token_in_blocklist_loader(hooks.check_if_token_in_blacklist)

    if debug:
        app.run(host=host, port=port, debug=True)
    else:
        waitress.serve(app, host=host, port=port, channel_timeout=10, threads=8)


if __name__ == '__main__':
    arg_parser = ArgumentParser('MyPass')
    arg_parser.add_argument(
        '-d', '--debug', action='store_true', default=False,
        help='flag for debugging mode')
    arg_parser.add_argument(
        '-H', '--host', type=str, default=HOST,
        help=f'specifies the host for the microservice, defaults to "{HOST}"')
    arg_parser.add_argument(
        '-p', '--port', type=int, default=PORT,
        help=f'specifies the port for the microservice, defaults to {PORT}')
    arg_parser.add_argument(
        '-k', '--jwt-key', type=str, default=JWT_KEY,
        help=f'specifies the secret jwt key by the application, defaults to "{JWT_KEY}" (should be changed)')
    arg_parser.add_argument(
        '-P', '--api-key', type=str, default=None,
        help=f'specifies the secret api key by the application, defaults to "{None}" (should be set)')

    args = arg_parser.parse_args(namespace=MyPassArgs)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)
    run(debug=args.debug, host=args.host, port=args.port, jwt_key=args.jwt_key, api_key=args.api_key)

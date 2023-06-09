import logging
from argparse import ArgumentParser, Namespace
from datetime import timedelta
from typing import Optional

import waitress
from flask import Flask
from flask_jwt_extended import JWTManager

from mypass import hooks
from mypass.api import AuthApi, MasterDbApi, VaultDbApi

HOST = None
PORT = 5758
JWT_KEY = 'sourcehaven-db'


class MyPassArgs(Namespace):
    debug: bool
    host: Optional[str]
    port: int
    jwt_key: str


def run(debug=False, host=HOST, port=PORT, jwt_key=JWT_KEY):
    app = Flask(__name__)
    app.register_blueprint(AuthApi)
    app.register_blueprint(MasterDbApi)
    app.register_blueprint(VaultDbApi)

    app.config['JWT_SECRET_KEY'] = jwt_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    jwt = JWTManager(app)
    jwt.token_in_blocklist_loader(hooks.check_if_token_in_blacklist)

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        app.run(host=host, port=port, debug=True)
    else:
        logging.basicConfig(level=logging.ERROR)
        waitress.serve(app, host=host, port=port, channel_timeout=10, threads=1)


if __name__ == '__main__':
    arg_parser = ArgumentParser('MyPass')
    arg_parser.add_argument(
        '-d', '--debug', action='store_true', default=False,
        help='flag for debugging mode')
    arg_parser.add_argument(
        '-H', '--host', type=str, default=None,
        help=f'specifies the host for the microservice, defaults to "{None}"')
    arg_parser.add_argument(
        '-p', '--port', type=int, default=PORT,
        help=f'specifies the port for the microservice, defaults to {PORT}')
    arg_parser.add_argument(
        '-k', '--jwt-key', type=str, default=JWT_KEY,
        help=f'specifies the secret jwt key by the application, defaults to "{JWT_KEY}" (should be changed)')

    args = arg_parser.parse_args(namespace=MyPassArgs)
    run(debug=args.debug, host=args.host, port=args.port, jwt_key=args.jwt_key)

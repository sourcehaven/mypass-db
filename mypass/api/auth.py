import logging
import os

import flask
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt

from mypass.persistence.blacklist.memory import blacklist
from mypass.utils import hash_fn

AuthApi = Blueprint('auth', __name__)

__STATE = {'logged_in': False}


@AuthApi.route('/api/auth/login', methods=['POST'])
def login():
    logging.getLogger().debug(f'Signing in user with\n    {request.json}')
    son = request.json
    pw = son['pw']
    key = flask.current_app.config['API_KEY']
    if key is None or hash_fn(pw) == key:
        logging.getLogger().debug('Clearing blacklists.')
        blacklist.clear()
        logging.getLogger().debug('Creating fresh access token.')
        access_token = create_access_token(identity=pw, fresh=True)
        refresh_token = create_refresh_token(identity=pw)
        logging.getLogger().debug(
            f'Returning access and refresh tokens\n    {dict(access_token="*****", refresh_token="*****")}')
        return {'access_token': access_token, 'refresh_token': refresh_token}, 201
    return {'msg': 'NOT AUTHORIZED :: Wrong password provided. Use the secret api key you provided.'}, 401


@AuthApi.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True, optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def refresh():
    pw = get_jwt_identity()
    logging.getLogger().debug('Creating non-fresh access token.')
    access_token = create_access_token(identity=pw, fresh=False)
    logging.getLogger().debug(
        f'Returning access token\n    {dict(access_token="*****")}')
    return {'access_token': access_token}, 201


@AuthApi.route('/api/auth/logout', methods=['DELETE'])
@jwt_required(optional=True)
def logout():
    logging.getLogger().debug('Logging out user.')
    try:
        jti = get_jwt()['jti']
        logging.getLogger().debug(f'Blacklisting token: {jti}.')
        blacklist.add(jti)
        # __STATE['logged_in'] = False
        return '', 204
    except KeyError:
        return '', 409

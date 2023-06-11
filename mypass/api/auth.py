import logging

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt

from mypass.persistence.blacklist.memory import blacklist

AuthApi = Blueprint('auth', __name__)


@AuthApi.route('/api/auth/login', methods=['POST'])
def login():
    # TODO: see if api has already logged in -> what to do?
    #  - force logout first
    #  - invalidate previous user
    #  - warn and renew tokens
    logging.getLogger().debug('Clearing blacklists.')
    logging.getLogger().debug(f'Signing in user with\n    {request.json}')
    blacklist.clear()
    son = request.json
    pw = son['pw']
    logging.getLogger().debug('Creating non-fresh access token.')
    access_token = create_access_token(identity=pw, fresh=True)
    refresh_token = create_refresh_token(identity=pw)
    logging.getLogger().debug(
        f'Returning access and refresh tokens\n    {dict(access_token="*****", refresh_token="*****")}')
    return {'access_token': access_token, 'refresh_token': refresh_token}, 201


@AuthApi.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
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
        return '', 204
    except KeyError:
        return '', 201

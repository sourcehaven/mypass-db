from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

AuthApi = Blueprint('auth', __name__)


@AuthApi.route('/api/auth/signup')
def signup():
    son = request.json
    pw = son['pw']
    access_token = create_access_token(identity=pw, fresh=True)
    refresh_token = create_refresh_token(identity=pw)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }, 201


@AuthApi.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def get_login():
    pw = get_jwt_identity()
    access_token = create_access_token(identity=pw, fresh=False)
    return {
        'access_token': access_token
    }, 201

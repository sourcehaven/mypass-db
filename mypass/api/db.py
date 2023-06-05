from flask import Blueprint
from flask_jwt_extended import jwt_required

DbApi = Blueprint('db', __name__)


@DbApi.route('/api/db/test', methods=['POST'])
def test():
    return {'message': 'Hello There!'}, 200


@DbApi.route('/api/db/secret-test', methods=['POST'])
@jwt_required()
def secret_test():
    return {'message': 'Pssst... Hello There!'}, 200


@DbApi.route('/api/db/fresh-secret-test', methods=['POST'])
@jwt_required(fresh=True)
def fresh_secret_tests():
    return {'message': 'Pssst... Hello There! Fresh as new, eh?'}, 200

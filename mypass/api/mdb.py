from flask import request
from flask_jwt_extended import jwt_required

from mypass.db.tiny.master import create, read
from . import DbApi


@DbApi.route('/api/db/tiny/master/create', methods=['POST'])
@jwt_required(fresh=True)
def create_vault_entry():
    son = request.json
    entry_id = create(**son)
    return {'id': entry_id}, 200


@DbApi.route('/api/db/tiny/master/read', methods=['POST'])
@jwt_required(fresh=True)
def query_vault_entry():
    documents = read()
    return {'documents': documents}, 200


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

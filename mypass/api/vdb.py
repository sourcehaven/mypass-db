from flask import request
from flask_jwt_extended import jwt_required

from mypass.db.tiny.vault import create, read, update, delete
from . import DbApi


@DbApi.route('/api/db/tiny/vault/create', methods=['POST'])
@jwt_required()
def create_vault_entry():
    son = request.json
    entry_id = create(**son)
    return {'id': entry_id}, 200


@DbApi.route('/api/db/tiny/vault/read', methods=['POST'])
@jwt_required()
def query_vault_entry():
    son = request.json
    documents = read(**son)
    return {'documents': documents}, 200


@DbApi.route('/api/db/tiny/vault/update', methods=['POST'])
@jwt_required()
def update_vault_entry():
    son = request.json
    ids = update(**son)
    return {'ids': ids}, 200


@DbApi.route('/api/db/tiny/vault/delete', methods=['POST'])
@jwt_required()
def delete_vault_entry():
    son = request.json
    ids = delete(**son)
    return {'ids': ids}, 200

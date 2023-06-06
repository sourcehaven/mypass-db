from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import UnsupportedMediaType

from mypass import create_vault_password, read_vault_passwords, update_vault_password, delete_vault_password

VaultDbApi = Blueprint('vdb', __name__)


@VaultDbApi.route('/api/db/tiny/vault/create', methods=['POST'])
@jwt_required()
def create_vault_entry():
    entry_id = create_vault_password(**request.json)
    return {'id': entry_id}, 200


@VaultDbApi.route('/api/db/tiny/vault/read', methods=['POST'])
@jwt_required()
def query_vault_entry():
    try:
        documents = read_vault_passwords(**request.json)
    except UnsupportedMediaType:
        documents = read_vault_passwords()

    return {'documents': documents}, 200


@VaultDbApi.route('/api/db/tiny/vault/update', methods=['POST'])
@jwt_required()
def update_vault_entry():
    entry_id = update_vault_password(**request.json)
    return {'ids': entry_id}, 200


@VaultDbApi.route('/api/db/tiny/vault/delete', methods=['POST'])
@jwt_required()
def delete_vault_entry():
    entry_id = delete_vault_password(**request.json)
    return {'ids': entry_id}, 200

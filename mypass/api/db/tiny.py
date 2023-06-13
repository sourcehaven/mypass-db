import logging
import os

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import UnsupportedMediaType

from mypass import create_master_password, read_master_password, update_master_password, \
    create_vault_password, read_vault_password, read_vault_passwords, update_vault_password, update_vault_passwords, \
    delete_vault_password, delete_vault_passwords, document_as_dict, documents_as_dict
from mypass.exceptions import MasterPasswordExistsError, MultipleMasterPasswordsError

TinyDbApi = Blueprint('tinydb', __name__)


@TinyDbApi.errorhandler(MasterPasswordExistsError)
def master_password_exists_handler(err):
    return {'msg': str(err)}, 500


@TinyDbApi.errorhandler(MultipleMasterPasswordsError)
def multiple_master_passwords_handler(err):
    return {'msg': str(err)}, 500


@TinyDbApi.route('/api/db/tiny/master/create', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def create_master_pw():
    logging.getLogger().debug(f'Creating master password with params\n    {request.json}')
    pw, salt = request.json['pw'], request.json['salt']
    doc_id = create_master_password(pw=pw, salt=salt)
    logging.getLogger().debug(f'Created master password with id: {doc_id}')
    return {'_id': doc_id}, 201


@TinyDbApi.route('/api/db/tiny/master/read', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def query_master_pw():
    logging.getLogger().debug(f'Reading master password.')
    doc = read_master_password()
    logging.getLogger().debug(f'Read master password: {doc}')
    return doc, 200


@TinyDbApi.route('/api/db/tiny/master/update', methods=['POST'])
@jwt_required(fresh=True, optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def update_master_pw():
    logging.getLogger().debug(f'Updating master password with params\n    {request.json}')
    pw, salt = request.json['pw'], request.json['salt']
    doc_id = update_master_password(pw=pw, salt=salt)
    logging.getLogger().debug(f'Updated master password with id: {doc_id}')
    return {'_id': doc_id}, 200


@TinyDbApi.route('/api/db/tiny/vault/create', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def create_vault_entry():
    request_obj = request.json
    logging.getLogger().debug(f'Creating password inside user vault with params\n    {request_obj}')
    doc_id = create_vault_password(**request_obj)
    logging.getLogger().debug(f'Created password inside vault with id: {doc_id}')
    return {'_id': doc_id}, 201


@TinyDbApi.route('/api/db/tiny/vault/read', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def query_vault_entry():
    try:
        request_obj = request.json
        if '_id' in request_obj:
            return document_as_dict(read_vault_password(doc_id=request_obj['_id']), keep_id=True), 200
        documents = documents_as_dict(read_vault_passwords(request_obj.get('cond', None)), keep_id=True)
    except UnsupportedMediaType:
        documents = documents_as_dict(read_vault_passwords(), keep_id=True)

    return {'documents': documents}, 200


@TinyDbApi.route('/api/db/tiny/vault/update', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def update_vault_entry():
    request_obj = dict(request.json)
    doc_id = request_obj.pop('_id', None)
    if doc_id is not None:
        doc_id = update_vault_password(doc_id=doc_id, **request_obj)
        return {'_id': doc_id}, 200
    doc_ids = request_obj.pop('_ids', None)
    doc_ids = update_vault_passwords(doc_ids=doc_ids, **request_obj)
    return {'_ids': doc_ids}, 200


@TinyDbApi.route('/api/db/tiny/vault/delete', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def delete_vault_entry():
    request_obj = dict(request.json)
    doc_id = request_obj.pop('_id', None)
    if doc_id is not None:
        doc_id = delete_vault_password(doc_id=doc_id)
        return {'_id': doc_id}, 200
    doc_ids = request_obj.pop('_ids', None)
    doc_ids = delete_vault_passwords(doc_ids=doc_ids, **request_obj)
    return {'_ids': doc_ids}, 200

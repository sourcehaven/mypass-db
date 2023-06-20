import logging
import os

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import UnsupportedMediaType

from mypass import create_master_password, read_master_password, update_master_password, \
    create_vault_entry, read_vault_entry, read_vault_entries, update_vault_entry, update_vault_entries, \
    delete_vault_entry, delete_vault_entries
from mypass.exceptions import MasterPasswordExistsError, MultipleMasterPasswordsError, EmptyRecordInsertionError

from . import _utils as utils


TinyDbApi = Blueprint('tinydb', __name__)


def _db_error_handler(err):
    return {'msg': f'{err.__class__.__name__} :: {err}'}, 500


@TinyDbApi.errorhandler(MasterPasswordExistsError)
def master_password_exists_handler(err):
    return _db_error_handler(err)


@TinyDbApi.errorhandler(MultipleMasterPasswordsError)
def multiple_master_passwords_handler(err):
    return _db_error_handler(err)


@TinyDbApi.errorhandler(EmptyRecordInsertionError)
def empty_record_insertion_handler(err):
    return _db_error_handler(err)


@TinyDbApi.route('/api/db/tiny/master/create', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def create_master_pw():
    request_obj = request.json
    logging.getLogger().debug(f'Creating master password with params\n    {request_obj}')
    user, token, pw, salt = request_obj['user'], request_obj['token'], request_obj['pw'], request_obj['salt']
    doc_id = create_master_password(user=user, token=token, pw=pw, salt=salt)
    logging.getLogger().debug(f'Created master password with id: {doc_id}')
    return {'_id': doc_id}, 201


@TinyDbApi.route('/api/db/tiny/master/read', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def query_master_pw():
    request_obj = request.json
    logging.getLogger().debug(f'Reading master password with params\n    {request_obj}')
    user = request_obj.pop('user', None)
    uid = request_obj.pop('uid', None)
    if user is None and uid is None:
        return {'msg': 'BAD REQUEST :: You should specify at least one of `user` or `uid` in the request'}, 400
    # user value will only be used if uid is not provided
    if uid is None:
        uid = user
    doc = read_master_password(uid)
    doc.pop('user', None)
    logging.getLogger().debug(f'Read master password: {doc}')
    return doc, 200


@TinyDbApi.route('/api/db/tiny/master/update', methods=['POST'])
@jwt_required(fresh=True, optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def update_master_pw():
    logging.getLogger().debug(f'Updating master password with params\n    {request.json}')
    user, token, pw, salt = request.json['user'], request.json['token'], request.json['pw'], request.json['salt']
    doc_id = update_master_password(user=user, token=token, pw=pw, salt=salt)
    logging.getLogger().debug(f'Updated master password with id: {doc_id}')
    return {'_id': doc_id}, 200


@TinyDbApi.route('/api/db/tiny/vault/create', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def new_vault_entry():
    request_obj = dict(request.json)
    logging.getLogger().debug(f'Creating password inside user vault with params\n    {request_obj}')
    # see if the main user is passed along the request
    uid = request_obj.pop('uid', None)
    fields = request_obj.pop('fields', None)
    if fields is not None:
        fields = fields.copy()
    # clearn every other unhandled special items, except salt
    # TODO: need configurable whitelist?
    fields = utils.clear_special_keys(fields, whitelist=['_salt'])
    doc_id = create_vault_entry(uid, **fields)
    logging.getLogger().debug(f'Created password inside vault with id: {doc_id}')
    return {'_id': doc_id}, 201


@TinyDbApi.route('/api/db/tiny/vault/read', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def query_vault_entry():
    try:
        request_obj = dict(request.json)
        doc_id = request_obj.pop('_id', None)
        doc_ids = request_obj.pop('_ids', None)
        uid = request_obj.pop('uid', None)
        cond = request_obj.pop('cond', None)

        if doc_id is not None:
            document: dict = read_vault_entry(uid, doc_id=doc_id, cond=cond)
            if document is not None:
                return document, 200
            return {
                'msg': 'NOT FOUND :: Requested password cannot be read, as it does not exists.',
                '_id': doc_id, 'cond': cond}, 404
        documents = read_vault_entries(uid, cond=cond, doc_ids=doc_ids)
    except UnsupportedMediaType:
        documents = read_vault_entries()
    return documents, 200


@TinyDbApi.route('/api/db/tiny/vault/update', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def change_vault_entry():
    request_obj = dict(request.json)
    doc_id = request_obj.pop('_id', None)
    doc_ids = request_obj.pop('_ids', None)
    uid = request_obj.pop('uid', None)
    cond = request_obj.pop('cond', None)
    remove_keys = request_obj.pop('remove_keys', None)
    fields = request_obj.pop('fields', None)
    if fields is not None:
        fields = utils.clear_special_keys(fields)

    if doc_id is not None:
        updated_id: int = update_vault_entry(
            uid, fields=fields, doc_id=doc_id, cond=cond, remove_keys=remove_keys)
        if updated_id is not None:
            return {'_id': updated_id}, 200
        return {
            'msg': 'NOT FOUND :: Requested password update cannot be done, as it does not exists.',
            '_id': doc_id, 'cond': cond}, 404
    updated_ids = update_vault_entries(
        uid, fields=fields, cond=cond, doc_ids=doc_ids, remove_keys=remove_keys)
    return {'_ids': updated_ids}, 200


@TinyDbApi.route('/api/db/tiny/vault/delete', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def remove_vault_entry():
    request_obj = dict(request.json)
    doc_id = request_obj.pop('_id', None)
    doc_ids = request_obj.pop('_ids', None)
    uid = request_obj.pop('uid', None)
    cond = request_obj.pop('cond', None)

    if doc_id is not None:
        deleted_id: int = delete_vault_entry(uid, doc_id=doc_id, cond=cond)
        if deleted_id is not None:
            return {'_id': deleted_id}, 200
        return {
            'msg': 'NOT FOUND :: Requested password cannot be deleted, as it does not exists.',
            '_id': doc_id, 'cond': cond}, 404
    deleted_ids = delete_vault_entries(uid, cond=cond, doc_ids=doc_ids)
    return {'_ids': deleted_ids}, 200

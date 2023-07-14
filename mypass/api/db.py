import logging
import os

import flask
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import UnsupportedMediaType

from mypass import utils
from mypass.db import MasterDbSupport, VaultDbSupport
from mypass.exceptions import MasterPasswordExistsError, MultipleMasterPasswordsError, EmptyRecordInsertionError, \
    RecordNotFoundError
from mypass.types import MasterEntity, VaultEntity

# TODO: Should all _write_ endpoints need fresh=True token?
DbApi = Blueprint('db', __name__)


def _db_error_handler(err):
    return {'msg': f'{err.__class__.__name__} :: {err}'}, 500


@DbApi.errorhandler(MasterPasswordExistsError)
def master_password_exists_handler(err):
    return _db_error_handler(err)


@DbApi.errorhandler(MultipleMasterPasswordsError)
def multiple_master_passwords_handler(err):
    return _db_error_handler(err)


@DbApi.errorhandler(EmptyRecordInsertionError)
def empty_record_insertion_handler(err):
    return _db_error_handler(err)


@DbApi.errorhandler(RecordNotFoundError)
def record_not_found_handler(err):
    return {'msg': f'{err.__class__.__name__} :: {err}'}, 404


@DbApi.route('/api/db/master/create', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def create_master_pw():
    controller: MasterDbSupport = flask.current_app.config['master_controller']
    request_obj = dict(request.json)
    logging.getLogger().debug(f'Creating master password with params\n    {request_obj}')
    entity_id = request_obj.get('id', None)
    user, token, pw, salt = request_obj['user'], request_obj['token'], request_obj['pw'], request_obj['salt']
    entity = MasterEntity(entity_id, user=user, token=token, pw=pw, salt=salt)
    entity_id = controller.create_master_password(entity)
    logging.getLogger().debug(f'Created master password with id: {entity_id}')
    return {'id': entity_id}, 201


@DbApi.route('/api/db/master/read', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def query_master_pw():
    controller: MasterDbSupport = flask.current_app.config['master_controller']
    request_obj = dict(request.json)
    logging.getLogger().debug(f'Reading master password with params\n    {request_obj}')
    user = request_obj.get('user', None)
    uid = request_obj.get('uid', None)
    if user is None and uid is None:
        return {'msg': 'BAD REQUEST :: You should specify at least one of `user` or `uid` in the request'}, 400
    # user value will only be used if uid is not provided
    if uid is None:
        uid = user
    pw = controller.read_master_password(uid)
    logging.getLogger().debug(f'Read master password: {pw}')
    return {'pw': pw}, 200


@DbApi.route('/api/db/master/update', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def update_master_pw():
    controller: MasterDbSupport = flask.current_app.config['master_controller']
    logging.getLogger().debug(f'Updating master password with params\n    {request.json}')
    uid, token, pw, salt = request.json['uid'], request.json['token'], request.json['pw'], request.json['salt']
    update = MasterEntity(token=token, pw=pw, salt=salt)
    entity_id = controller.update_master_password(uid, update)
    logging.getLogger().debug(f'Updated master password with id: {entity_id}')
    return {'id': entity_id}, 200


@DbApi.route('/api/db/vault/create', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def new_vault_entry():
    controller: VaultDbSupport = flask.current_app.config['vault_controller']
    request_obj = dict(request.json)
    logging.getLogger().debug(f'Creating password inside user vault with params\n    {request_obj}')
    entity_id = request_obj.get('id', None)
    uid = request_obj.get('uid', None)
    fields = request_obj.get('fields', None)
    if fields is not None:
        fields = fields.copy()
    entity = VaultEntity(entity_id, **fields)
    entity_id = controller.create_vault_entry(uid, entity=entity)
    logging.getLogger().debug(f'Created password inside vault with id: {entity_id}')
    return {'id': entity_id}, 201


@DbApi.route('/api/db/vault/read', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def query_vault_entry():
    controller: VaultDbSupport = flask.current_app.config['vault_controller']
    try:
        request_obj = dict(request.json)
        pk = request_obj.get('id', None)
        pks = request_obj.get('ids', None)
        uid = request_obj.get('uid', None)
        crit = request_obj.get('crit', None)

        if pk is not None:
            entity = controller.read_vault_entry(uid, crit=crit, pk=pk)
            entity_dict = utils.entity_as_dict(entity, keep_id=True, remove_special=False)
            return entity_dict, 200
        if pks is not None or crit is not None:
            entities = controller.read_vault_entries(uid, crit=crit, pks=pks)
            entities_dict = utils.entities_as_dict(entities, keep_id=True, remove_special=False)
            return entities_dict, 200
    except UnsupportedMediaType:
        entities = controller.read_vault_entries()
        entities_dict = utils.entities_as_dict(entities, keep_id=True, remove_special=False)
        return entities_dict, 200


@DbApi.route('/api/db/vault/update', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def change_vault_entry():
    controller: VaultDbSupport = flask.current_app.config['vault_controller']
    request_obj = dict(request.json)
    pk = request_obj.get('id', None)
    pks = request_obj.get('ids', None)
    uid = request_obj.get('uid', None)
    crit = request_obj.get('crit', None)
    fields = request_obj.get('fields', None)

    update = VaultEntity(**fields)
    if pk is not None:
        entity_id = controller.update_vault_entry(uid, update=update, pk=pk)
        return {'id': entity_id}, 200
    entity_ids = controller.update_vault_entries(uid, update=update, crit=crit, pks=pks)
    return [{'id': e_id} for e_id in entity_ids], 200


@DbApi.route('/api/db/vault/delete', methods=['POST'])
@jwt_required(optional=bool(int(os.environ.get('MYPASS_OPTIONAL_JWT_CHECKS', 0))))
def remove_vault_entry():
    controller: VaultDbSupport = flask.current_app.config['vault_controller']
    request_obj = dict(request.json)
    pk = request_obj.get('id', None)
    pks = request_obj.get('ids', None)
    uid = request_obj.get('uid', None)
    crit = request_obj.get('crit', None)

    if pk is not None:
        entity_id = controller.delete_vault_entry(uid, pk=pk)
        return {'id': entity_id}, 200
    entity_ids = controller.delete_vault_entries(uid, crit=crit, pks=pks)
    return [{'id': e_id} for e_id in entity_ids], 200

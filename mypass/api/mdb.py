import logging

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from mypass import create_master_password, read_master_password, update_master_password

MasterDbApi = Blueprint('mdb', __name__)


@MasterDbApi.route('/api/db/tiny/master/create', methods=['POST'])
@jwt_required()
def create_master_pw():
    logging.getLogger().debug(f'Creating master password with params\n    {request.json}')
    entry_id = create_master_password(**request.json)
    logging.getLogger().debug(f'Created master password with id: {entry_id}')
    return {'id': entry_id}, 200


@MasterDbApi.route('/api/db/tiny/master/read', methods=['POST'])
@jwt_required()
def query_master_pw():
    logging.getLogger().debug(f'Reading master password with params\n    {request.json}')
    doc = read_master_password()
    logging.getLogger().debug(f'Read master password: {doc}')
    return doc, 200


@MasterDbApi.route('/api/db/tiny/master/update', methods=['POST'])
@jwt_required(fresh=True)
def update_master_pw():
    logging.getLogger().debug(f'Updating master password with params\n    {request.json}')
    entry_id = update_master_password(**request.json)
    logging.getLogger().debug(f'Updated master password with id: {entry_id}')
    return {'ids': entry_id}, 200

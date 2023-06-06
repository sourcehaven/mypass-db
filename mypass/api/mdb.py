from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from mypass import create_master_password, update_master_password

MasterDbApi = Blueprint('mdb', __name__)


@MasterDbApi.route('/api/db/tiny/master/create', methods=['POST'])
@jwt_required()
def create_master_pw():
    entry_id = create_master_password(**request.json)
    return {'id': entry_id}, 200


@MasterDbApi.route('/api/db/tiny/master/update', methods=['POST'])
@jwt_required(fresh=True)
def update_master_pw():
    entry_id = update_master_password(**request.json)
    return {'ids': entry_id}, 200

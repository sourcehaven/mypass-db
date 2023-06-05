from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from mypass.db.tiny.master import create, read, update

MasterDbApi = Blueprint('mdb', __name__)


@MasterDbApi.route('/api/db/tiny/master/create', methods=['POST'])
@jwt_required(fresh=True)
def create_master_pw():
    son = request.json
    entry_id = create(**son)
    return {'id': entry_id}, 200


@MasterDbApi.route('/api/db/tiny/master/read', methods=['POST'])
@jwt_required(fresh=True)
def query_master_pw():
    documents = read()
    return {'documents': documents}, 200


@MasterDbApi.route('/api/db/tiny/master/update', methods=['POST'])
@jwt_required(fresh=True)
def update_master_pw():
    son = request.json
    ids = update(**son)
    return {'ids': ids}, 200

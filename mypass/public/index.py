import logging
from datetime import datetime

import flask
from flask import Blueprint, render_template, request

IndexTemplate = Blueprint('index', __name__, template_folder='templates')


@IndexTemplate.route('/', methods=['GET'])
@IndexTemplate.route('/index', methods=['GET'])
def index():
    return render_template('index.html', utc_dt=datetime.utcnow())


@IndexTemplate.route('/app/config', methods=['POST'])
def config():
    # TODO: should we restart the server somehow?
    values = request.values
    port = int(values['port'])
    logging.getLogger().debug(f'Port: {port}')
    return flask.redirect('/index')

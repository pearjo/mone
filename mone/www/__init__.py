# Copyright (C) 2020  Joe Pearson
#
# This file is part of Mone.
#
# Mone is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mone is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import logging
import logging.config

from connexion.decorators.uri_parsing import OpenAPIURIParser
import coloredlogs
import connexion

from mone.www import db


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    logging.config.dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'DEBUG',
            'handlers': ['wsgi']
        }
    })

    fmt = '%(levelname)s %(module)s.%(funcName)s: %(message)s'
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='DEBUG', logger=logger, fmt=fmt)

    app = connexion.FlaskApp(__name__,
                             options={'uri_parsing_class': OpenAPIURIParser})
    app.add_api('api/openapi.yaml',
                resolver=connexion.RestyResolver('mone.www.api'),
                validate_responses=True)

    flask_app = app.app
    flask_app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(flask_app.instance_path, 'mone.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        flask_app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        flask_app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(flask_app.instance_path)
    except OSError:
        pass

    # register the database commands
    db.init_app(flask_app)

    return flask_app

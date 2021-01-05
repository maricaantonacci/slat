# Copyright (c) Istituto Nazionale di Fisica Nucleare (INFN). 2019-2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flaat import Flaat

from app.auth import indigoiam
from app.auth import egicheckin
from .models import migrate, alembic, db, OAuth, User, Role, Group, login_manager
import logging
from flask_dance.consumer import oauth_authorized

app = Flask(__name__, instance_relative_config=True)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = "30bb7cf2-1fef-4d26-83f0-8096b6dcc7a3"
app.config.from_object('config.default')
app.config.from_json('config.json')

with app.app_context():
    iam_blueprint = indigoiam.create_blueprint()
    app.register_blueprint(iam_blueprint, url_prefix="/login")

    # create/login local user on successful OAuth login
    @oauth_authorized.connect_via(iam_blueprint)
    def iam_logged_in(blueprint, token):
        return indigoiam.auth_blueprint_login(blueprint, token)


    if app.config.get('EGI_AAI_CLIENT_ID') and app.config.get('EGI_AAI_CLIENT_SECRET'):
        egicheckin_blueprint = egicheckin.create_blueprint()
        app.register_blueprint(egicheckin_blueprint, url_prefix="/login")


        @oauth_authorized.connect_via(egicheckin_blueprint)
        def egicheckin_logged_in(blueprint, token):
            return egicheckin.auth_blueprint_login(blueprint, token)

        # Inject the variable inject_egi_aai_enabled automatically into the context of templates
        @app.context_processor
        def inject_egi_aai_enabled():
            return dict(is_egi_aai_enabled=True)

flaat = Flaat()
flaat.set_web_framework('flask')
flaat.set_trusted_OP_list([idp['iss'] for idp in app.config.get('TRUSTED_OIDC_IDP_LIST')])
flaat.set_timeout(20)
flaat.set_client_connect_timeout(20)
flaat.set_iss_config_timeout(20)


db.init_app(app)
migrate.init_app(app, db)
alembic.init_app(app, run_mkdir=False)

login_manager.init_app(app)


# logging
loglevel = app.config.get("LOG_LEVEL") if app.config.get("LOG_LEVEL") else "INFO"
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

logging.basicConfig(level=numeric_level)

from app import models
from app import routes

from app.rest.routes import rest_bp
app.register_blueprint(rest_bp, url_prefix="/rest")

from app.sla.routes import sla_bp
app.register_blueprint(sla_bp, url_prefix="/sla")


from app.group.routes import group_bp
app.register_blueprint(group_bp, url_prefix="/group")









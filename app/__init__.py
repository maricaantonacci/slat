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

from flask import Flask, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_dance import OAuth2ConsumerBlueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import login_user, current_user
from flaat import Flaat
from .models import migrate, alembic, db, OAuth, User, Role, login_manager
import logging
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound



app = Flask(__name__, instance_relative_config=True)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = "30bb7cf2-1fef-4d26-83f0-8096b6dcc7a3"
app.config.from_object('config.default')
app.config.from_json('config.json')


iam_base_url = app.config['IAM_BASE_URL']
iam_token_url = iam_base_url + '/token'
iam_refresh_url = iam_base_url + '/token'
iam_authorization_url = iam_base_url + '/authorize'

iam_blueprint = OAuth2ConsumerBlueprint(
    "iam", __name__,
    client_id=app.config['IAM_CLIENT_ID'],
    client_secret=app.config['IAM_CLIENT_SECRET'],
    base_url=iam_base_url,
    token_url=iam_token_url,
    auto_refresh_url=iam_refresh_url,
    authorization_url=iam_authorization_url,
    redirect_to='sla_bp.home',
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
)
app.register_blueprint(iam_blueprint, url_prefix="/login")

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


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(iam_blueprint)
def iam_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with IAM.", category="error")
        return False

    resp = blueprint.session.get("/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        return False

    iam_info = resp.json()
    iam_user_id = str(iam_info["sub"])
    iam_user_groups = str(iam_info["groups"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=iam_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=iam_user_id,
            token=token,
        )

    if oauth.user:
        # If this OAuth token already has an associated local account,
        # log in that local user account.
        # Note that if we just created this OAuth token, then it can't
        # have an associated local account yet.
        login_user(oauth.user)
        flash("Successfully signed in.")

    else:
        # If this OAuth token doesn't have an associated local account,
        # create a new local user account for this user. We can log
        # in that account as well, while we're at it.
        user = User(
            # Remember that `email` can be None, if the user declines
            # to publish their email address on GitHub!
            email=iam_info["email"],
            name=iam_info["name"],
        )
        # check user role
        if app.config.get("SLAT_ADMIN_GROUP") in iam_user_groups:
            user.roles = [Role(name="Admin")]
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in.")

    # Since we're manually creating the OAuth model in the database,
    # we should return False so that Flask-Dance knows that
    # it doesn't have to do it. If we don't return False, the OAuth token
    # could be saved twice, or Flask-Dance could throw an error when
    # trying to incorrectly save it for us.
    return False



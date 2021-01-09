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
from flaat import tokentools
from flask import flash, current_app as app
from flask_dance import OAuth2ConsumerBlueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from app.models import db, OAuth, User, Role, Group
from flask_login import current_user, login_user
import re

def create_blueprint():
    egicheckin_base_url = app.config['EGI_AAI_BASE_URL']
    egicheckin_token_url = egicheckin_base_url + '/token'
    egicheckin_refresh_url = egicheckin_base_url + '/token'
    egicheckin_authorization_url = egicheckin_base_url + '/authorize'

    return OAuth2ConsumerBlueprint(
        "egiaai", __name__,
        client_id=app.config['EGI_AAI_CLIENT_ID'],
        client_secret=app.config['EGI_AAI_CLIENT_SECRET'],
        base_url=egicheckin_base_url,
        token_url=egicheckin_token_url,
        auto_refresh_url=egicheckin_refresh_url,
        authorization_url=egicheckin_authorization_url,
        redirect_to='provider_bp.list',
        storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
    )

def get_user_roles(info):
    roles = []

    if 'eduperson_entitlement' in info:
        memberships = info['eduperson_entitlement']
        pattern = 'urn:mace:egi.eu:group:(.*):role=vm_operator#aai.egi.eu'
        groups = []
        for m in memberships:
            match = re.search(pattern, m)
            if match:
                group = Group.query.filter_by(name=match.group(1)).first()
                if not group:
                    group = Group(name=match.group(1))
                roles.append(Role(name="Member", group=group))
    return roles


def auth_blueprint_login(blueprint, token):
    if not token:
        flash("Failed to log in with EGI Checkin.", category="error")
        return False

    resp = blueprint.session.get('/oidc/userinfo')
    jwt = tokentools.get_accesstoken_info(token['access_token'])

    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        return False

    user_info = resp.json()
    user_id = jwt['body']['sub']
    issuer = jwt['body']['iss']

    # Find this OAuth token in the database, or create it
    oauth = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=user_id,
    ).first()

    if not oauth:
        oauth = OAuth(provider=blueprint.name,
                      provider_user_id=user_id,
                      token=token,
                      issuer=issuer)
    else:
        oauth.token = token #store token

    if oauth.user:
        oauth.user.roles = get_user_roles(user_info) # update user roles
        db.session.commit()
        login_user(oauth.user)
        flash("Successfully signed in.")

    else:
        user = User(email=user_info["email"],
                    name=user_info["name"],
                    roles=get_user_roles(user_info))
        oauth.user = user
        db.session.add_all([oauth, user])
        db.session.commit()
        login_user(user)
        flash("Successfully signed in.")

    return False


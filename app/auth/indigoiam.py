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
from flask import current_app as app, flash
from flask_dance import OAuth2ConsumerBlueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from app.models import db, OAuth, User, Role, Group
from flask_login import current_user, login_user

def create_blueprint():
    iam_base_url = app.config['IAM_BASE_URL']
    iam_token_url = iam_base_url + '/token'
    iam_refresh_url = iam_base_url + '/token'
    iam_authorization_url = iam_base_url + '/authorize'

    global admin_group
    admin_group = app.config.get("SLAT_ADMIN_GROUP")

    return OAuth2ConsumerBlueprint(
    "iam", __name__,
    client_id=app.config['IAM_CLIENT_ID'],
    client_secret=app.config['IAM_CLIENT_SECRET'],
    scope=['openid', 'profile', 'email', 'offline_access'],
    base_url=iam_base_url,
    token_url=iam_token_url,
    auto_refresh_url=iam_refresh_url,
    authorization_url=iam_authorization_url,
    redirect_to='sla_bp.home',
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
  )

def get_user_roles(info):
    roles = []
    if "groups" in info:
        groups = info['groups']

        if admin_group in groups:
            roles.append(Role(name="Admin"))
        for group_name in groups:
            group = Group.query.filter_by(name=group_name).first()
            if not group:
                group = Group(name=group_name)
            roles.append(Role(name="Member", group=group))

    return roles


def auth_blueprint_login(blueprint, token):
    if not token:
        flash("Failed to log in with IAM.", category="error")
        return False

    resp = blueprint.session.get('/userinfo')
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






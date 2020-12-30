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

from datetime import datetime, date
import uuid, enum

from sqlalchemy.orm.collections import attribute_mapped_collection
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_alembic import Alembic
from flask_login import UserMixin
from flask_login import LoginManager


# initialize SQLAlchemy
db: SQLAlchemy = SQLAlchemy()

# initialize Migrate
migrate: Migrate = Migrate()

# Intialize Alembic
alembic: Alembic = Alembic()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), nullable=False)
    roles = db.relationship('Role', secondary='user_roles')

    def has_role(self, role):

        for item in self.roles:
            if item.name == role:
                return True
        return False

    def has_roles(self, *requirements):
        """ Return True if the user has all of the specified roles. Return False otherwise.
            has_roles() accepts a list of requirements:
                has_role(requirement1, requirement2, requirement3).
            Each requirement is either a role_name, or a tuple_of_role_names.
                role_name example:   'manager'
                tuple_of_role_names: ('funny', 'witty', 'hilarious')
            A role_name-requirement is accepted when the user has this role.
            A tuple_of_role_names-requirement is accepted when the user has ONE of these roles.
            has_roles() returns true if ALL of the requirements have been accepted.
            For example:
                has_roles('a', ('b', 'c'), d)
            Translates to:
                User has role 'a' AND (role 'b' OR role 'c') AND role 'd'"""

        # Translates a list of role objects to a list of role_names
        role_names = [role.name for role in self.roles]

        # has_role() accepts a list of requirements
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                # this is a tuple_of_role_names requirement
                tuple_of_role_names = requirement
                authorized = False
                for role_name in tuple_of_role_names:
                    if role_name in role_names:
                        # tuple_of_role_names requirement was met: break out of loop
                        authorized = True
                        break
                if not authorized:
                    return False                    # tuple_of_role_names requirement failed: return False
            else:
                # this is a role_name requirement
                role_name = requirement
                # the user must have this role
                if not role_name in role_names:
                    return False                    # role_name requirement failed: return False

        # All requirements have been met: return True
        return True

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class OAuth(OAuthConsumerMixin, db.Model):
    __table_args__ = (
        db.UniqueConstraint("provider", "provider_user_id"),
    )
    provider_user_id = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(
        User,
        # This `backref` thing sets up an `oauth` property on the User model,
        # which is a dictionary of OAuth models associated with that user,
        # where the dictionary key is the OAuth provider name.
        backref=db.backref(
            "oauth",
            collection_class=attribute_mapped_collection("provider"),
            cascade="all, delete-orphan",
        ),
    )



"""GUID helper for backend-agnostic UUID column type"""
from app.utils.sqlalchemy_helpers import GUID, IntEnum
db.GUID = GUID

class Group(db.Model):
    name = db.Column(db.String(64), primary_key=True, nullable=False)
    description = db.Column(db.String(64), nullable=True)
    slas = db.relationship('Sla', backref='customer_slas', lazy=True)

    def __init__(self, *args):
        super(db.Model, self).__init__(*args)

    def __repr__(self):
        return '<Group {}>'.format(self.name)


class SlaStatusTypes(enum.IntEnum):
    draft = 1
    sent = 2
    accepted = 3
    expired = 4


class Sla(db.Model):
    __table_args__ = (
        db.UniqueConstraint("type", "customer"),
    )
    id = db.Column(db.GUID(), default=uuid.uuid4, primary_key=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    start_date = db.Column(db.Date, default=date(2020, 11, 16), nullable=False)
    end_date = db.Column(db.Date, default=date(2020, 11, 16), nullable=False)
    customer = db.Column(db.String(64), db.ForeignKey('group.name'), nullable=False)
    type = db.Column(db.String(64), nullable=False) # service_id
    provider = db.Column(db.String(64), nullable=False)
    vcpu_cores = db.Column(db.Integer, default=0)
    ram_gb = db.Column(db.Integer, default=0)
    public_ips = db.Column(db.Integer, default=0)
    storage_gb = db.Column(db.Integer, default=0)
    num_instances = db.Column(db.Integer, default=0)
    status = db.Column(IntEnum(SlaStatusTypes), default=SlaStatusTypes.draft)

    def __init__(self, *args):
        super(db.Model, self).__init__(*args)

    def __repr__(self):
        return '<Sla {} with site/service {}/{}>'.format(self.id, self.provider, self.type)


login_manager = LoginManager()
login_manager.login_view = "iam.login"
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)









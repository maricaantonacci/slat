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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)




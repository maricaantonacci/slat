# Copyright (c) Istituto Nazionale di Fisica Nucleare (INFN). 2020-2021
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

from flask import Blueprint, render_template, request
from flask_login import login_required
from app import app, cmdb


cmdb_client = cmdb.Client(app.config.get("CMDB_URL"), cacert=app.config.get("CMDB_CA_CERT"))


provider_bp = Blueprint('provider_bp', __name__,
                           template_folder='templates',
                           static_folder='static')


@provider_bp.route('/list', methods=["GET"])
@login_required
def list():

    providers = cmdb_client.get_providers(detailed=True)
    return render_template('providers.html', providers=providers)

@provider_bp.route('/services', methods=["GET"])
@login_required
def get_services():
    id = request.args.get('provider_id', None)
    services = cmdb_client.get_services(provider_id=id, detailed=True)
    filtered_services = [s for s in services if s['doc']['data']['service_type'] != 'eu.indigo-datacloud.mesos']
    return render_template('services.html', title="{} Services".format(id), services=filtered_services)
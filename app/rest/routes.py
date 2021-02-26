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
from flaat import tokentools, issuertools
from app import app, flaat, decoders, models, db, cmdb
from flask import Blueprint, request, render_template, make_response

rest_bp = Blueprint('rest_bp', __name__,
                           template_folder='templates',
                           static_folder='static')


cmdb_client = cmdb.Client(app.config.get("CMDB_URL"), cacert=app.config.get("CMDB_CA_CERT"))

class TokenDecoder:
    def get_groups(self, request):
        access_token = tokentools.get_access_token_from_request(request)
        issuer = issuertools.find_issuer_config_in_at(access_token)
        #info = flaat.get_info_thats_in_at(access_token)
        info = flaat.get_info_from_userinfo_endpoints(access_token)
        iss = issuer['issuer']

        idp = next(filter(lambda x: x['iss']==iss, app.config.get('TRUSTED_OIDC_IDP_LIST')))

        if 'client_id' in idp and 'client_secret' in idp:
            flaat.set_client_id(idp['client_id'])
            flaat.set_client_secret(idp['client_secret'])
            info = flaat.get_info_from_introspection_endpoints(access_token)
        decoder = decoders.factory.get_decoder(idp['type'])
        return decoder.get_groups(info)

@rest_bp.route("/slam/preferences/<group>", methods=["GET"])
@flaat.login_required()
def get_by_group(group=None):

    slas = []
    if group:
      slas = db.session.query(models.Sla).filter(models.Sla.customer == group).all()

    app.logger.debug("Computed slas for group {}: {}".format(group, slas))

    response = make_response(render_template('slas.json', slas=slas, customer=group))
    response.headers['Content-Type'] = 'application/json'
    return response

@rest_bp.route("/slam/preferences/<group>/<subgroup>", methods=["GET"])
@flaat.login_required()
def get_by_subgroup(group, subgroup=None):
    if subgroup:
        group = group + '/' + subgroup
    return get_by_group(group)


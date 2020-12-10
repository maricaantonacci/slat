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
from sqlalchemy.exc import IntegrityError
from app import app, flaat, decoders, models, db, cmdb
from flask import Blueprint, request, render_template, make_response

rest_bp = Blueprint('rest_bp', __name__,
                           template_folder='templates',
                           static_folder='static')


cmdb_client = cmdb.Client(app.config.get("CMDB_URL"))

class TokenDecoder:
    def get_group(self, request):
        access_token = tokentools.get_access_token_from_request(request)
        info = flaat.get_info_thats_in_at(access_token)
        iss = info['body']['iss']
        type = [ k['type'] for k in app.config.get('TRUSTED_OIDC_IDP_LIST') if k.get('iss')==iss]

        decoder = decoders.factory.get_decoder(type[0])
        return decoder.get_group(info)


# @rest_bp.route("/create", methods=["POST"])
# @flaat.login_required()
# def create():
#     if not request.json or not 'service_id' in request.json:
#         return "service_id field is mandatory", 400
#     isla = request.json
#
#     td = TokenDecoder()
#     isla['user_group'] = td.get_group(request)
#
#     service = isla['service_id']
#     if not cmdb_client.is_valid_service(service):
#         return "Service with id {} not found".format(service), 404
#     else:
#         new_sla = models.Sla(**isla)
#         try:
#             db.session.add(new_sla)
#             db.session.commit()
#         except IntegrityError as e:
#             return str(e.args[0]), 400
#         return "", 204


@rest_bp.route("/slam/preferences/<legacy_customer>", methods=["GET"])
@flaat.login_required()
def get(legacy_customer=None):

    td = TokenDecoder()
    group = td.get_group(request)

    slas = db.session.query(models.Sla).filter(models.Sla.customer == group).all()
    app.logger.debug("Requesting slas for group {}: {}".format(group, slas))

    response = make_response(render_template('slas.json', slas=slas, customer=legacy_customer))
    response.headers['Content-Type'] = 'application/json'
    return response



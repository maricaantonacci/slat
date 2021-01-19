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

from flask import Blueprint, render_template
from flask_login import login_required
from app import app, cmdb, db, forms, models
from app.utils.decorators import *

sla_bp = Blueprint('sla_bp', __name__,
                           template_folder='templates',
                           static_folder='static')


cmdb_client = cmdb.Client(app.config.get("CMDB_URL"), cacert=app.config.get("CMDB_CA_CERT"))



@sla_bp.route('/list', methods=["GET"])
@login_required
def list():

    if current_user.is_admin():
        slas = models.Sla.query.order_by(models.Sla.customer).all()
    else:
        slas = []
        for group in current_user.groups:
            slas.extend(group.slas)

    return render_template('slalist.html', title='Service Level Agreements', slas=slas)

@sla_bp.route('/view', methods=["GET"])
@roles_required(('Admin','SlaManager'))
def view():
    sla_id = request.args.get('sla_id', None)
    if sla_id:
        sla = models.Sla.query.filter(models.Sla.id == sla_id).first()
        return render_template('sladetails.html', title="SLA details", sla=sla)
    else:
        return "not found"


@sla_bp.route('/edit/<id>', methods=['GET', 'POST'])
@roles_required('Admin')
def edit(id=None):

    sla = models.Sla.query.filter(models.Sla.id == id).first()

    form = forms.SlaForm(obj=sla)

    if form.validate_on_submit():
        # save to db
        try:
            form.populate_obj(sla)
            db.session.add(sla)
            db.session.commit()
            flash('You have successfully updated the SLA!', 'success')
        except Exception as e:
            flash("Error updating the SLA: {}".format(str(e)), 'danger')

        return redirect(url_for('sla_bp.list'))

    # disable fields that cannot be changed
    form.type.choices = [(sla.type, sla.type, dict(disabled='disabled'))]
    form.type.render_kw = {'disabled': 'disabled'}
    form.customer.choices = [(sla.customer, sla.customer, dict(disabled='disabled'))]
    form.customer.render_kw = {'disabled': 'disabled'}

    return render_template('slaform.html', title='Update SLA', form=form)


@sla_bp.route('/create', methods=["GET", "POST"])
@roles_required(('Admin','SlaManager'))
def create():
    form = forms.SlaForm()

    if form.validate_on_submit():
        # save to db
        try:
            new_sla = models.Sla()

            form.populate_obj(new_sla)
            provider = cmdb_client.get_service(new_sla.type)['provider_id']
            new_sla.provider = provider
            db.session.add(new_sla)
            db.session.commit()
            flash('You have successfully saved the SLA!', 'success')
        except Exception as e:
            flash("Error saving the draft SLA: {}".format(str(e)), 'danger')

        return redirect(url_for('sla_bp.list'))


    groups = models.Group.query.all()
    if not groups:
        flash('Cannot retrieve customer information. Configure group before', 'danger')
    form.customer.choices = [ (g.name, g.name, dict(data_subtext=g.description)) for g in groups]

    service_id = request.args.get('service_id', None)
    if service_id:
        form.type.data = service_id
        form.type.choices = [(service_id, service_id, dict())]
    else:
        services = cmdb_client.get_services(detailed=True)
        form.type.choices = [(s['id'], s['id'], dict(data_subtext="site: {}, service type: {}, service endpoint: {}".format(s['doc']['data']['sitename'], s['doc']['data']['service_type'], s['doc']['data']['endpoint']))) for s in services]
    return render_template('slaform.html', title='Create SLA', form=form)


@sla_bp.route('/delete', methods=["GET"])
@roles_required('Admin')
def delete():
    id = request.args.get('id', None)

    try:
        sla = models.Sla.query.get(id)
        db.session.delete(sla)
        db.session.commit()

        flash('You have successfully deleted the SLA {}'.format(id), 'success')

    except Exception as e:
        app.logger.error("Error deleting SLA {}: {}".format(id, str(e)))
        flash("Error deleting SLA {}: {}".format(id, str(e)), 'warning')

    return redirect(url_for('sla_bp.list'))


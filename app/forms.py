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

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from wtforms.fields.html5 import DateField
from wtforms.widgets import html_params, Select
from markupsafe import Markup

class AttribSelect(Select):
    """
    Renders a select field that supports options including additional html params.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected, html_attribs)`.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected, html_attribs in field.iter_choices():
            html.append(self.render_option(val, label, selected, **html_attribs))
        html.append('</select>')
        return Markup(''.join(html))

class AttribSelectField(SelectField):
    widget = AttribSelect()

    def iter_choices(self):
        for value, label, render_args in self.choices:
            yield (value, label, self.coerce(value) == self.data, render_args)

    def pre_validate(self, form):
         if self.choices:
             for v, _, _ in self.choices:
                 if self.data == v:
                     break
             else:
                 raise ValueError(self.gettext('Is Not a valid choice'))

class SlaForm(FlaskForm):
    type = AttribSelectField('Service', validators=[DataRequired()], coerce=str, validate_choice=False)
    customer = AttribSelectField('Customer Group', validators=[DataRequired()], coerce=str, validate_choice=False)
    start_date = DateField('Effective from', validators=[DataRequired()])
    end_date = DateField('Expiration Date', validators=[DataRequired()])
    num_instances = IntegerField('Number of Virtual Machines (if applicable)', default=0)
    vcpu_cores = IntegerField('Total number of vCPUs (if applicable)', default=0)
    ram_gb = IntegerField('Total amount of RAM in GB (if applicable)', default=0)
    public_ips = IntegerField('Total number of Public IPs (if applicable)', default=0)
    storage_gb = IntegerField('Total amount of storage in GB (if applicable)', default=0)
    submit = SubmitField('Save')

    def validate_end_date(form, field):
        if field.data <= form.start_date.data:
            raise ValidationError("End date must be later than start date.")



class GroupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')

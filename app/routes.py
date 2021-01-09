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

from flask import render_template, flash, redirect, url_for
from app import app
from flask_login import login_required, logout_user


@app.route('/')
def login():
    return render_template('home.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out", 'success')
    return redirect(url_for("login"))



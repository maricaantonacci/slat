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
from functools import wraps
from flask import current_app, flash, request, redirect, url_for
from flask_login import current_user

def roles_accepted(*role_names):
    """| This decorator ensures that the current user is logged in,
    | and has *at least one* of the specified roles (OR operation).
    Example::
        @route('/edit_article')
        @roles_accepted('Writer', 'Editor')
        def edit_article():  # User must be 'Writer' OR 'Editor'
            ...
    | Calls unauthenticated_view() when the user is not logged in
        or when user has not confirmed their email address.
    | Calls unauthorized_view() when the user does not have the required roles.
    | Calls the decorated view otherwise.
    """
    # convert the list to a list containing that list.
    # Because roles_required(a, b) requires A AND B
    # while roles_required([a, b]) requires A OR B
    def wrapper(view_function):

        @wraps(view_function)    # Tells debuggers that is is a function wrapper
        def decorator(*args, **kwargs):
            login_manager = current_app.login_manager

            # User must be logged in with a confirmed email address
            allowed = current_user.is_authenticated
            if not allowed:
                # Redirect to unauthenticated page
                return redirect(url_for("login"))

            # User must have the required roles
            # NB: roles_required would call has_roles(*role_names): ('A', 'B') --> ('A', 'B')
            # But: roles_accepted must call has_roles(role_names):  ('A', 'B') --< (('A', 'B'),)
            if not current_user.has_roles(role_names):
                # Redirect to the unauthorized page
                flash("Sorry, You are not authorized for this action.", 'warning')
                if request.referrer:
                    return redirect(request.referrer)
                else:
                    redirect(url_for("login"))

            # It's OK to call the view
            return view_function(*args, **kwargs)

        return decorator

    return wrapper

def roles_required(*role_names):
    """| This decorator ensures that the current user is logged in,
    | and has *all* of the specified roles (AND operation).
    Example::
        @route('/escape')
        @roles_required('Special', 'Agent')
        def escape_capture():  # User must be 'Special' AND 'Agent'
            ...
    | Calls unauthenticated_view() when the user is not logged in
        or when user has not confirmed their email address.
    | Calls unauthorized_view() when the user does not have the required roles.
    | Calls the decorated view otherwise.
    """
    def wrapper(view_function):

        @wraps(view_function)    # Tells debuggers that is is a function wrapper
        def decorator(*args, **kwargs):

            login_manager = current_app.login_manager

            # User must be logged in with a confirmed email address
            allowed = current_user.is_authenticated
            if not allowed:
                # Redirect to unauthenticated page
                return redirect(url_for("login"))

            # User must have the required roles
            if not current_user.has_roles(*role_names):
                # Redirect to the unauthorized page
                flash("Sorry, You are not authorized for this action.", 'warning')
                if request.referrer:
                    return redirect(request.referrer)
                else:
                    return redirect(url_for("login"))

            # It's OK to call the view
            return view_function(*args, **kwargs)

        return decorator

    return wrapper



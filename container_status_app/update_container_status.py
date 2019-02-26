# Flask
from flask import render_template, request
from flask.views import MethodView

# USCC
from container_status_app.forms import ContainerForm
from common.common import Common

# Misc
import json
import os


class UpdateContainer(MethodView):
    def __init__(self):

        self.container_status_dict = None

    def get(self):
        """

        :return: Renders the html page with all substituted content needed.
        """
        if request.cookies.get('access_token_cookie') is None:
            self.redirect_to_uscc_login()
            return self.login_redirect_response

        form = ContainerForm()

        return render_template('container_status/update_container_status.html', form=form)

    def post(self):
        """
        """

        if 'logout_btn' in request.form:
            self.delete()
            return self.login_redirect_response

        if request.cookies.get('access_token_cookie') is None:
            self.redirect_to_uscc_login()
            return self.login_redirect_response

        form = ContainerForm()

        if request.form.get('open_status') == 'on':
            self.open_container_status()
        else:
            if form.validate_on_submit():
                with open(os.environ.get('container_status_path')) as csrfh:
                    status_file_dict = json.load(csrfh)

                update_container_dict = status_file_dict.get(request.form.get('container_name'))
                update_container_dict['status'] = 'not open'
                update_container_dict.get('time_frame')['start_date'] = request.form.get('start_date')
                update_container_dict.get('time_frame')['end_date'] = request.form.get('end_date')
                update_container_dict.get('poc')['name'] = request.form.get('poc_name')
                update_container_dict.get('poc')['email'] = request.form.get('poc_email')
                status_file_dict[request.form.get('container_name')] = update_container_dict

                with open(os.environ.get('container_status_path'),mode='w') as cswfh:
                    json.dump(status_file_dict, cswfh)
            else:
                if len(form.errors) != 0:
                    for form_field, error_message_text in form.errors.items():
                        Common.create_flash_message(message=form_field + ':' + error_message_text[0])

        return render_template('container_status/update_container_status.html', form=form)

    def open_container_status(self):
        """
        If the "Set to open status" checkbox is checked for a container name, clears the dictionary information for the
        container_name and sets the "status" key to "open".

        :return:
        """

        with open(os.environ.get('container_status_path'), 'r') as csrfh:
            status_file_dict = json.load(csrfh)

        update_container_dict = status_file_dict.get(request.form.get('container_name'))
        for k, v in update_container_dict.items():
            if k == 'status':
                update_container_dict[k] = 'open'
            else:
                for sub_dict_key in update_container_dict.get(k).keys():
                    update_container_dict.get(k)[sub_dict_key] = ""

        status_file_dict[request.form.get('container_name')] = update_container_dict

        with open(os.environ.get('container_status_path'),mode='w') as cswfh:
            json.dump(status_file_dict, cswfh)

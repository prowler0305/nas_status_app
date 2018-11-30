# Flask
from flask import render_template, redirect, request, url_for, make_response
from flask_jwt_extended import set_access_cookies, set_refresh_cookies
from flask.views import MethodView

# USCC
from uscc_api import api
from uscc_api import uscc_eng_app
from uscc_apps.uscc_login.login_form import LoginForm
from common.common import Common
from resources.auth import Authenticate

# Misc
import requests
import json
import os


class Login(MethodView):
    def __init__(self):
        self.headers = {'content-type': 'application/json'}
        self.client_referrer = None
        self.auth_data = dict(username=None, password=None)

    def get(self):
        """

        :return:
        """

        form = LoginForm()

        return render_template('login.html', form=form)

    def post(self):
        """

        """

        form = LoginForm()
        if form.validate_on_submit():
            self.auth_data['username'] = request.form['username']
            self.auth_data['password'] = request.form['password']
            self.client_referrer = request.args.get('referrer')
            auth_response = requests.post(api.url_for(Authenticate, _external=True), data=json.dumps(self.auth_data),
                                          headers=self.headers)
            uscc_eng_app.logger.info(auth_response.text)
            auth_response_text_dict = json.loads(auth_response.text)
            if auth_response.status_code == requests.codes.ok:
                login_data_dict = json.loads(auth_response.text)
                if self.client_referrer is not None:
                    response = redirect(self.client_referrer)
                    response.set_cookie('username', value=self.auth_data.get('username'), httponly=True)
                    response.set_cookie('automations', value=json.dumps(login_data_dict.get('automations')),
                                        max_age=uscc_eng_app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))
                    set_access_cookies(response, login_data_dict.get('art').get('access_token'),
                                       max_age=uscc_eng_app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))
                    set_refresh_cookies(response, login_data_dict.get('art').get('refresh_token'),
                                        max_age=uscc_eng_app.config.get('JWT_REFRESH_TOKEN_EXPIRES'))
                    return response
                else:
                    response = make_response(render_template('login_welcome.html', username=self.auth_data.get('username')))
                    response.set_cookie('automations', value=json.dumps(login_data_dict.get('automations')),
                                        max_age=uscc_eng_app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))
                    response.set_cookie('username', value=self.auth_data.get('username'), httponly=True)
                    set_access_cookies(response, login_data_dict.get('art').get('access_token'),
                                       max_age=uscc_eng_app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))
                    set_refresh_cookies(response, login_data_dict.get('art').get('refresh_token'),
                                        max_age=uscc_eng_app.config.get('JWT_REFRESH_TOKEN_EXPIRES'))
                    return response
            elif auth_response.status_code == requests.codes.unauthorized:
                uscc_eng_app.logger.info('Invalid login occurred. IP=%s:Username=%s'
                                         % (request.remote_addr, self.auth_data.get('username')))
                bad_cred_mmsg = 'Username and/or password is invalid. Please reenter.'
                Common.create_flash_message(bad_cred_mmsg)
            else:
                if auth_response_text_dict.get('message') == 'api_cred_path invalid':

                    auth_response_cred_path_msg = '%s:%s. Configuration error please contact Core Automation Team.' \
                                                  % (auth_response.status_code, auth_response.reason)
                    # auth_response_cred_path_msg = auth_response_text_dict.get('message') + '. Path set as %s.' \
                    #                               % os.environ.get('api_cred_path')
                    # INFO: Temporary code. Once LDAP integration put in place this is not needed.
                    api_cred_dir_found_list = Common.find_file_in_project('api_cred')
                    if len(api_cred_dir_found_list) > 0:
                        uscc_eng_app.logger.critical(auth_response_text_dict.get('message') +
                                                       '. Path set as %s. Did you mean to set path as %s?'
                                                       % (os.environ.get('api_cred_path'), api_cred_dir_found_list[0]))

                    Common.create_flash_message(auth_response_cred_path_msg)
                else:
                    Common.create_flash_message("%s:%s Please Contact Core Automation Team"
                                                % (auth_response.status_code, auth_response.reason))
        else:
            if len(form.errors) != 0:
                for error_message_text in form.errors.values():
                    Common.create_flash_message(error_message_text[0])

        return render_template('login.html', form=form)

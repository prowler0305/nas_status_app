# Flask
from flask import render_template, redirect, request, url_for, abort, make_response
from flask.views import MethodView

# USCC
from resources.logout import Logout
from uscc_api import api, uscc_eng_app
from resources.imsi import Imsi
from uscc_apps.imsi_tracking.forms import ImsiForm
from common.common import Common

# Misc
import requests
import json
import os


class ContainerStatus(MethodView):
    def __init__(self):

        # self.imsi_header = {'Authorization': None}
        # self.imsi_tracking_dict = dict(imsi=None,
        #                                userid=None,
        #                                email=None
        #                                )
        # self.imsi_list_get_resp = None
        self.login_redirect_response = None
        self.container_status_dict = None

    def get(self):
        """

        :return: Renders the html page with all substituted content needed.
        """

        with open(os.environ.get('container_status_path')) as csfh:
            self.container_status_dict = json.load(csfh)

        if request.url_rule.rule == '/nas_status':
            if 'nas_production' in self.container_status_dict:
                return render_template('container_status/nas_prod_status.html', cs=self.container_status_dict.get('nas_production'))
            else:
                return render_template('container_status/nas_prod_status.html')

        return render_template('container_status/container_status.html', cs=self.container_status_dict)

    def post(self):
        """
        Receives control after the users clicks submit on the web page via the HTTP POST request done on the HTML form
        action method.

        The string of imsis is extracted from the form and passed on to either a HTTP POST or DELETE request to the
        USCC ENG REST API. Which request to perform is determined by interrogating the Add or Delete radio button to
        determine which value the radio button contains.

        :return: If the form validates correctly then a redirect to the same page is done to reload the page with the
        updated imsi list. If not then the web page is loaded without the imsi list so that any error messages can be
        displayed.
        """

        if 'logout_btn' in request.form:
            self.delete()
            return self.login_redirect_response

        if request.cookies.get('access_token_cookie') is None:
            self.redirect_to_uscc_login()
            return self.login_redirect_response
        else:
            # INFO: needed if JWT_TOKEN_LOCATION is set to headers as opposed to in cookies
            # self.imsi_header['Authorization'] = 'JWT {}'.format(request.cookies.get('access_token_cookie'))
            # INFO: With JWT in cookies set the CSRF token is still expected to be in the header for POST to succeed
            self.imsi_header['X-CSRF-TOKEN'] = request.cookies.get('csrf_access_token')
            self.imsi_header['content_type'] = 'application/json'

        form = ImsiForm()
        if form.validate_on_submit():
            if request.form.get('imsis') == "" and request.form.get('email') == "":
                Common.create_flash_message("Please fill in either the Imsi or Email fields.")
            else:
                self.imsi_tracking_dict['imsi'] = request.form.get('imsis')
                self.imsi_tracking_dict['email'] = request.form.get('email')
                self.imsi_tracking_dict['userid'] = request.cookies.get('username')
                if self.imsi_tracking_dict.get('email') != '' and '@' not in self.imsi_tracking_dict.get('email'):
                    Common.create_flash_message('Email entered is not a valid email address', 'error')
                    return render_template('imsi_tracking/imsi_tracking.html', form=form)
                if request.form['add_delete_radio'] == 'A':
                    imsi_post_resp = \
                        requests.post(api.url_for(Imsi, _external=True), data=json.dumps(self.imsi_tracking_dict),
                                      headers=self.imsi_header,
                                      cookies={'access_token_cookie': request.cookies.get('access_token_cookie')})

                    if imsi_post_resp.status_code == requests.codes.unauthorized:
                        self.redirect_to_uscc_login()
                        return self.login_redirect_response
                    else:
                        if imsi_post_resp.json().get('msg') is not None:
                            Common.create_flash_message("%s. Please Contact Core Automation Team." % imsi_post_resp.json().get('msg'))
                        else:
                            Common.create_flash_message(imsi_post_resp.json().get('imsi_msg'))
                    return redirect(url_for('imsi_tracking'))
                else:
                    self.delete()
                    return redirect(url_for('imsi_tracking'))
        else:
            if len(form.errors) != 0:
                for error_message_text in form.errors.values():
                    Common.create_flash_message(error_message_text[0])

        return render_template('imsi_tracking/imsi_tracking.html', form=form)

    def delete(self):
        """
        Called by the above post() method if the radio button value is 'D' in which an HTTP DELETE request is made to
        the USCC ENG REST API to delete the imsi(s) from the tracking file.

        :return: True - if the delete API request is successful with a successful message
                False - if the delete API request is unsuccessful with an error message derived from the API HTTP
                        Response object.
        """

        if 'logout_btn' in request.form:
            self.imsi_header['X-CSRF-TOKEN'] = request.cookies.get('csrf_access_token')
            imsi_logout_resp = requests.delete(api.url_for(Logout, _external=True), headers=self.imsi_header,
                                               cookies={'access_token_cookie': request.cookies.get('access_token_cookie')})
            if imsi_logout_resp.status_code == requests.codes.ok:
                self.redirect_to_uscc_login()


        else:
            imsi_delete_resp = requests.delete(api.url_for(Imsi, _external=True),
                                               data=json.dumps(self.imsi_tracking_dict),
                                               headers=self.imsi_header,
                                               cookies={'access_token_cookie': request.cookies.get('access_token_cookie')})

            if imsi_delete_resp.status_code == requests.codes.ok:
                Common.create_flash_message(imsi_delete_resp.json().get('imsi_msg'))
                return True
            else:
                if imsi_delete_resp.status_code == requests.codes.unauthorized:
                    self.redirect_to_uscc_login()
                    return self.login_redirect_response
                else:
                    delete_error_message = "%s: %s" % (imsi_delete_resp.status_code, imsi_delete_resp.reason)
                    Common.create_flash_message(delete_error_message, 'error')
                    return False

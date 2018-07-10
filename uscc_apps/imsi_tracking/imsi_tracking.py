# Flask
from flask import render_template, redirect, request, url_for
from flask.views import MethodView

# USCC
from uscc_apps.imsi_tracking.forms import ImsiForm
from uscc_apps.common import Common

# Misc
import requests
import json
import sys
import os


class ImsiTracking(MethodView):
    def __init__(self):

        self.imsi_tracking_api_url = os.environ.get('imsi_tracking_api_url')
        self.art = None
        self.imsi_header = {'content-type': 'application/json'}
        self.imsi_tracking_dict = dict(imsi=None,
                                       userid=None,
                                       email=None
                                       )
        self.imsi_list_get_resp = None

    def get(self):
        """
        Receives control from the HTTP GET request when accessing the Imsi tracking web app. Renders the initial html
        web page with the empty web form and does an HTTP GET request to the USCC ENG REST API to retrieve and display
        the current list of tracked imsis.

        :return: Renders the html page with all substituted content needed.
        """

        print(request.cookies.get('session'))
        print(request.cookies.get('access_token_cookie'))
        if request.cookies.get('session') is None:
            # return redirect(url_for(os.environ.get('login_app'), callback_url=url_for('imsi_tracking')))
            return redirect(os.environ.get('login_app') + '?callback_url=' + url_for('imsi_tracking', _external=True))

        self.imsi_tracking_dict['userid'] = request.cookies.get('userid')

        auth_header = {'Authorization': 'JWT {}'.format(request.cookies.get('session'))}
        form = ImsiForm()
        imsi_list = {}
        email_list = {}
        self.imsi_list_get_resp = requests.get(self.imsi_tracking_api_url, params=self.imsi_tracking_dict, headers=auth_header)
        if self.imsi_list_get_resp.status_code == requests.codes.ok:
            if request.args.get('imsi_filter') is not None and request.args.get('imsi_filter') != '':
                imsi_list = self.filter_imsis()
            else:
                imsi_list = self.imsi_list_get_resp.json().get('imsi_list')

            email_list = self.imsi_list_get_resp.json().get('email_list')
        elif self.imsi_list_get_resp.status_code == requests.codes.unauthorized:
            return redirect(url_for('uscc_login'))
        else:
            get_imsi_list_error = "Retrieving list of tracked Imsi failed with: %s:%s.\nPlease contact Core Automation Team" %\
                            (str(self.imsi_list_get_resp.status_code), self.imsi_list_get_resp.reason)
            Common.create_flash_message(get_imsi_list_error)

        return render_template('imsi_tracking/imsi_tracking.html', form=form, imsi_list=imsi_list, art=self.art,
                               userid=self.imsi_tracking_dict.get('userid'), email_list=email_list)

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

        self.set_art()
        form = ImsiForm()
        if form.validate_on_submit():
            if request.form.get('imsis') == "" and request.form.get('email') == "":
                Common.create_flash_message("Please fill in either the Imsi or Email fields.")

            else:
                self.imsi_tracking_dict['imsi'] = request.form.get('imsis')
                self.imsi_tracking_dict['email'] = request.form.get('email')
                self.imsi_tracking_dict['userid'] = request.args.get('userid')
                if self.imsi_tracking_dict.get('email') != '' and '@' not in self.imsi_tracking_dict.get('email'):
                    Common.create_flash_message('Email entered is not a valid email address', 'error')
                    return render_template('imsi_tracking/imsi_tracking.html', form=form)
                if request.form['add_delete_radio'] == 'A':
                    imsi_post_resp = \
                        requests.post(self.imsi_tracking_api_url, data=json.dumps(self.imsi_tracking_dict),
                                      headers=self.imsi_header)
                    Common.create_flash_message(imsi_post_resp.json().get('imsi_msg'))
                    return redirect(url_for('imsi_tracking', art=self.art, userid=self.imsi_tracking_dict.get('userid')))
                else:
                    self.delete()
                    return redirect(url_for('imsi_tracking', art=self.art, userid=self.imsi_tracking_dict.get('userid')))
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

        imsi_delete_resp = requests.delete(self.imsi_tracking_api_url,
                                           data=json.dumps(self.imsi_tracking_dict),
                                           headers=self.imsi_header)

        if imsi_delete_resp.status_code == requests.codes.ok:
            Common.create_flash_message(imsi_delete_resp.json().get('imsi_msg'))
            return True
        else:
            delete_error_message = "%s: %s" % (imsi_delete_resp.status_code, imsi_delete_resp.reason)
            Common.create_flash_message(delete_error_message, 'error')
            return False

    def set_art(self):
        """
        Sets the class variable that contains the known JWT access token.
        :return: True if the class instance variable is set otherwise False
        """

        if request.args.get('art') is not None:
            self.art = request.args.get('art')
            self.imsi_header['Authorization'] = 'JWT {}'.format(self.art)
            return True

        return False

    def filter_imsis(self):
        imsi_list = {}
        user_filter = request.args.get('imsi_filter').lower()
        for key, imsi_value in self.imsi_list_get_resp.json().get('imsi_list').items():
            if '(' in imsi_value:
                imsi, alias_right_paren = imsi_value.split('(', 1)
                alias = alias_right_paren.rstrip(')')
                if user_filter.isdigit():
                    if user_filter == imsi:
                        imsi_list[key] = imsi_value
                else:
                    if user_filter == alias.lower():
                        imsi_list[key] = imsi_value
            else:
                if user_filter == imsi_value:
                    imsi_list[key] = imsi_value
        return imsi_list

# Flask
from flask import render_template, redirect, request, url_for
from flask.views import MethodView

# container status specific
from common.common import Common
from container_status_app import container_status_app

# Misc
import json
import os
from collections import OrderedDict


class NasFaqs(MethodView):
    def __init__(self):

        self.nas_faq_html_template = 'container_status/nas_faqs.html'
        self.faq_dict = OrderedDict()

    def get(self):
        """

        :return: Renders the html page with all substituted content needed.
        """

        if os.environ.get('faq_data_path') is None or os.environ.get('faq_data_path') == '':
            container_status_app.logger.error("Environment variable 'faq_data_path' not defined.")
            return render_template(self.nas_faq_html_template, faq_file_err=True)
        read_json_rc, self.faq_dict = Common.rw_json_file(file_path=os.environ.get('faq_data_path'))
        if read_json_rc:
            return render_template(self.nas_faq_html_template, faq_dict=self.faq_dict)

        return render_template(self.nas_faq_html_template, faq_file_err=True)

    def post(self):
        """
        Receives control when the Submit button is clicked in the Notifications Card to register an email address.
        :return: Re-renders the page with the message of whether the email address was registered successfully or not.
        """

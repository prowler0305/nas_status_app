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


class NasAddFaq(MethodView):
    def __init__(self):

        self.nas_add_faq_html_template = 'container_status/nas_add_faq.html'
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
            return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict)
        else:
            container_status_app.logger.error("FAQ data file could not be read at location {}".format(os.environ.get('faq_data_path')))
            return render_template(self.nas_add_faq_html_template, faq_file_err=True)

    def post(self):
        """
        Receives control when the Submit button is clicked in the Notifications Card to register an email address.
        :return: Re-renders the page with the message of whether the email address was registered successfully or not.
        """

        read_json_rc, self.faq_dict = Common.rw_json_file(file_path=os.environ.get('faq_data_path'))
        if read_json_rc:
            faq_category_dicts = self.faq_dict.get(request.form.get('faq_type_radio'))
            if "\r\n" in request.form.get('faq_content'):
                faq_content_data = request.form.get('faq_content').split("\r\n")
            else:
                faq_content_data = request.form.get('faq_content')
            faq_category_dicts[request.form.get('faq_question')] = faq_content_data
            self.faq_dict[request.form.get('faq_type_radio')] = faq_category_dicts
            update_json_rc, file_updated = Common.rw_json_file(file_path=os.environ.get('faq_data_path'),
                                                               mode='write',
                                                               output_dict=self.faq_dict)
            if update_json_rc:
                container_status_app.logger.info("New FAQ: {} | Category: {} | Content: {}".format(
                    request.form.get('faq_question'), request.form.get('faq_type_radio'), request.form.get('faq_content')))
                return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict, faq_added_rc=True)
            else:
                container_status_app.logger.error("Unable to add to Category: {} | FAQ: {} | Content: {}".format(
                    request.form.get('faq_type_radio'), request.form.get('faq_question'), request.form.get('faq_content')))
                return render_template(self.nas_add_faq_html_template, faq_added_rc=False)

        else:
            container_status_app.logger.error("Unable to read JSON file containing FAQ data at path: {}".format(os.environ.get('faq_data_path')))
            return render_template(self.nas_add_faq_html_template, faq_added_rc=False)

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
            # for faq_category, faq_dicts in self.faq_dict.items():
            #     for faq_question, faq_content in faq_dicts.items():
            #         if type(faq_content) is list:
            #             joined_multiline_content = ""
            #             for content_string in faq_content:
            #                 joined_multiline_content = joined_multiline_content + content_string + "\r\n"
            #             faq_dicts[faq_question] = joined_multiline_content.replace("\r\n", "<br\>")
            #         self.faq_dict[faq_category] = faq_dicts
            return render_template(self.nas_faq_html_template, faq_dict=self.faq_dict)

        return render_template(self.nas_faq_html_template, faq_file_err=True)

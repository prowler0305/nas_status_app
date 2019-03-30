# Flask
from flask import render_template, redirect, request, url_for
from flask.views import MethodView

# container status specific
from common.common import Common
from container_status_app import container_status_app

# Misc
import json
import os


class NasFaqs(MethodView):
    def __init__(self):

        self.nas_faq_html_template = 'container_status/nas_faqs.html'

    def get(self):
        """

        :return: Renders the html page with all substituted content needed.
        """

        return render_template(self.nas_faq_html_template)

    def post(self):
        """
        Receives control when the Submit button is clicked in the Notifications Card to register an email address.
        :return: Re-renders the page with the message of whether the email address was registered successfully or not.
        """

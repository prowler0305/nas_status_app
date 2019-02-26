# Flask
from flask import render_template, redirect, request, url_for
from flask.views import MethodView

# USCC
from common.common import Common

# Misc
import json
import os


class ContainerStatus(MethodView):
    def __init__(self):

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

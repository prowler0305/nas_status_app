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
        self.notify_email_dict = None
        self.nas_down_email = dict(subject='NAS Automation Platform Outage',
                                   from_addr='SA3CoreAutomationTeam@noreply.com',
                                   to_addr='Andrew.Spear@uscellular.com',
                                   content='There will be an outage with the NAS Automation Platform on Saturday')
        self.nas_production_html_template = 'container_status/nas_prod_status.html'

    def get(self):
        """

        :return: Renders the html page with all substituted content needed.
        """

        read_json_rc, self.container_status_dict = Common.rw_json_file(file_path=os.environ.get('container_status_path'))
        if read_json_rc:
            if request.url_rule.rule == '/nas_status':
                if 'nas_production' in self.container_status_dict:
                    read_email_rc, email_address_dict = Common.rw_json_file(file_path=os.environ.get('notify_emails_path'))
                    if read_email_rc and type(email_address_dict) is dict:
                        return render_template(self.nas_production_html_template,
                                               cs=self.container_status_dict.get('nas_production'),
                                               list_registered_emails=email_address_dict.get('email_address_list'))

                    return render_template(self.nas_production_html_template,
                                           cs=self.container_status_dict.get('nas_production'))
                else:
                    return render_template(self.nas_production_html_template)

            return render_template(self.nas_production_html_template, cs=self.container_status_dict)

    def post(self):
        """
        Receives control when the Submit button is clicked in the Notifications Card to register an email address.
        :return: Re-renders the page with the message of whether the email address was registered successfully or not.
        """

        write_notify_email_file_rc = False
        read_status_file_rc, self.container_status_dict = Common.rw_json_file(file_path=os.environ.get('container_status_path'))
        if read_status_file_rc:
            if not Common.check_path_exists(os.environ.get('notify_emails_path')):
                with open(os.environ.get('notify_emails_path'), 'w+') as emfh:
                    emfh.write('{"email_address_list": []}')

            read_notify_email_file_rc, self.notify_email_dict = Common.rw_json_file(file_path=os.environ.get('notify_emails_path'))
            if read_notify_email_file_rc:
                if request.form.get('email_addr') not in self.notify_email_dict.get('email_address_list'):
                    self.notify_email_dict.get('email_address_list').append(request.form.get('email_addr'))
                    write_notify_email_file_rc, write_info = Common.rw_json_file(os.environ.get('notify_emails_path'),
                                                                                 mode='write',
                                                                                 output_dict=self.notify_email_dict)
                else:
                    write_notify_email_file_rc = True

        return render_template(self.nas_production_html_template, cs=self.container_status_dict.get('nas_production'),
                               email_registered=write_notify_email_file_rc)

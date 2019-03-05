# Flask
from flask import render_template, redirect, request, url_for
from flask.views import MethodView

# USCC
from common.common import Common

# Misc
import json
import os
import shutil
from services.email import EmailServices


class NasNotifications(MethodView):
    def __init__(self):

        self.nas_down_email = dict(subject='Critical Bulletin - NAS Automation Platform Outage - Date: {}',
                                   from_addr='SA3CoreAutomationTeam@noreply.com')
        self.nas_notify_html_template = 'container_status/nas_notify.html'
        self.notify_email_dict = None
        self.email_template_temp_file = os.environ.get('scratch_dir') + '/copy_nas_outage_email'

    def get(self):
        """

        :return: Renders the html page with all substituted content needed.
        """
        return render_template(self.nas_notify_html_template)

    def post(self):
        """
        Receives control when the Submit button is clicked in the Notifications Card to register an email address.
        :return: Re-renders the page with the message of whether the email address was registered successfully or not.
        """

        if 'Choose' in request.form.get('time_of_day_start'):
            return render_template(self.nas_notify_html_template, tods_error=True)
        elif 'Choose' in request.form.get('time_of_day_end'):
            return render_template(self.nas_notify_html_template, tode_error=True)

        shutil.copyfile(os.environ.get('nas_down_email_template'), self.email_template_temp_file)
        with open(self.email_template_temp_file, 'r+') as email_template_fh:
            email_template_data = email_template_fh.read()
            email_template_data = email_template_data.replace('{sd}', request.form.get('outage_start_date'))
            email_template_data = email_template_data.replace('{st}', "{} {}".format(request.form.get('outage_start_time'), request.form.get('time_of_day_start')))
            email_template_data = email_template_data.replace('{ed}', request.form.get('outage_end_date'))
            email_template_data = email_template_data.replace('{et}', "{} {}".format(request.form.get('outage_end_time'), request.form.get('time_of_day_end')))
            email_template_fh.seek(0)
            email_template_fh.truncate()
            email_template_fh.write(email_template_data)

        read_notify_email_file_rc, self.notify_email_dict = Common.rw_json_file(file_path=os.environ.get('notify_emails_path'))
        if read_notify_email_file_rc:
            email = EmailServices(subject=self.nas_down_email.get('subject').format(request.form.get('outage_start_date')),
                                  from_address=self.nas_down_email.get('from_addr'),
                                  to_address=self.notify_email_dict.get('email_address_list'))

            with open(self.email_template_temp_file) as email_fh:
                email.send_email(email_fh.read())

        return render_template(self.nas_notify_html_template)

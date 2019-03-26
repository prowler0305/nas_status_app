# Flask
from flask import render_template, redirect, request, url_for
from flask.views import MethodView

# container status specific
from common.common import Common
from container_status_app import container_status_app

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
        self.container_status_dict = None

    def get(self):
        """

        :return: Renders the html page with all substituted content needed.
        """
        read_json_rc, self.container_status_dict = Common.rw_json_file(file_path=os.environ.get('container_status_path'))
        if read_json_rc:
            if self.container_status_dict.get('nas_production') is not None and self.container_status_dict.get\
                        ('nas_production').get('display_name') == 'NAS Automation Platform':
                return render_template(self.nas_notify_html_template,
                                       nas_overall_status=self.container_status_dict.get('nas_production').get('overall_status'))

        return render_template(self.nas_notify_html_template)

    def post(self):
        """
        Receives control when the Submit button is clicked in the Notifications Card to register an email address.
        :return: Re-renders the page with the message of whether the email address was registered successfully or not.
        """

        if request.form.get('status_switch') is not None:
            self.put()
        else:
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
                email_template_data = email_template_data.replace('{why}', "{}".format(request.form.get('reason_textarea')))
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

                read_json_rc, self.container_status_dict = Common.rw_json_file(file_path=os.environ.get('container_status_path'))
                if read_json_rc:
                    nas_production_dict = self.container_status_dict.get('nas_production')
                    if nas_production_dict is not None and nas_production_dict.get('display_name') == 'NAS Automation Platform':
                        nas_production_dict['overall_status'] = 'NOT ACTIVE'
                        nas_production_dict['restored_by'] = '{} {} {} CST'.format(request.form.get('outage_end_date'),
                                                                                   request.form.get('outage_end_time'),
                                                                                   request.form.get('time_of_day_end'))
                        write_json_rc, file_updated = Common.rw_json_file(file_path=os.environ.get('container_status_path'),
                                                                          mode='write',
                                                                          output_dict=self.container_status_dict)
                        container_status_app.logger.info("Container status JSON file updated successfully: {}".format(file_updated))
                else:
                    container_status_app.logger.error("File path {} for container status JSON data could not be updated"
                                                      .format(os.environ.get('container_status_path')))

                    return render_template(self.nas_notify_html_template,
                                           status_file_update_err=os.environ.get('container_status_path'))

        return render_template(self.nas_notify_html_template,
                               nas_overall_status=self.container_status_dict.get('nas_production').get('overall_status'))

    def put(self):
        """
        Called by the Post method if the Status Switch button is toggled. Looks at updating the container status JSON
        data to set the overall_status field for the NAS Platform.

        :return:
        """
        if request.form.get('status_switch') == 'on':
            set_nas_overall_status = 'ACTIVE'
        else:
            set_nas_overall_status = 'NOT ACTIVE'

        read_json_rc, self.container_status_dict = Common.rw_json_file(file_path=os.environ.get('container_status_path'))
        if read_json_rc:
            if self.container_status_dict.get('nas_production') is not None:
                if self.container_status_dict['nas_production'].get('overall_status') is not None:
                    self.container_status_dict['nas_production']['overall_status'] = set_nas_overall_status
                    update_json_rc, file_updated = Common.rw_json_file(file_path=os.environ.get('container_status_path'),
                                                                       mode='write',
                                                                       output_dict=self.container_status_dict)

                    update_log_message = "{} update of container status JSON file. Path: {}".format(
                        'Successful' if update_json_rc else 'Unsuccessful', file_updated)
                    if update_json_rc:
                        container_status_app.logger.info(update_log_message)
                    else:
                        container_status_app.logger.error(update_log_message)
        return

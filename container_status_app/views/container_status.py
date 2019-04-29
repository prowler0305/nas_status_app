# Flask
from flask import render_template, request, redirect, url_for
from flask.views import MethodView

# Container status app specific
from container_status_app.common.common import Common
from flask import current_app as container_status_app

# Misc
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
        self.base_notify_emails_json_structure = '{"agg_router_health_check": {"email_list": [], "platform": "old"}, ' \
                                                 '"b2b": {"email_list": [], "platform": "new"}, ' \
                                                 '"ethersam": {"email_list": [], "platform": "old"}, ' \
                                                 '"mvlan": {"email_list": [], "platform": "old"}, ' \
                                                 '"segw_health_check": {"email_list": [], "platform": "old"}}'

    def get(self):
        """

        :return: Renders the html page with all substituted content needed.
        """
        if os.environ.get('container_status_path') is None or os.environ.get('container_status_path') == '':
            container_status_app.logger.error("Environment variable 'container_status_path' not defined.")
            return render_template(self.nas_production_html_template, status_file_err=True)
        read_json_rc, self.container_status_dict = Common.rw_json_file(file_path=os.environ.get('container_status_path'))
        if read_json_rc:
            if request.url_rule.rule == '/nas_status' or request.url_rule.rule == '/':
                if 'nas_production' in self.container_status_dict:
                    if os.environ.get('notify_emails_path') is not None and os.environ.get('notify_emails_path') != '':
                        self.create_emails_file()
                        read_email_rc, self.notify_email_dict = Common.rw_json_file(file_path=os.environ.get('notify_emails_path'))
                        if read_email_rc and type(self.notify_email_dict) is dict:
                            return render_template(self.nas_production_html_template,
                                                   cs=self.container_status_dict.get('nas_production'),
                                                   list_registered_emails=self.notify_email_dict)
                        else:
                            return render_template(self.nas_production_html_template,
                                                   cs=self.container_status_dict.get('nas_production'))
                    else:
                        container_status_app.logger.error("Environment variable 'notify_emails_path' not defined")
                        return render_template(self.nas_production_html_template,
                                               cs=self.container_status_dict.get('nas_production'))
                else:
                    return render_template(self.nas_production_html_template)

            return render_template(self.nas_production_html_template, cs=self.container_status_dict)
        else:
            container_status_app.logger.error("File {} could not be read.".format(os.environ.get('container_status_path')))
            return render_template(self.nas_production_html_template, status_file_err=True)

    def post(self):
        """
        Receives control when the Submit button is clicked in the Notifications Card to register an email address.
        :return: Re-renders the page with the message of whether the email address was registered successfully or not.
        """

        read_status_file_rc, self.container_status_dict = Common.rw_json_file(file_path=os.environ.get('container_status_path'))
        if read_status_file_rc:
            if request.form.get('add_delete_email_radio') == 'delete':
                self.delete_email()
            else:
                write_notify_email_file_rc = False
                self.create_emails_file()

                read_notify_email_file_rc, self.notify_email_dict = Common.rw_json_file(file_path=os.environ.get('notify_emails_path'))
                if read_notify_email_file_rc:
                    if request.form.get('app_email_register_radio') != 'ALL':
                        app_email_list = self.notify_email_dict.get(request.form.get('app_email_register_radio')).get('email_list')
                        if request.form.get('email_addr') not in app_email_list:
                            app_email_list.append(request.form.get('email_addr'))
                            write_notify_email_file_rc, write_info = Common.rw_json_file(os.environ.get('notify_emails_path'),
                                                                                         mode='write',
                                                                                         output_dict=self.notify_email_dict)
                        else:
                            write_notify_email_file_rc = True
                    else:
                        for app_email_dict in self.notify_email_dict.values():
                            if request.form.get('email_addr') not in app_email_dict.get('email_list'):
                                app_email_dict.get('email_list').append(request.form.get('email_addr'))

                        write_notify_email_file_rc, write_info = Common.rw_json_file(os.environ.get('notify_emails_path'),
                                                                                     mode='write',
                                                                                     output_dict=self.notify_email_dict)
                    if write_notify_email_file_rc:
                        Common.create_flash_message("Email registered Successfully")
                    else:
                        Common.create_flash_message("Error registering email. Please contact SA3 Core Automation Team.")

        return redirect(url_for("container_status"))

    def delete_email(self):
        """
        Deletes the email address from the requested app or all apps from the form in the Notifications card
        :return:
        """
        write_notify_email_file_rc = False

        read_notify_email_file_rc, self.notify_email_dict = Common.rw_json_file(file_path=os.environ.get('notify_emails_path'))
        if read_notify_email_file_rc:
            if request.form.get('app_email_register_radio') != 'ALL':
                app_email_list = self.notify_email_dict.get(request.form.get('app_email_register_radio')).get('email_list')
                if request.form.get('email_addr') in app_email_list:
                    app_email_list.remove(request.form.get('email_addr'))
                    write_notify_email_file_rc, write_info = Common.rw_json_file(os.environ.get('notify_emails_path'),
                                                                                 mode='write',
                                                                                 output_dict=self.notify_email_dict)
                else:
                    write_notify_email_file_rc = True
            else:
                for app_email_dict in self.notify_email_dict.values():
                    if request.form.get('email_addr') in app_email_dict.get('email_list'):
                        app_email_dict.get('email_list').remove(request.form.get('email_addr'))

                write_notify_email_file_rc, write_info = Common.rw_json_file(os.environ.get('notify_emails_path'),
                                                                             mode='write',
                                                                             output_dict=self.notify_email_dict)
        if write_notify_email_file_rc:
            Common.create_flash_message("Email Deleted Successfully")
        else:
            Common.create_flash_message("Error deleting email. Please contact SA3 Core Automation Team.")
        return

    def create_emails_file(self):
        """
        Creates the JSON structure for the list of emails if it doesn't exist. Uses the base json structure defined as
        a class attribute.

        :return:
        """

        if not Common.check_path_exists(os.environ.get('notify_emails_path')):
            with open(os.environ.get('notify_emails_path'), 'w+') as emfh:
                emfh.write(self.base_notify_emails_json_structure)
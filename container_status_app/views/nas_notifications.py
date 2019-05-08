# Flask
from flask import render_template, request
from flask.views import MethodView
from werkzeug.utils import secure_filename

# container status specific
from container_status_app.common.common import Common
from container_status_app.services.email import EmailServices
from flask import current_app as container_status_app

# Misc
import os
import shutil


class NasNotifications(MethodView):
    def __init__(self):

        self.default_from_email_addr = 'SA3CoreAutomationTeam@noreply.com'
        self.nas_down_email = dict(subject='Critical Bulletin - NAS Automation Platform Outage - Date: {}',
                                   from_addr=self.default_from_email_addr)
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
                                       nas_prod_status_data=self.container_status_dict.get('nas_production'))

        return render_template(self.nas_notify_html_template)

    def post(self):
        """
        Receives control when the Submit button is clicked in either of the send email forms

        :return: Message indicating if the email was successfully sent or not.
        """

        if 'toggle_switch_form' in list(request.form.keys()) or 'p2_toggle_switch_form' in list(request.form.keys()):
            self.toggle_platform_status()
        else:
            read_json_rc, self.container_status_dict = Common.rw_json_file(file_path=os.environ.get('container_status_path'))
            nas_production_dict = self.container_status_dict.get('nas_production')

            if 'nas_notify_form' in list(request.form.keys()):
                if self.send_email_notification():
                    Common.create_flash_message("Email sent Successfully", category_request='info')
                else:
                    Common.create_flash_message("Error sending email. Please Contact SA3 Core Automation Team.",
                                                category_request='error')

                return render_template(self.nas_notify_html_template,
                                       nas_prod_status_data=self.container_status_dict.get('nas_production'))

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
                if request.form.get('platform_name') == 'old_platform':
                    apps_list = nas_production_dict.get('applications').keys()
                else:
                    apps_list = nas_production_dict.get('new_platform_apps').keys()

                app_replacement_string = ''
                for app in apps_list:
                    app_replacement_string = app_replacement_string + 'o	{}\n'.format(app)

                email_template_data = email_template_data.replace('{app}', app_replacement_string)
                email_template_fh.seek(0)
                email_template_fh.truncate()
                email_template_fh.write(email_template_data)

            read_notify_email_file_rc, self.notify_email_dict = Common.rw_json_file(file_path=os.environ.get('notify_emails_path'))
            if read_notify_email_file_rc:
                dict_of_emails = dict()
                for app, app_email_data in self.notify_email_dict.items():
                    if app_email_data.get('platform') in request.form.get('platform_name'):
                        dict_of_emails[app] = app_email_data.get('email_list')

                email = EmailServices(subject=self.nas_down_email.get('subject').format(request.form.get('outage_start_date')),
                                      from_address=self.nas_down_email.get('from_addr'),
                                      to_address=Common.flatten_list(dict_of_emails))

                with open(self.email_template_temp_file) as email_fh:
                    email_sent = email.send_email(email_fh.read())
                email_sent_message = "Outage notification email {}"
                if email_sent:
                    container_status_app.logger.info(email_sent_message.format('sent'))
                    Common.create_flash_message("Email sent Successfully", category_request='info')
                else:
                    container_status_app.logger.error(email_sent_message.format('not sent'))
                    Common.create_flash_message("Error sending email. Please Contact SA3 Core Automation Team.",
                                                category_request='error')

                if read_json_rc and nas_production_dict is not None:
                    if request.form.get('platform_name') == 'old_platform':
                        overall_status = 'overall_status'
                        restored_by = 'restored_by'
                    else:
                        overall_status = 'p2_overall_status'
                        restored_by = 'p2_restored_by'
                    nas_production_dict[overall_status] = 'NOT ACTIVE'
                    nas_production_dict[restored_by] = '{} {} {} CST'.format(request.form.get('outage_end_date'),
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
                               nas_prod_status_data=self.container_status_dict.get('nas_production'))

    def toggle_platform_status(self):
        """
        Called when the one of the forms containing the platform toggle switches are submitted. Contains the high level
        logic and then calls the appropriate put() method.

        :return:
        """
        read_json_rc, self.container_status_dict = Common.rw_json_file(file_path=os.environ.get('container_status_path'))
        nas_production_dict = self.container_status_dict.get('nas_production')

        if nas_production_dict is not None and nas_production_dict.get('display_name') == 'NAS Automation Platform':
            if 'toggle_switch_form' in list(request.form.keys()):
                toggle_switch_names = self.create_list_of_toggle_names(nas_production_dict.get('applications').keys())
                status_switch_name = nas_production_dict.get('display_name') + '_status_switch'
                additional_info_name = None
                app_toggle_info_tuple = (status_switch_name, additional_info_name)
                toggle_switch_names.append(app_toggle_info_tuple)
                self.put(list_o_switch_name=toggle_switch_names)
            if 'p2_toggle_switch_form' in list(request.form.keys()):
                toggle_switch_names = self.create_list_of_toggle_names(nas_production_dict.get('new_platform_apps').keys())
                status_switch_name = nas_production_dict.get('p2_display_name') + '_status_switch'
                additional_info_name = None
                app_toggle_info_tuple = (status_switch_name, additional_info_name)
                toggle_switch_names.append(app_toggle_info_tuple)
                self.put_p2(list_o_switch_name=toggle_switch_names)
        return

    def send_email_notification(self):
        """
        Called by the POST method when the "Send Email Notification" form is submitted.

        :return: True or false the email was sent.
        """
        email_sent_message = "Notification email {}"
        read_notify_email_file_rc, self.notify_email_dict = Common.rw_json_file(file_path=os.environ.get('notify_emails_path'))
        if read_notify_email_file_rc:
            file = request.files.get('attachment_file', None)
            if request.files.get('attachment_file') is not None:
                file = request.files.get('attachment_file')
                filename = secure_filename(file.filename)
                if not os.path.exists(container_status_app.config.get('UPLOAD_FOLDER')):
                    os.makedirs(container_status_app.config.get('UPLOAD_FOLDER'))
                file.save(os.path.join(container_status_app.config.get('UPLOAD_FOLDER'), filename))

            if request.form.get('from_email_addr') is None or request.form.get('from_email_addr') == '':
                # send_from = self.default_from_email_addr
                send_from = None
            else:
                send_from = request.form.get('from_email_addr').strip() + '@uscellular.com'

            if request.form.get('app_email_radio') == 'ALL':
                dict_of_emails = dict()
                for app, app_email_data in self.notify_email_dict.items():
                    dict_of_emails[app] = app_email_data.get('email_list')
                list_of_addr_to_send_to = Common.flatten_list(dict_of_emails)

            else:
                list_of_addr_to_send_to = self.notify_email_dict.get(request.form.get('app_email_radio').lower()).get('email_list')

            email = EmailServices(subject=request.form.get('email_subject'),
                                  from_address=send_from,
                                  to_address=list_of_addr_to_send_to)

            # email_sent = email.send_email(request.form.get('email_content'))
            email_sent = email.send_email(request.form.get('email_content'),
                                          attachment=file)
            if os.path.exists(os.path.join(container_status_app.config.get('UPLOAD_FOLDER'), file.filename)):
                os.remove(os.path.join(container_status_app.config.get('UPLOAD_FOLDER'), file.filename))
            if email_sent:
                container_status_app.logger.info(email_sent_message.format('sent'))
                return True
            else:
                container_status_app.logger.error(email_sent_message.format('not sent'))
                return False
        else:
            container_status_app.logger.error(email_sent_message.format('not sent. List of registered emails could not be retrieved.'))
            return False

    def put(self, list_o_switch_name):
        """
        Called by the Post method if the Status Switch button is toggled. Looks at updating the container status JSON
        data to set the overall_status field for the NAS Platform.

        :param list_o_switch_name: switch names from the nas_notify.html components.
        :return:
        """

        if self.container_status_dict.get('nas_production') is not None:
            if self.container_status_dict['nas_production'].get('overall_status') is not None:
                for switch_tuple in list_o_switch_name:
                    """
                    For each switch tuple (i.e. (switch name, additional info) find the switch name in the request form 
                    and see if it was switch on or off and set the appropriate status string.
                    """
                    if request.form.get(switch_tuple[0]) == 'on':
                        update_status = 'ACTIVE'
                    else:
                        update_status = 'NOT ACTIVE'

                    update_app_name = switch_tuple[0].split('_', 1)
                    if update_app_name[0] == self.container_status_dict.get('nas_production').get('display_name'):
                        if update_status == 'ACTIVE':
                            self.container_status_dict['nas_production']['overall_status'] = update_status
                    else:
                        self.container_status_dict['nas_production']['applications'][update_app_name[0]]['status'] = update_status
                        self.container_status_dict['nas_production']['applications'][update_app_name[0]]['additional_info'] = switch_tuple[1]

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

    def put_p2(self, list_o_switch_name):
        """
        Called by the Post method if the Status Switch button is toggled on the New Architecture tab panel. Looks at
        updating the container status JSON data to set the overall and each application status keys.

        :param list_o_switch_name: switch names from the nas_notify.html components.
        :return:
        """

        if self.container_status_dict.get('nas_production') is not None:
            if self.container_status_dict['nas_production'].get('p2_overall_status') is not None:
                for switch_tuple in list_o_switch_name:
                    """
                    For each switch tuple (i.e. (switch name, additional info) find the switch name in the request form 
                    and see if it was switch on or off and set the appropriate status string.
                    """
                    if request.form.get(switch_tuple[0]) == 'on':
                        update_status = 'ACTIVE'
                    else:
                        update_status = 'NOT ACTIVE'

                    update_app_name = switch_tuple[0].split('_', 1)
                    if update_app_name[0] == self.container_status_dict.get('nas_production').get('p2_display_name'):
                        if update_status == 'ACTIVE':
                            self.container_status_dict['nas_production']['p2_overall_status'] = update_status
                    else:
                        self.container_status_dict['nas_production']['new_platform_apps'][update_app_name[0]]['status'] = update_status
                        self.container_status_dict['nas_production']['new_platform_apps'][update_app_name[0]]['additional_info'] = switch_tuple[1]

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

    @staticmethod
    def create_list_of_toggle_names(application_names: list):
        """
        Given a the list of application names from the container_status_data JSON file, generates and return a list of
        tuples containing (switch name, additional info textarea name)

        :param application_names: list of applications names (i.e. ['B2B', 'Ethersam', 'etc...']
        :return: list of tuples
        """

        toggle_switch_names = []

        for app_name in application_names:
            status_switch_name = app_name + '_status_switch'
            additional_info_name = request.form.get(app_name + '_textarea')
            app_toggle_info_tuple = (status_switch_name, additional_info_name)
            toggle_switch_names.append(app_toggle_info_tuple)

        return toggle_switch_names

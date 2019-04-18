# Flask
from flask import render_template, request
from flask.views import MethodView
from werkzeug.utils import secure_filename

# container status specific
from container_status_app.common.common import Common
from flask import current_app as container_status_app

# Misc
import os
from collections import OrderedDict
import shutil


class NasAddFaq(MethodView):
    def __init__(self):

        self.nas_add_faq_html_template = 'container_status/nas_add_faq.html'
        self.faq_dict = OrderedDict()
        self.allowed_extensions = set(['txt'])
        self.faq_backup_file = os.environ.get('scratch_dir') + '/backup_faq_data.json'

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
            if 'deleteFAQButton' in request.form.keys():
                    if len(request.form) > 1:
                        if self.delete():
                            self.backup_faq_data()
                            reread_json_rc, self.faq_dict = Common.rw_json_file(file_path=os.environ.get('faq_data_path'))
                            if reread_json_rc:
                                return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict,
                                                       faq_delete_rc=True)
                            else:
                                return render_template(self.nas_add_faq_html_template, faq_file_err=True)
                        else:
                            return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict,
                                                   faq_delete_rc=False)
                    else:
                        return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict,
                                               faq_selected=False)
            else:
                if 'faq_file' in request.files:
                    if self.process_faq_file():
                        self.backup_faq_data()
                        return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict,
                                               faq_added_rc=True)
                    else:
                        if self.backup_faq_data(restore=True):
                            reread_json_rc, self.faq_dict = Common.rw_json_file(os.environ.get('faq_data_path'))
                            return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict,
                                                   faq_added_rc=False)
                        else:
                            return render_template(self.nas_add_faq_html_template, faq_file_err=True)

                faq_category_dicts = self.faq_dict.get(request.form.get('faq_type_radio'))
                if request.form.get('faq_question') == '' and request.form.get('faq_content') == '':
                    error_message = "Please fill in the Question and Answer form or select a file to be uploaded"
                    Common.create_flash_message(error_message, 'error')
                    return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict)
                if "\r\n" in request.form.get('faq_content'):
                    faq_content_data = request.form.get('faq_content').split("\r\n")
                else:
                    faq_content_data = request.form.get('faq_content')
                faq_category_dicts[request.form.get('faq_question')] = faq_content_data
                self.faq_dict[request.form.get('faq_type_radio')] = faq_category_dicts
                update_json_rc, file_updated = Common.rw_json_file(file_path=os.environ.get('faq_data_pah'),
                                                                   mode='write',
                                                                   output_dict=self.faq_dict)
                if update_json_rc:
                    container_status_app.logger.info("New FAQ: {} | Category: {} | Content: {}".format(
                        request.form.get('faq_question'), request.form.get('faq_type_radio'), request.form.get('faq_content')))
                    self.backup_faq_data()
                    return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict, faq_added_rc=True)
                else:
                    container_status_app.logger.error("Unable to add to Category: {} | FAQ: {} | Content: {}".format(
                        request.form.get('faq_type_radio'), request.form.get('faq_question'), request.form.get('faq_content')))
                    _, self.faq_dict = Common.rw_json_file(os.environ.get('faq_data_path'))
                    return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict, faq_added_rc=False)
        else:
            container_status_app.logger.error("Unable to read JSON file containing FAQ data at path: {}".format(os.environ.get('faq_data_path')))
            return render_template(self.nas_add_faq_html_template, faq_added_rc=False)

    def delete(self):
        """
        Called when the Delete button is pressed on the Delete FAQ form on the /nas/add/faq page.

        Expects that the faq_dict class instance variable has been populated by the post() method above.

        :return: True/False if the selected FAQ titles were deleted or not.
        """
        faqs_deleted = False
        for faq_to_delete_key, faq_to_delete_value in request.form.items():
            if 'FAQButton' in faq_to_delete_key:
                continue
            else:
                faq_delete_metadata_list = faq_to_delete_key.split(':')
                category_faq_dict = self.faq_dict.get(faq_delete_metadata_list[0])
                if faq_to_delete_value == 'ALL':
                    category_faq_dict.clear()
                    container_status_app.logger.info("All FAQs in Category {} have been deleted".format(faq_delete_metadata_list[0].upper()))
                    faqs_deleted = True
                else:
                    if category_faq_dict.pop(faq_to_delete_value, None) is not None:
                        container_status_app.logger.info("FAQ {} in Category {} has been deleted.".format(
                            faq_to_delete_value, faq_delete_metadata_list[0].upper()))
                        faqs_deleted = True
                    else:
                        container_status_app.logger.warning("FAQ {} in Category {} not found.".format(
                            faq_to_delete_value, faq_delete_metadata_list[0].upper()))

        update_json_rc, file_updated = Common.rw_json_file(file_path=os.environ.get('faq_data_path'),
                                                           mode='write',
                                                           output_dict=self.faq_dict)
        if update_json_rc:
            container_status_app.logger.info("FAQ data file {} updated successfully.".format(os.environ.get('faq_data_path')))
        else:
            container_status_app.logger.error("FAQ data file {} could not be updated.".format(os.environ.get('faq_data_path')))
            if faqs_deleted:
                faqs_deleted = False

        if faqs_deleted:
            return True
        else:
            return False

    def allowed_file_types(self, filename):
        """
        Checks a file to make sure that it is one of the allowable types.
        :param filename:
        :return:
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def process_faq_file(self):
        """
        Processes an FAQ file uploaded via the upload element on the /nas/add/faq page.

        :return:
        """

        question_keywords = ['Question', 'QUESTION', 'question']
        answer_keywords = ['Answer', 'answer', 'ANSWER']

        file = request.files.get('faq_file')
        if file.filename == '':
            return False
        if file and self.allowed_file_types(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(container_status_app.config.get('UPLOAD_FOLDER'), filename))
            faq_category_dicts = self.faq_dict.get(request.form.get('faq_type_radio'))
            current_question = None
            # with open(os.path.join(container_status_app.config.get('UPLOAD_FOLDER'), filename)) as faq_file_handler:
            #     for line in faq_file_handler:
            for line in file:
                if line.decode('utf-8-sig').split(':', 1)[0] in question_keywords:
                    faq_category_dicts[(line.decode('utf-8-sig').split(':', 1)[1]).rstrip()] = None
                    current_question = line.decode('utf-8-sig').split(':', 1)[1].rstrip()
                elif line.decode('utf-8').split(':', 1)[0] in answer_keywords:
                    if "\n" in line.decode('utf-8').split(':', 1)[1]:
                        faq_category_dicts[current_question] = (line.decode('utf-8').split(':', 1)[1]).rstrip("\n")
                    else:
                        faq_category_dicts[current_question] = line.decode('utf-8').split(':', 1)[1]
                else:  # Have to assume the current read line is part of a answer that has multiple lines for the output
                    current_answer = faq_category_dicts.get(current_question)
                    if not isinstance(current_answer, list):
                        temp_list = [current_answer, line.decode('utf-8').rstrip()]
                        faq_category_dicts[current_question] = temp_list
                    else:
                        current_answer.append(line.decode('utf-8').rstrip())
                        faq_category_dicts[current_question] = current_answer
                # if line.split(':', 1)[0] in question_keywords:
                #     faq_category_dicts[(line.split(':', 1)[1]).rstrip()] = None
                #     current_question = line.split(':', 1)[1].rstrip()
                # elif line.split(':', 1)[0] in answer_keywords:
                #     if "\n" in line.split(':', 1)[1]:
                #         faq_category_dicts[current_question] = (line.split(':', 1)[1]).rstrip("\n")
                #     else:
                #         faq_category_dicts[current_question] = line.split(':', 1)[1]
                # else:  # Have to assume the current read line is part of a answer that has multiple lines for the output
                #     current_answer = faq_category_dicts.get(current_question)
                #     if not isinstance(current_answer, list):
                #         temp_list = [current_answer, line.rstrip()]
                #         faq_category_dicts[current_question] = temp_list
                #     else:
                #         current_answer.append(line.rstrip())
                #         faq_category_dicts[current_question] = current_answer

            self.faq_dict[request.form.get('faq_type_radio')] = faq_category_dicts
            update_json_rc, file_updated = Common.rw_json_file(file_path=os.environ.get('faq_data_path'),
                                                               mode='write',
                                                               output_dict=self.faq_dict)
            if update_json_rc:
                container_status_app.logger.info("FAQ Category: {} updated".format(request.form.get('faq_type_radio').upper()))
                # os.remove(os.path.join(container_status_app.config.get('UPLOAD_FOLDER'), filename))
                return True
            else:
                container_status_app.logger.error("Unable to add to FAQ Category: {}".format(request.form.get('faq_type_radio').upper()))
                return False

    def backup_faq_data(self, restore: bool = False):
        """
        Backs up or restores the faq JSON data by copying the file to or from the backup file path indicated by the
        class attribute faq_backup_file

        :param restore:
        :return:
        """

        if restore:
            if os.path.exists(self.faq_backup_file):
                shutil.copyfile(self.faq_backup_file, os.environ.get('faq_data_path'))
                container_status_app.logger.info("FAQ data restored successfully from {}.".format(self.faq_backup_file))
                return True
            else:
                container_status_app.logger.error("Backup file - {} - doesn't due to either path is incorrect or a backup file hasn't "
                                  "been created yet.".format(self.faq_backup_file))
                return False
        else:
            if not os.path.exists(self.faq_backup_file):
                with open(self.faq_backup_file, mode='w+'):
                    container_status_app.logger.info("Creating backup file location {}.".format(self.faq_backup_file))
            shutil.copyfile(os.environ.get('faq_data_path'), self.faq_backup_file)
            container_status_app.logger.info("FAQ Data backed up successfully to {}.".format(self.faq_backup_file))
            return True

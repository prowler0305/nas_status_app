# Flask
from flask import render_template, request
from flask.views import MethodView

# container status specific
from container_status_app.common.common import Common
from container_status_app import container_status_app

# Misc
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
            if 'deleteFAQButton' in request.form.keys():
                    if len(request.form) > 1:
                        if self.delete():
                            return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict, faq_delete_rc=True)
                        else:
                            return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict, faq_delete_rc=False)
                    else:
                        return render_template(self.nas_add_faq_html_template, faq_dict=self.faq_dict, faq_selected=False)
            else:
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
                if category_faq_dict.pop(faq_to_delete_value, None) is not None:
                    container_status_app.logger.info("FAQ {} in Category {} has been deleted.".format(
                        faq_to_delete_value, faq_delete_metadata_list[0].upper()))
                    faqs_deleted = True
                else:
                    container_status_app.logger.warning("FAQ {} in Category {} not found.".format(
                        faq_to_delete_value, faq_delete_metadata_list[0].upper()))
                    faqs_deleted = False

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

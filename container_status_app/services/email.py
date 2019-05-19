import os
# import smtplib
# from email.message import EmailMessage
from flask_mail import Message
from flask import current_app as container_status_app
from container_status_app.common.common import Common
from werkzeug.utils import secure_filename
# from decorators import async_thread


class EmailServices(object):
    def __init__(self, subject, from_address: str, to_address: list):
        """
        Encapsulates ability to send email using USCC mail server
        """
        # self.message_object = EmailMessage()
        # self.mail_server_url = "Corpmta.uscc.com"
        # self.mail_server_port = 25
        self.subject = subject
        self.from_address = from_address
        self.to_address = to_address

    # @async_thread
    # def send_async_email(self, msg):
    #     with container_status_app.app_context():
    #         container_status_app.extensions.get('mail').send(msg)

    def send_email(self, email_content: str, subject: str = None, from_address: str = None, to_address: list = None,
                   attachment=None):
        """

        :param email_content: data to be put in the body of the email.
        :param subject: option to override class attribute if needed
        :param from_address: option to override class attribute if needed
        :param list to_address: option to override class attribute if needed
        :param attachment: werkzeug.datastructures.FileStorage object from the request.files object
        :return: True/False
        """

        if subject is None:
            subject = self.subject
        if from_address is None:
            if self.from_address is not None:
                from_address = self.from_address
        if to_address is None:
            to_address = self.to_address

        if from_address is not None:
            msg = Message(subject, sender=from_address, recipients=to_address)
        else:
            msg = Message(subject, recipients=to_address)
        msg.body = email_content
        # msg.html = email_content
        if attachment is not None:
            with open(os.path.join(container_status_app.config.get('UPLOAD_FOLDER'), secure_filename(attachment.filename))) as fp:
                msg.attach(filename=attachment.filename, content_type=attachment.content_type, data=fp.read())
        try:
            container_status_app.extensions.get('mail').send(msg)
        except AssertionError as ae:
            Common.create_flash_message('Error: ' + str(ae), category_request='error')
            return False
        # self.message_object['Subject'] = subject
        # # msg['From'] = 'SA3CoreAutomationTeam@noreply.com'
        # self.message_object['From'] = from_address
        # self.message_object['To'] = to_address
        # mail_server = smtplib.SMTP(self.mail_server_url, self.mail_server_port)
        # send_resp = mail_server.send_message(self.message_object)
        # if len(send_resp) == 0:
        #     return True
        # else:
        #     self._logger.error(str(send_resp))
        #     return False
        return True

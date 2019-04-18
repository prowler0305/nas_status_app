import smtplib
import logging
from email.message import EmailMessage
from flask import current_app as container_status_app


class EmailServices(object):
    def __init__(self, subject, from_address, to_address):
        """
        Encapsulates ability to send email using USCC mail server
        """
        self.message_object = EmailMessage()
        self.mail_server_url = "Corpmta.uscc.com"
        self.mail_server_port = 25
        self.subject = subject
        self.from_address = from_address
        self.to_address = to_address

    def send_email(self, email_content: str, subject=None, from_address=None, to_address=None):
        """

        :param email_content: data to be put in the body of the email.
        :param subject: option to override class attribute if needed
        :param from_address: option to override class attribute if needed
        :param to_address: option to override class attribute if needed
        :return: True/False
        """
        self.message_object.set_content(email_content)
        if subject is None:
            subject = self.subject
        if from_address is None:
            from_address = self.from_address
        if to_address is None:
            to_address = self.to_address

        self.message_object['Subject'] = subject
        # msg['From'] = 'SA3CoreAutomationTeam@noreply.com'
        self.message_object['From'] = from_address
        self.message_object['To'] = to_address
        mail_server = smtplib.SMTP(self.mail_server_url, self.mail_server_port)
        send_resp = mail_server.send_message(self.message_object)
        if len(send_resp) == 0:
            return True
        else:
            container_status_app.logger.error(str(send_resp))
            return False

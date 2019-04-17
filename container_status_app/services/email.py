import smtplib
import logging
from email.message import EmailMessage
from flask_mail import Message
import container_status_app


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
        self._logger = logging.getLogger('container_status_app')

    def send_email(self, email_content: str, subject: str = None, from_address: str = None, to_address: list = None,
                   attachment: str = None):
        """

        :param email_content: data to be put in the body of the email.
        :param subject: option to override class attribute if needed
        :param from_address: option to override class attribute if needed
        :param list to_address: option to override class attribute if needed
        :param attachment: Path to a file to attach to the email
        :return: True/False
        """

        # self.message_object.set_content(email_content)
        if subject is None:
            subject = self.subject
        if from_address is None:
            from_address = self.from_address
        if to_address is None:
            to_address = self.to_address

        msg = Message(subject, sender=from_address, recipients=to_address)
        msg.body = email_content
        if attachment is not None:
            with open(attachment) as fp:
                msg.attach("example.txt", "image/png", fp.read())
        container_status_app.mail.send(msg)
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

# Flask
from flask import render_template, redirect, request, url_for
from flask.views import MethodView

# USCC
from common.common import Common

# Misc
import json
import os
from services.email import EmailServices


class ContainerStatus(MethodView):
    def __init__(self):

        self.container_status_dict = None
        self.nas_down_email = dict(subject='NAS Automation Platform Outage',
                                   from_addr='SA3CoreAutomationTeam@noreply.com',
                                   to_addr='Andrew.Spear@uscellular.com',
                                   content='There will be an outage with the NAS Automation Platform on Saturday')

    def get(self):
        """

        :return: Renders the html page with all substituted content needed.
        """

        with open(os.environ.get('container_status_path')) as csfh:
            self.container_status_dict = json.load(csfh)

        if request.url_rule.rule == '/nas_status':
            email = EmailServices(subject=self.nas_down_email.get('subject'),
                                  from_address=self.nas_down_email.get('from_addr'),
                                  to_address=self.nas_down_email.get('to_addr'))
            email.send_email(self.nas_down_email.get('content'))

            if 'nas_production' in self.container_status_dict:
                return render_template('container_status/nas_prod_status.html', cs=self.container_status_dict.get('nas_production'))
            else:
                return render_template('container_status/nas_prod_status.html')

        return render_template('container_status/container_status.html', cs=self.container_status_dict)



# from email.mime.multipart import MIMEMultipart
# import smtplib
# msg = MIMEMultipart()
# msg['Subject'] = 'Email from Python code Test'
# msg['From'] = 'SA3CoreAutomationTeam@noreply.com'
# msg['To'] = 'Andrew.Spear@uscellular.com'
# msg.preamble = 'Email from Python code Test'
# server = smtplib.SMTP('Corpmta.uscc.com', 25)
# server.sendmail('SA3CoreAutomationTeam@noreply.com', 'Andrew.Spear@uscellular.com', msg.as_string())

# import smtplib
# from email.message import EmailMessage
# msg = EmailMessage()
# msg.set_content("NAS Platform will be down")
# msg['Subject'] = "NAS Platform Status"
# msg['From'] = 'SA3CoreAutomationTeam@noreply.com'
# msg['To'] = 'Andrew.Spear@uscellular.com'
# server = smtplib.SMTP('Corpmta.uscc.com', 25)
# server.send_message(msg)
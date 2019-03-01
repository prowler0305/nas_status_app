import smtplib
from email.message import EmailMessage

class EmailServices():

msg = EmailMessage()
msg.set_content("NAS Platform will be down")
msg['Subject'] = "NAS Platform Status"
msg['From'] = 'SA3CoreAutomationTeam@noreply.com'
msg['To'] = 'Andrew.Spear@uscellular.com'
server = smtplib.SMTP('Corpmta.uscc.com', 25)
server.send_message(msg)
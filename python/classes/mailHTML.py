import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

class MailHTML:
    def __init__(self, host='smheb.essos.lan', fromaddr='python@alphasia.com', toaddrs='c.leblond@agelia.com'):
        print("emai : =>>>>>>>>>>>>>>>>>>>>")
        self.in_plaintext = "erreur de python"
        self.in_subject = "[ERROR PYTHON][Intern] site : "
        self.host = host
        self.fromAdrr = fromaddr
        self.toAdrrs = toaddrs

    def set_message(self, in_plaintext="Aucun", in_subject="Aucun"):
        """
        Creates the MIME message to be sent by e-mail. Optionally allows adding subject and 'from' field. Sets up empty recipient fields. To use html messages specify an htmltext input

        :param in_plaintext: Plaintext email body (required even when HTML message is specified, as fallback)
        :param in_subject: Subject line (optional)
        """
        self.in_subject = in_subject
        self.in_plaintext = in_plaintext

    def send_all(self):
        print("emai : =>>>>>>>>>>>>>>>>>>>>"+self.in_plaintext['date'])
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.in_subject
        msg['From'] = self.fromAdrr
        msg['To'] = self.toAdrrs
        message_trace = ""

        for traceback in self.in_plaintext['traceback']:
            msg_traceback = "{0}".format(traceback).replace("<", "").replace(">", "")
            message_trace = message_trace + "<tr><td>Traceback</td><td>{0}</td></tr>".format(msg_traceback[13:])

        for stack in self.in_plaintext['stack']:
            msg_stack = "{0}".format(stack).replace("<", "").replace(">", "")
            message_trace = message_trace + "<tr><td>stack</td><td>{0}</td></tr>".format(msg_stack[13:])

        i = 0
        message_trace = message_trace + "<tr><td>CPU utilisé</td><td>"
        for cpu in self.in_plaintext['cpu']:
            i = i+1
            message_trace = message_trace + " cpu{0} : {1}%".format(i, cpu)
        message_trace = message_trace + "</td></tr>"

        message_trace = message_trace + "<tr><td>Mémoire utilisée</td><td>{0} %</td></tr>".format(self.in_plaintext['memory'].percent)
        message_trace = message_trace + "<tr><td>Disque utilisé</td><td>{0} %</td></tr>".format(
            self.in_plaintext['disk'].percent)

        message_trace = message_trace + "<tr><td>Réseaux</td><td>{0} %</td></tr>".format(
            self.in_plaintext['network'])


        # Create the body of the message (a plain-text and an HTML version).
        text = "/!\ Une erreur a été détectée sur le site. /!\\nVoici ses informations :"
        html = """\
        <html>
          <head></head>
          <body>
            <p>/!\ Une erreur a été détectée sur le site. /!\<br>Voici ses informations :</p>

            <style type="text/css">
.tftable {font-size:12px;color:#333333;width:100%;border-width: 1px;border-color: #729ea5;border-collapse: collapse;}
.tftable th {font-size:12px;background-color:#acc8cc;border-width: 1px;padding: 8px;border-style: solid;border-color: #729ea5;text-align:left;}
.tftable tr {background-color:#d4e3e5;}
.tftable td {font-size:12px;border-width: 1px;padding: 8px;border-style: solid;border-color: #729ea5;}
.tftable tr:hover {background-color:#ffffff;}
</style>

<table class="tftable" border="1">
<tr><th>Objet</th><th>Détail</th></tr>
<tr><td>Date</td><td>"""+self.in_plaintext['date']+"""</td></tr>
<tr><td>Date</td><td>"""+self.in_plaintext['server']+"""</td></tr>
<tr><td>Message</td><td>"""+self.in_plaintext['message'] +""""</td></tr>"""+ message_trace +""""
</table>


          </body>
        </html>
        """

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        try:
            server = smtplib.SMTP('smheb.essos.lan')
            server.set_debuglevel(1)
            server.sendmail(self.fromAdrr, self.toAdrrs, msg.as_string())
            server.quit()
        except smtplib.SMTPException:
            print("Error: unable to send email")
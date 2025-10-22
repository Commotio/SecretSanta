import os
import ssl
import smtplib
import mimetypes
import configparser
from email.message import EmailMessage

def create_message(sender, receiver, subject, body, html=None, attachments=None):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject

    # Text and HTML versions
    if html:
        msg.set_content(body)
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(body)

    # Optional attachments
    if attachments:
        for path in attachments:
            ctype, encoding = mimetypes.guess_type(path)
            maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
            with open(path, "rb") as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(path))
    return msg


def send_email(config_path="config.ini", receiver=None, html_template=None, body_override=None):
    config = configparser.ConfigParser()
    with open("config.ini", "r", encoding="utf-8") as f:
        config.read_file(f)
    email_conf = config["email"]

    smtp_server = email_conf.get("smtp_server", "smtp.gmail.com")
    port = email_conf.getint("port", 465)
    sender = email_conf.get("sender_email")
    password = email_conf.get("password")
    subject = email_conf.get("subject", "Your Secret Santa Assignment!")

    # Load body
    if body_override:
        text_body = body_override
        html_body = html_template
    elif html_template and os.path.exists(html_template):
        with open(html_template, "r", encoding="utf-8") as f:
            html_body = f.read()
        text_body = "Your Secret Santa assignments are ready!"
    else:
        html_body = None
        text_body = "Your Secret Santa assignments are ready!"

    # Create the message
    msg = create_message(sender, receiver, subject, text_body, html_body)

    # Send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        server.send_message(msg)
from typing import TypedDict

from flask import render_template
from flask_mail import Mail, Message

import app

mail = Mail(app)

class ReportForm(TypedDict):
    person: str
    report: str

def send_opening_mail(email, rider_name, event_name, driver_name, url ) -> None:
    if app.config['MAIL_PROD']:
        recipients = ['<' + email + '>']
        msg = Message(subject='Ride Opening For ' + event_name,
                      sender=app.config.get('MAIL_USERNAME'),
                      recipients=recipients)

        template = 'mail/opening'
        msg.body = render_template(template + '.txt', rider = rider_name, event = event_name, driver = driver_name, url = url)
        msg.html = render_template(template + '.html', rider = rider_name, event = event_name, driver = driver_name, url = url)
        app.logger.info('Sending mail to ' + recipients[0])
        mail.send(msg)

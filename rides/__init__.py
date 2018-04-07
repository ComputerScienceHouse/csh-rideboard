import datetime
import time
import os
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask import Flask, render_template, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Get app config from absolute file path
if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

db = SQLAlchemy(app)

auth = OIDCAuthentication(app,
                          issuer = app.config["OIDC_ISSUER"],
client_registration_info = app.config["OIDC_CLIENT_CONFIG"])


# pylint: disable=wrong-import-position
from rides.models import Ride, Rider, Car
from rides.forms import RideForm, CarForm


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/assets'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
@auth.oidc_auth
def index(auth_dict=None):
    # List of objects from the database
    events = Ride.query.all()
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    for event in events:
        t = datetime.datetime.strftime(event.end_time, '%Y-%m-%d %H:%M:%S')
        if st > t:
            events.remove(event)
    return render_template('index.html', events=events, timestamp=st, datetime=datetime.datetime, auth_dict=auth_dict)

@app.route('/rideform', methods=['GET', 'POST'])
@auth.oidc_auth
def rideform():
    form = RideForm()
    print(form.start_time.data)
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('form.html',form=form)

@app.route("/logout")
@auth.oidc_logout
def _logout():
    return redirect("/", 302)

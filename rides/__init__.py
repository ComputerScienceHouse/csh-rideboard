####################################
# File name: __init__.py           #
# Author: Ayush Goel & Fred Rybin  #
####################################
import datetime
import os
import pytz
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask import Flask, render_template, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Setting up Flask and csrf token for forms.
app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)

# Get app config from absolute file path
if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

db = SQLAlchemy(app)

# OIDC Authentication
CSH_AUTH = ProviderConfiguration(issuer=app.config["OIDC_ISSUER"],
                                 client_metadata=ClientMetadata(
                                     app.config["OIDC_CLIENT_ID"],
                                     app.config["OIDC_CLIENT_SECRET"]))
GOOGLE_AUTH = ProviderConfiguration(issuer=app.config["GOOGLE_ISSUER"],
                                    client_metadata=ClientMetadata(
                                        app.config["GOOGLE_CLIENT_ID"],
                                        app.config["GOOGLE_CLIENT_SECRET"]))
auth = OIDCAuthentication({'default': CSH_AUTH,
                           'google': GOOGLE_AUTH},
                          app)
auth.init_app(app)


# pylint: disable=wrong-import-position
from rides.models import Event, Rider, Car
from rides.forms import EventForm, CarForm
from .utils import csh_user_auth, google_user_auth, latin_to_utf8

# time setup for the server side time
eastern = pytz.timezone('US/Eastern')
fmt = '%Y-%m-%d %H:%M'

# Favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/assets'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/demo')
def demo(auth_dict=None):
    # Get current EST time.
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)
    return render_template('demo.html', timestamp=st, datetime=datetime, auth_dict=auth_dict)

@app.route('/')
def login(auth_dict=None):
    return render_template('login.html', auth_dict=auth_dict)

@app.route('/home')
@auth.oidc_auth('default')
@csh_user_auth
def index(auth_dict=None):
    # Get all the events and current EST time.
    events = Event.query.all()
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)

    rider_instance = []
    if auth_dict is not None:
        for rider_instances in Rider.query.filter(Rider.username == auth_dict['uid']).all():
            rider_instance.append(Car.query.get(rider_instances.car_id).event_id)
        for rider_instances in Car.query.all():
            if rider_instances.username == auth_dict['uid']:
                rider_instance.append(rider_instances.event_id)

    # If any event has expired by 1 hour then expire the event.
    for event in events:
        t = datetime.datetime.strftime((event.end_time + datetime.timedelta(hours=1)), '%Y-%m-%d %H:%M')
        if st > t:
            event.expired = True
            db.session.commit()

    # Query one more time for the display.
    events = Event.query.filter(Event.expired == False).order_by(Event.start_time.asc()).all() #pylint: disable=singleton-comparison
    return render_template('index.html', events=events, timestamp=st, datetime=datetime,
                                         auth_dict=auth_dict, rider_instance=rider_instance)

@app.route('/google')
@auth.oidc_auth('google')
@google_user_auth
def index_google(auth_dict=None):
    # Get all the events and current EST time.
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)
    return render_template('layout.html', timestamp=st, datetime=datetime, auth_dict=auth_dict)

@app.route('/history')
@auth.oidc_auth('default')
@csh_user_auth
def history(auth_dict=None):
    # Get all the events and current EST time.
    events = Event.query.all()
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)
    events = Event.query.filter(Event.expired == True).order_by(Event.start_time.desc()).all() #pylint: disable=singleton-comparison
    return render_template('history.html', events=events, timestamp=st, datetime=datetime,
                                         auth_dict=auth_dict)


# Event Form
@app.route('/eventform', methods=['GET', 'POST'])
@auth.oidc_auth('default')
@csh_user_auth
def eventform(auth_dict=None):
    # Time to prepopulate the datetime field
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)
    form = EventForm()
    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        start_time = datetime.datetime(int(form.start_date_time.data.year),
                                       int(form.start_date_time.data.month),
                                       int(form.start_date_time.data.day),
                                       int(form.start_date_time.data.hour),
                                       int(form.start_date_time.data.minute))
        end_time = datetime.datetime(int(form.end_date_time.data.year),
                                     int(form.end_date_time.data.month),
                                     int(form.end_date_time.data.day),
                                     int(form.end_date_time.data.hour),
                                     int(form.end_date_time.data.minute))
        creator = auth_dict['uid']
        event = Event(name, address, start_time, end_time, creator)
        db.session.add(event)
        db.session.commit()
        infinity = Car('∞', 'Need a Ride', 0, 0, start_time, end_time, "", event.id)
        db.session.add(infinity)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('eventform.html', form=form, timestamp=st, auth_dict=auth_dict)

# Edit event form
@app.route('/edit/eventform/<string:eventid>', methods=['GET', 'POST'])
@auth.oidc_auth('default')
@csh_user_auth
def editeventform(eventid, auth_dict=None):
    username = auth_dict['uid']
    event = Event.query.get(eventid)
    if username == event.creator and event is not None:
        form = EventForm()
        if form.validate_on_submit():
            event.name = form.name.data
            event.address = form.address.data
            event.start_time = datetime.datetime(int(form.start_date_time.data.year),
                                                int(form.start_date_time.data.month),
                                                int(form.start_date_time.data.day),
                                                int(form.start_date_time.data.hour),
                                                int(form.start_date_time.data.minute))
            event.end_time = datetime.datetime(int(form.end_date_time.data.year),
                                              int(form.end_date_time.data.month),
                                              int(form.end_date_time.data.day),
                                              int(form.end_date_time.data.hour),
                                              int(form.end_date_time.data.minute))
            event.creator = auth_dict['uid']
            event.expired = False
            car = Car.query.filter(Car.event_id == eventid).filter(Car.name == "Need a Ride").first()
            car.departure_time = datetime.datetime(int(form.start_date_time.data.year),
                                                int(form.start_date_time.data.month),
                                                int(form.start_date_time.data.day),
                                                int(form.start_date_time.data.hour),
                                                int(form.start_date_time.data.minute))
            car.return_time = datetime.datetime(int(form.end_date_time.data.year),
                                              int(form.end_date_time.data.month),
                                              int(form.end_date_time.data.day),
                                              int(form.end_date_time.data.hour),
                                              int(form.end_date_time.data.minute))
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('editeventform.html', form=form, event=event, auth_dict=auth_dict)

# Car form
@app.route('/carform/<string:eventid>', methods=['GET', 'POST'])
@auth.oidc_auth('default')
@csh_user_auth
def carform(eventid, auth_dict=None):
    form = CarForm()
    event = Event.query.get(eventid)
    if form.validate_on_submit():
        username = auth_dict['uid']
        name = latin_to_utf8(auth_dict['first']+" "+ auth_dict['last'])
        current_capacity = 0
        max_capacity = int(form.max_capacity.data['max_capacity'])
        departure_time = datetime.datetime(int(form.departure_date_time.data.year),
                                           int(form.departure_date_time.data.month),
                                           int(form.departure_date_time.data.day),
                                           int(form.departure_date_time.data.hour),
                                           int(form.departure_date_time.data.minute))
        return_time = datetime.datetime(int(form.return_date_time.data.year),
                                        int(form.return_date_time.data.month),
                                        int(form.return_date_time.data.day),
                                        int(form.return_date_time.data.hour),
                                        int(form.return_date_time.data.minute))
        driver_comment = form.comments.data
        event_id = eventid
        car = Car(username, name, current_capacity, max_capacity, departure_time, return_time, driver_comment, event_id)
        db.session.add(car)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('carform.html', form=form, event=event, auth_dict=auth_dict)

# Edit car form
@app.route('/edit/carform/<string:carid>', methods=['GET', 'POST'])
@auth.oidc_auth('default')
@csh_user_auth
def editcarform(carid, auth_dict=None):
    username = auth_dict['uid']
    car = Car.query.get(carid)
    if username == car.username and car is not None:
        form = CarForm()
        if form.validate_on_submit():
            car.username = auth_dict['uid']
            car.name = latin_to_utf8(auth_dict['first']+" "+ auth_dict['last'])
            car.max_capacity = int(form.max_capacity.data['max_capacity'])
            car.departure_time = datetime.datetime(int(form.departure_date_time.data.year),
                                                   int(form.departure_date_time.data.month),
                                                   int(form.departure_date_time.data.day),
                                                   int(form.departure_date_time.data.hour),
                                                   int(form.departure_date_time.data.minute))
            car.return_time = datetime.datetime(int(form.return_date_time.data.year),
                                                int(form.return_date_time.data.month),
                                                int(form.return_date_time.data.day),
                                                int(form.return_date_time.data.hour),
                                                int(form.return_date_time.data.minute))
            car.driver_comment = form.comments.data
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('editcarform.html', form=form, car=car, auth_dict=auth_dict)

# Join a ride
@app.route('/join/<string:car_id>/<string:user>', methods=["GET"])
@auth.oidc_auth('default')
@csh_user_auth
def join_ride(car_id, user, auth_dict=None):
    incar = False
    username = auth_dict['uid']
    name = latin_to_utf8(auth_dict['first']+" "+ auth_dict['last'])
    car = Car.query.filter(Car.id == car_id).first()
    event = Event.query.filter(Event.id == car.event_id).first()
    attempted_username = user
    if attempted_username == username:
        for c in event.cars:
            if c.username == username:
                incar = True
            for person in c.riders:
                if person.username == username:
                    incar = True
        if (car.current_capacity < car.max_capacity or car.max_capacity == 0) and not incar:
            rider = Rider(username, name, car_id)
            car.current_capacity += 1
            db.session.add(rider)
            db.session.add(car)
            db.session.commit()
    return redirect(url_for('index'))

# Delete Car
@app.route('/delete/car/<string:car_id>', methods=["GET"])
@auth.oidc_auth('default')
@csh_user_auth
def delete_car(car_id, auth_dict=None):
    username = auth_dict['uid']
    car = Car.query.filter(Car.id == car_id).first()
    if car.username == username and car is not None:
        for peeps in car.riders:
            db.session.delete(peeps)
        db.session.delete(car)
        db.session.commit()
    return redirect(url_for('index'))

# Delete Event
@app.route('/delete/ride/<string:event_id>', methods=["GET"])
@auth.oidc_auth('default')
@csh_user_auth
def delete_ride(event_id, auth_dict=None):
    username = auth_dict['uid']
    event = Event.query.filter(Event.id == event_id).first()
    if event.creator == username and event is not None:
        for car in event.cars:
            for peeps in car.riders:
                db.session.delete(peeps)
            db.session.delete(car)
        db.session.delete(event)
        db.session.commit()
    return redirect(url_for('index'))

# Leave a ride
@app.route('/delete/rider/<string:car_id>/<string:rider_username>', methods=["GET"])
@auth.oidc_auth('default')
@csh_user_auth
def leave_ride(car_id, rider_username, auth_dict=None):
    username = auth_dict['uid']
    car = Car.query.filter(Car.id == car_id).first()
    rider = Rider.query.filter(Rider.username == rider_username, Rider.car_id == car_id).first()
    if rider.username == username and rider is not None:
        db.session.delete(rider)
        car.current_capacity -= 1
        db.session.add(car)
        db.session.commit()
    return redirect(url_for('index'))

# Log out
@app.route("/logout")
@auth.oidc_logout
def _logout():
    return redirect("/", 302)

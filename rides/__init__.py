####################################
# File name: __init__.py           #
# Author: Ayush Goel & Fred Rybin  #
####################################
from subprocess import check_output
import datetime
import os
import pytz
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask import Flask, render_template, send_from_directory, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, logout_user, login_required, LoginManager, current_user

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
                                        app.config["GOOGLE_CLIENT_SECRET"]),
                                    auth_request_params={'scope': ['email', 'profile', 'openid']})
auth = OIDCAuthentication({'default': CSH_AUTH,
                           'google': GOOGLE_AUTH},
                          app)
auth.init_app(app)

# Flask-Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Commit
commit = check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').rstrip()


# pylint: disable=wrong-import-position
from rides.models import Event, Rider, Car, User
from rides.forms import EventForm, CarForm
from .utils import csh_user_auth, google_user_auth
from .pings import send_join, send_leave

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


# LOG IN MANAGEMENT


@app.route('/login')
@app.route('/')
def login(auth_dict=None):
    return render_template('login.html', auth_dict=auth_dict)


@login_manager.user_loader
def load_user(user_id):
    q = User.query.get(user_id)
    if q:
        return q
    return None


@app.route("/logout")
@auth.oidc_logout
def _logout():
    logout_user()
    return redirect("/", 302)


@app.route('/csh-auth')
@auth.oidc_auth('default')
@csh_user_auth
def csh_auth(auth_dict=None):
    if auth_dict is None:
        return redirect(url_for('login'))
    q = User.query.get(auth_dict['uid'])
    if q is not None:
        g.user = q
        q.firstname = auth_dict['first']
        q.lastname = auth_dict['last']
        q.picture = auth_dict['picture']
    else:
        user = User(auth_dict['uid'], auth_dict['first'], auth_dict['last'], auth_dict['picture'])
        g.user = user
        db.session.add(user)

    db.session.commit()
    login_user(g.user)
    return redirect(url_for('index'))

# TODO: Figure out the deal with commit number.
# TODO: Potential conflicts between google id and csh id and other ids.

@app.route('/google-auth')
@auth.oidc_auth('google')
@google_user_auth
def google_auth(auth_dict=None):
    if auth_dict is None:
        return redirect(url_for('login'))
    q = User.query.get(auth_dict['uid'])
    if q is not None:
        q.firstname = auth_dict['first']
        q.lastname = auth_dict['last']
        q.picture = auth_dict['picture']
        g.user = q
    else:
        user = User(auth_dict['uid'], auth_dict['first'], auth_dict['last'], auth_dict['picture'])
        g.user = user
        db.session.add(user)

    db.session.commit()
    login_user(g.user)
    return redirect(url_for('index'))


# Application


@app.route('/home')
@login_required
def index():
    # Get all the events and current EST time.
    events = Event.query.all()
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)

    rider_instance = []
    if current_user.is_authenticated:
        # TODO: Likely don't need this for loop, should be a single query.
        for rider_instances in Rider.query.filter(Rider.username == current_user.id).all():
            rider_instance.append(Car.query.get(rider_instances.car_id).event_id)
        for rider_instances in Car.query.all():
            if rider_instances.username == current_user.id:
                rider_instance.append(rider_instances.event_id)

    # If any event has expired by 1 hour then expire the event.
    for event in events:
        t = datetime.datetime.strftime((event.end_time + datetime.timedelta(hours=1)), '%Y-%m-%d %H:%M')
        if st > t:
            event.expired = True
            db.session.commit()

    # Query one more time for the display.
    events = Event.query.filter(Event.expired == False).order_by(Event.start_time.asc()).all()  # pylint: disable=singleton-comparison
    return render_template('index.html', events=events, timestamp=st, datetime=datetime, rider_instance=rider_instance)


@app.route('/history')
@login_required
def history():
    # Get all the events and current EST time.
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)
    events = Event.query.filter(Event.expired == True).order_by(Event.start_time.desc()).all()  # pylint: disable=singleton-comparison
    return render_template('history.html', events=events, timestamp=st, datetime=datetime)


# Event Form
@app.route('/eventform', methods=['GET', 'POST'])
@login_required
def eventform():
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
        creator = current_user.id
        event = Event(name, address, start_time, end_time, creator)
        db.session.add(event)
        db.session.commit()
        infinity = Car('∞', 'Need a Ride', 0, 0, start_time, end_time, "", event.id)
        db.session.add(infinity)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('eventform.html', form=form, timestamp=st)


# Edit event form
@app.route('/edit/eventform/<string:eventid>', methods=['GET', 'POST'])
@login_required
def editeventform(eventid):
    username = current_user.id
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
            event.creator = current_user.id
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
    return render_template('editeventform.html', form=form, event=event)


# Car form
@app.route('/carform/<string:eventid>', methods=['GET', 'POST'])
@login_required
def carform(eventid):
    form = CarForm()
    event = Event.query.get(eventid)
    if form.validate_on_submit():
        username = current_user.id
        name = current_user.firstname + " " + current_user.lastname
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
    return render_template('carform.html', form=form, event=event)


# Edit car form
@app.route('/edit/carform/<string:carid>', methods=['GET', 'POST'])
@login_required
def editcarform(carid):
    username = current_user.id
    car = Car.query.get(carid)
    if username == car.username and car is not None:
        form = CarForm()
        if form.validate_on_submit():
            car.username = current_user.id
            car.name = current_user.firstname + " " + current_user.lastname
            # TODO: If new capacity is lower, move people.
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
    return render_template('editcarform.html', form=form, car=car)


# Join a ride
@app.route('/join/<string:car_id>/<user>', methods=["POST"])
@login_required
def join_ride(car_id, user):
    incar = False
    username = current_user.id
    name = current_user.firstname + " " + current_user.lastname
    car = Car.query.get(car_id)
    event = Event.query.get(car.event_id)
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
            u = User.query.get(username)
            user_str = f"{u.firstname} {u.lastname}"
            event = Event.query.get(car.event_id)
            # if the first character if the username is a digit, it is not a csh user
            if not u.id[0].isdigit():
                user_str += f" (@{username})"
            if user_str[0] == "@":
                user_str = user_str[1:]
            send_join(car.username, user_str, event.name)
    return redirect(url_for('index'))


# Delete Car
@app.route('/delete/car/<string:car_id>', methods=["POST"])
@login_required
def delete_car(car_id):
    username = current_user.id
    car = Car.query.get(car_id)
    if car.username == username and car is not None:
        for peeps in car.riders:
            # TODO: Add peeps to need ride.
            db.session.delete(peeps)
        db.session.delete(car)
        db.session.commit()
    return redirect(url_for('index'))


# Delete Event
@app.route('/delete/ride/<string:event_id>', methods=["POST"])
@login_required
def delete_ride(event_id):
    username = current_user.id
    event = Event.query.get(event_id)
    if event.creator == username and event is not None:
        for car in event.cars:
            for peeps in car.riders:
                db.session.delete(peeps)
            db.session.delete(car)
        db.session.delete(event)
        db.session.commit()
    return redirect(url_for('index'))


# Leave a ride
@app.route('/delete/rider/<string:car_id>/<string:rider_username>', methods=["POST"])
@login_required
def leave_ride(car_id, rider_username):
    username = current_user.id
    car = Car.query.get(car_id)
    rider = Rider.query.filter(Rider.username == rider_username, Rider.car_id == car_id).first()
    if rider.username == username and rider is not None:
        db.session.delete(rider)
        car.current_capacity -= 1
        db.session.add(car)
        db.session.commit()
        u = User.query.get(username)
        user_str = f"{u.firstname} {u.lastname}"
        event = Event.query.get(car.event_id)
        # if the first character if the username is a digit, it is not a csh user
        if not u.id[0].isdigit():
            user_str += f" (@{username})"
        if user_str[0] == "@":
            user_str = user_str[1:]
        send_leave(car.username, user_str, event.name)
    return redirect(url_for('index'))

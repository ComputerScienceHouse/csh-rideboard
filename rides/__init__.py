####################################
# File name: __init__.py           #
# Author: Ayush Goel & Fred Rybin  #
####################################
import datetime
import os
import pytz
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask import Flask, render_template, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Setting up Flask and csrf token for forms.
app = Flask(__name__)
csrf = CSRFProtect(app)

# Get app config from absolute file path
if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

db = SQLAlchemy(app)

# OIDC Authentication, for CSH member login.
auth = OIDCAuthentication(app, issuer=app.config["OIDC_ISSUER"],
client_registration_info=app.config["OIDC_CLIENT_CONFIG"])

# pylint: disable=wrong-import-position
from rides.models import Ride, Rider, Car
from rides.forms import RideForm, CarForm
from .utils import user_auth

# time setup for the server side time
eastern = pytz.timezone('US/Eastern')
fmt = '%Y-%m-%d %H:%M'

# Favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/assets'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Home page without authentication.
@app.route('/')
def index(auth_dict=None):
    # If user has logged in before then redirect them to home page.
    if 'userinfo' in session:
        return redirect(url_for('index_auth'))

    # Get current EST time.
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)

    events = []
    return render_template('index.html', events=events, timestamp=st, datetime=datetime, auth_dict=auth_dict)

# Home page with auth
@app.route('/home')
@auth.oidc_auth
@user_auth
def index_auth(auth_dict=None):
    # Get all the events and current EST time.
    events = Ride.query.all()
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)

    rider_instance = []
    for rider_instances in Rider.query.filter(Rider.username == auth_dict['uid']).all():
        rider_instance.append(Car.query.get(rider_instances.car_id).ride_id)
    for rider_instances in Car.query.all():
        if rider_instances.username == auth_dict['uid']:
            rider_instance.append(rider_instances.ride_id)

    # If any event has expired by 1 hour then delete the event.
    for event in events:
        t = datetime.datetime.strftime((event.end_time + datetime.timedelta(hours=1)), '%Y-%m-%d %H:%M')
        if st > t:
            for car in event.cars:
                for peeps in car.riders:
                    db.session.delete(peeps)
                db.session.delete(car)
            db.session.delete(event)
            db.session.commit()

    # Query one more time for the display.
    events = Ride.query.order_by(Ride.start_time.asc()).all()
    return render_template('index.html', events=events, timestamp=st, datetime=datetime,
                                         auth_dict=auth_dict, rider_instance=rider_instance)

# Event Form
@app.route('/rideform', methods=['GET', 'POST'])
@auth.oidc_auth
@user_auth
def rideform(auth_dict=None):
    # Time to prepopulate the datetime field
    loc_dt = datetime.datetime.now(tz=eastern)
    st = loc_dt.strftime(fmt)
    form = RideForm()
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
        ride = Ride(name, address, start_time, end_time, creator)
        db.session.add(ride)
        db.session.commit()
        infinity = Car('∞', 'Need a Ride', 0, 0, start_time, end_time, "", ride.id)
        db.session.add(infinity)
        db.session.commit()
        return redirect(url_for('index_auth'))
    return render_template('rideform.html', form=form, timestamp=st, auth_dict=auth_dict)

# Edit event form
@app.route('/edit/rideform/<string:rideid>', methods=['GET', 'POST'])
@auth.oidc_auth
@user_auth
def editrideform(rideid, auth_dict=None):
    username = auth_dict['uid']
    ride = Ride.query.get(rideid)
    if username == ride.creator and ride is not None:
        form = RideForm()
        if form.validate_on_submit():
            ride.name = form.name.data
            ride.address = form.address.data
            ride.start_time = datetime.datetime(int(form.start_date_time.data.year),
                                                int(form.start_date_time.data.month),
                                                int(form.start_date_time.data.day),
                                                int(form.start_date_time.data.hour),
                                                int(form.start_date_time.data.minute))
            ride.end_time = datetime.datetime(int(form.end_date_time.data.year),
                                              int(form.end_date_time.data.month),
                                              int(form.end_date_time.data.day),
                                              int(form.end_date_time.data.hour),
                                              int(form.end_date_time.data.minute))
            ride.creator = auth_dict['uid']
            car = Car.query.filter(Car.ride_id == rideid).filter(Car.name == "Need a Ride").first()
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
            return redirect(url_for('index_auth'))
    return render_template('editrideform.html', form=form, ride=ride, auth_dict=auth_dict)

# Car form
@app.route('/carform/<string:rideid>', methods=['GET', 'POST'])
@auth.oidc_auth
@user_auth
def carform(rideid, auth_dict=None):
    form = CarForm()
    ride = Ride.query.get(rideid)
    if form.validate_on_submit():
        username = auth_dict['uid']
        name = auth_dict['first']+" "+ auth_dict['last']
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
        ride_id = rideid
        car = Car(username, name, current_capacity, max_capacity, departure_time, return_time, driver_comment, ride_id)
        db.session.add(car)
        db.session.commit()
        return redirect(url_for('index_auth'))
    return render_template('carform.html', form=form, ride=ride, auth_dict=auth_dict)

# Edit car form
@app.route('/edit/carform/<string:carid>', methods=['GET', 'POST'])
@auth.oidc_auth
@user_auth
def editcarform(carid, auth_dict=None):
    username = auth_dict['uid']
    car = Car.query.get(carid)
    if username == car.username and car is not None:
        form = CarForm()
        if form.validate_on_submit():
            car.username = auth_dict['uid']
            car.name = auth_dict['first']+" "+ auth_dict['last']
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
            return redirect(url_for('index_auth'))
    return render_template('editcarform.html', form=form, car=car, auth_dict=auth_dict)

# Join a ride
@app.route('/join/<string:car_id>/<string:user>', methods=["GET"])
@auth.oidc_auth
@user_auth
def join_ride(car_id, user, auth_dict=None):
    incar = False
    username = auth_dict['uid']
    name = auth_dict['first']+" "+ auth_dict['last']
    car = Car.query.filter(Car.id == car_id).first()
    event = Ride.query.filter(Ride.id == car.ride_id).first()
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
    return redirect(url_for('index_auth'))

# Delete Car
@app.route('/delete/car/<string:car_id>', methods=["GET"])
@auth.oidc_auth
@user_auth
def delete_car(car_id, auth_dict=None):
    username = auth_dict['uid']
    car = Car.query.filter(Car.id == car_id).first()
    if car.username == username and car is not None:
        for peeps in car.riders:
            db.session.delete(peeps)
        db.session.delete(car)
        db.session.commit()
    return redirect(url_for('index_auth'))

# Delete Event
@app.route('/delete/ride/<string:ride_id>', methods=["GET"])
@auth.oidc_auth
@user_auth
def delete_ride(ride_id, auth_dict=None):
    username = auth_dict['uid']
    ride = Ride.query.filter(Ride.id == ride_id).first()
    if ride.creator == username and ride is not None:
        for car in ride.cars:
            for peeps in car.riders:
                db.session.delete(peeps)
            db.session.delete(car)
        db.session.delete(ride)
        db.session.commit()
    return redirect(url_for('index_auth'))

# Leave a ride
@app.route('/delete/rider/<string:car_id>/<string:rider_username>', methods=["GET"])
@auth.oidc_auth
@user_auth
def leave_ride(car_id, rider_username, auth_dict=None):
    username = auth_dict['uid']
    car = Car.query.filter(Car.id == car_id).first()
    rider = Rider.query.filter(Rider.username == rider_username, Rider.car_id == car_id).first()
    if rider.username == username and rider is not None:
        db.session.delete(rider)
        car.current_capacity -= 1
        db.session.add(car)
        db.session.commit()
    return redirect(url_for('index_auth'))

# Log out
@app.route("/logout")
@auth.oidc_logout
def _logout():
    return redirect("/", 302)

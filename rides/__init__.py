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

auth = OIDCAuthentication(app, issuer=app.config["OIDC_ISSUER"],
client_registration_info=app.config["OIDC_CLIENT_CONFIG"])


# pylint: disable=wrong-import-position
from rides.models import Ride, Rider, Car
from rides.forms import RideForm, CarForm
from .utils import user_auth


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/assets'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
@app.route('/home')
@auth.oidc_auth
@user_auth
def index(auth_dict=None):
    # List of objects from the database
    events = Ride.query.all()
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    for event in events:
        t = datetime.datetime.strftime(event.end_time, '%Y-%m-%d %H:%M:%S')
        print("ST: " + st + " t:" + t)
        if st > t:
            events.remove(event)
    return render_template('index.html', events=events, timestamp=st, datetime=datetime.datetime, auth_dict=auth_dict)


@app.route('/rideform', methods=['GET', 'POST'])
@auth.oidc_auth
@user_auth
def rideform(auth_dict=None):
    form = RideForm()
    print(form.start_date.data)
    print(form.start_time.data)
    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        start_time = datetime.datetime(int(form.start_date.data['year']),
                                       int(form.start_date.data['month']),
                                       int(form.start_date.data['day']), int(form.start_time.data['hour']),
                                       int(form.start_time.data['minute']))
        end_time = datetime.datetime(int(form.end_date.data['year']),
                                     int(form.end_date.data['month']),
                                     int(form.end_date.data['day']),
                                     int(form.end_time.data['hour']),
                                     int(form.end_time.data['minute']))
        creator = auth_dict['uid']
        ride = Ride(name, address, start_time, end_time, creator)
        db.session.add(ride)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('rideform.html', form=form, auth_dict=auth_dict)


@app.route('/carform/<string:rideid>', methods=['GET', 'POST'])
@auth.oidc_auth
@user_auth
def carform(rideid, auth_dict=None):
    form = CarForm()
    if form.validate_on_submit():
        username = auth_dict['uid']
        name = auth_dict['first']+" "+ auth_dict['last']
        current_capacity = 0
        max_capacity = form.max_capacity.data
        departure_time = datetime.datetime(int(form.departure_date.data['year']),
                                           int(form.departure_date.data['month']),
                                           int(form.departure_date.data['day']),
                                           int(form.departure_time.data['hour']),
                                           int(form.departure_time.data['minute']))
        return_time = datetime.datetime(int(form.return_date.data['year']),
                                        int(form.return_date.data['month']),
                                        int(form.return_date.data['day']),
                                        int(form.return_time.data['hour']),
                                        int(form.return_time.data['minute']))
        driver_comment = form.comments.data
        ride_id = rideid
        car = Car(username, name, current_capacity, max_capacity, departure_time, return_time, driver_comment, ride_id)
        db.session.add(car)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('carform.html', form=form, auth_dict=auth_dict)


@app.route('/join/<string:car_id>/<string:user>', methods=["GET"])
@auth.oidc_auth
@user_auth
def join_ride(car_id, user, auth_dict=None):
    incar = False
    username = auth_dict['uid']
    name = auth_dict['first']+" "+ auth_dict['last']
    car = Car.query.filter(Car.id == car_id).first()
    attempted_username = user
    if attempted_username == username:
        for person in car.riders:
            if person.username == username:
                incar = True
        if car.current_capacity < car.max_capacity and not incar:
            rider = Rider(username, name, car_id)
            car.current_capacity += 1
            db.session.add(rider)
            db.session.add(car)
            db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/car/<string:car_id>', methods=["GET"])
@auth.oidc_auth
@user_auth
def delete_car(car_id, auth_dict=None):
    username = auth_dict['uid']
    car = Car.query.filter(Car.id == car_id).first()
    if car.username == username:
        for peeps in car.riders:
            db.session.delete(peeps)
        db.session.delete(car)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/ride/<string:ride_id>', methods=["GET"])
@auth.oidc_auth
@user_auth
def delete_ride(ride_id, auth_dict=None):
    username = auth_dict['uid']
    ride = Ride.query.filter(Ride.id == ride_id).first()
    if ride.creator == username:
        for car in ride.cars:
            for peeps in car.riders:
                db.session.delete(peeps)
            db.session.delete(car)
        db.session.delete(ride)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/rider/<string:car_id>/<string:rider_username>', methods=["GET"])
@auth.oidc_auth
@user_auth
def leave_ride(car_id, rider_username, auth_dict=None):
    username = auth_dict['uid']
    car = Car.query.filter(Car.id == car_id).first()
    rider = Rider.query.filter(Rider.username == rider_username, Rider.car_id == car_id).first()
    if rider.username == username:
        db.session.delete(rider)
        car.current_capacity -= 1
        db.session.add(car)
        db.session.commit()
    return redirect(url_for('index'))


@app.route("/logout")
@auth.oidc_logout
def _logout():
    return redirect("/", 302)

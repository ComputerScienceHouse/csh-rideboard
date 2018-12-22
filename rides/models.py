####################################
# File name: models.py             #
# Author: Fred Rybin               #
####################################
from rides import db

class Ride(db.Model):
    __tablename__ = 'rides'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    creator = db.Column(db.String(50), nullable=False)
    expired = db.Column(db.Boolean, default=False, nullable=False)
    cars = db.relationship('Car', backref='rides', lazy=True)

    def __init__(self, name, address, start_time, end_time, creator):
        self.name = name
        self.address = address
        self.start_time = start_time
        self.end_time = end_time
        self.creator = creator

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    current_capacity = db.Column(db.Integer, nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    return_time = db.Column(db.DateTime, nullable=False)
    driver_comment = db.Column(db.Text)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    riders = db.relationship('Rider', backref='cars', lazy=True)

    def __init__(self, username, name, current_capacity, max_capacity,
         departure_time, return_time, driver_comment, ride_id):
        self.username = username
        self.name = name
        self.current_capacity = current_capacity
        self.max_capacity = max_capacity
        self.departure_time = departure_time
        self.return_time = return_time
        self.driver_comment = driver_comment
        self.ride_id = ride_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Rider(db.Model):
    __tablename__ = 'riders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)

    def __init__(self, username, name, car_id):
        self.username = username
        self.name = name
        self.car_id = car_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

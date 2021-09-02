####################################
# File name: models.py             #
# Author: Ayush Goel & Fred Rybin  #
####################################
from rides import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String, primary_key=True)         # TODO: Refactor ID.
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    picture = db.Column(db.String, nullable=False)
    slack = db.Column(db.String, nullable=False) # ADD TO MYSQL
    email = db.Column(db.String, nullable=False) # ADD TO MYSQL

    def __init__(self, id, firstname, lastname, picture, slack, email):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.picture = picture
        self.slack = slack
        self.email = email

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def get_id(self):
        return self.id

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    creator = db.Column(db.String(50), nullable=False)
    expired = db.Column(db.Boolean, default=False, nullable=False)
    cars = db.relationship('Car', backref='events', lazy=True)

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
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    riders = db.relationship('Rider', backref='cars', lazy=True)

    def __init__(self, username, name, current_capacity, max_capacity,
         departure_time, return_time, driver_comment, event_id):
        self.username = username
        self.name = name
        self.current_capacity = current_capacity
        self.max_capacity = max_capacity
        self.departure_time = departure_time
        self.return_time = return_time
        self.driver_comment = driver_comment
        self.event_id = event_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Rider(db.Model):
    __tablename__ = 'riders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    slack = db.Column(db.String, nullable=False) # ADD TO MYSQL
    email = db.Column(db.String, nullable=False) # ADD TO MYSQL

    def __init__(self, username, name, car_id, slack, email):
        self.username = username
        self.name = name
        self.car_id = car_id
        self.slack = slack
        self.email = email

    def __repr__(self):
        return '<id {}>'.format(self.id)

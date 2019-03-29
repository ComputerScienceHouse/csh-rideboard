####################################
# File name: models.py             #
# Author: Ayush Goel & Fred Rybin  #
####################################
from rides import db


class BucketEvent(db.Model):
    __tablename__ = 'bucketevent'

    bucket_id = db.Column(db.Integer, db.ForeignKey('bucket.id'), nullable=False, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, primary_key=True)

    def __init__(self, bucket_id, event_id):
        self.event_id = event_id
        self.bucket_id = bucket_id


class UserBucket(db.Model):
    __tablename__ = 'userbucket'

    bucket_id = db.Column(db.Integer, db.ForeignKey('bucket.id'), nullable=False, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False, primary_key=True)

    def __init__(self, bucket_id, user_id):
        self.user_id = user_id
        self.bucket_id = bucket_id


class Bucket(db.Model):
    __tablename__ = 'bucket'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    owner = db.Column(db.String(50), nullable=False)

    def __init__(self, id, title, owner):
        self.id = id
        self.title = title
        self.owner = owner

    def __repr__(self):
        return '<id {}>'.format(self.id)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String, primary_key=True)         # TODO: Refactor ID.
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    picture = db.Column(db.String, nullable=False)

    def __init__(self, id, firstname, lastname, picture):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.picture = picture

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
    bucket_id = db.Column(db.Integer, db.ForeignKey('bucket.id'), nullable=False)
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

    def __init__(self, username, name, car_id):
        self.username = username
        self.name = name
        self.car_id = car_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

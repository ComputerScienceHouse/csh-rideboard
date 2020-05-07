####################################
# File name: models_db.py             #
# Author: Ayush Goel               #
####################################
import uuid

from rides import db
from sqlalchemy.dialects.postgresql import UUID


class UserTeam(db.Model):
    __tablename__ = 'userteam'

    team_id = db.Column(db.Integer, db.ForeignKey(
        'team.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(
        'user.id'), nullable=False, primary_key=True)
    # is_admin

    def __init__(self, team_id, user_id):
        self.user_id = user_id
        self.team_id = team_id


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String, primary_key=True)
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


class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    # description
    token = db.Column(UUID(as_uuid=True), default=uuid.uuid4,
                      unique=True, nullable=False)
    owner = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    sharing = db.Column(db.Boolean, default=False, nullable=False)
    members = db.relationship("User", secondary=UserTeam.__tablename__,
                              backref=db.backref('teams'), lazy='dynamic')

    def __init__(self, title, owner, sharing=False):
        self.title = title
        self.owner = owner
        self.sharing = sharing

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Passenger(db.Model):
    # TODO: This should just be a car.id and user.id table.
    __tablename__ = 'passengers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey(
        'cars.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, username, name, car_id):
        self.username = username
        self.name = name
        self.car_id = car_id

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.id'), nullable=False) # TODO: Make foreign key to User
    name = db.Column(db.String(50), nullable=False)
    current_capacity = db.Column(db.Integer, nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    return_time = db.Column(db.DateTime, nullable=False)
    driver_comment = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey(
        'events.id', ondelete='CASCADE'), nullable=False)
    passengers = db.relationship(
        "Passenger", backref='cars', cascade="all,delete", lazy='dynamic')

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


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.Integer, db.ForeignKey(
        'team.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    creator = db.Column(db.String(50), nullable=False)
    expired = db.Column(db.Boolean, default=False, nullable=False)
    cars = db.relationship("Car", cascade="all,delete", lazy='dynamic')

    def __init__(self, name, address, start_time, end_time, creator, team_id):
        self.name = name
        self.address = address
        self.start_time = start_time
        self.end_time = end_time
        self.creator = creator
        self.team_id = team_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

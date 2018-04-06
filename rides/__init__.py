import os
from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Get app config from absolute file path
if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

db = SQLAlchemy(app)

# pylint: disable=wrong-import-position
from rides.models import Ride, Rider, Car

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/assets'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def hello_world():
    # List of objects from the database
    events = Ride.query.all()
    return render_template('index.html', events=events)

# RideBoard

RideBoard is CSH service that allows the members to carpool, allowing those that do not have a car to participate in events.

[![Travis](https://travis-ci.org/ag-ayush/rides.svg?branch=master)](https://travis-ci.org/ag-ayush/rideboard)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/ag-ayush/rideboard/blob/master/LICENSE)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/ag-ayush/rideboard/issues)

## Contributing
All contributors are welcome! If you would like to contribute:

### Dependencies
1. You will need `python3` ([Install Guide](https://docs.python-guide.org/starting/installation/#installation-guides)).
2. You will need `pip` ([Install Guide](https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line)).
3. And lastly you will need to install `virtualenv` by running `pip install virtualenv`.

### Setup
1. Fork this repo and clone it locally by running `git clone https://github.com/<your_username>/rideboard.git`
2. `cd rides/`
2. Create a python virtual environment, activate it and install requirements.
  - `virtualenv rides-venv`
  - `source rides-venv/bin/activate`
  - `pip install -r requirements.txt`
5. You will need the _LDAP DN_, _LDAP PW_, _MySQL Databse_, and _OIDC Secret_. You can create your own if you are hosting your own application or ask me for these if you would like to contribute to CSH.
```
export SERVER_NAME=127.0.0.1:8080
export IP=127.0.0.1
export PORT=8080
export SQLALCHEMY_DATABASE_URI=postgresql://<LDAP DN>:<LDAP PW>@<MySQL Database>
export OIDC_CLIENT_SECRET=<OIDC Secret>
```
6. To run the application:
  - Set debug mode: `export FLASK_ENV=development`
  - Export application: `export FLASK_APP=app.py`
  - Run: `flask run`
7. Now you can make your changes. Make sure the changes made work and that your code passes pylint (run `pylint rides/`). Once you do that you can make your pullrequest.

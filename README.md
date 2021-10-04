# RideBoard

RideBoard is CSH service that allows the members to carpool, allowing those that do not have a car to participate in events.

[![Build Status](https://travis-ci.org/ag-ayush/rideboard.svg?branch=master)](https://travis-ci.org/ag-ayush/rideboard)
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
2. `cd csh-rideboard/`
2. Create a python virtual environment, activate it and install requirements.
  - `virtualenv rides-venv`
  - `source rides-venv/bin/activate`
  - `pip install -r requirements.txt`
5. You will need many credentials to run, see the exports below. You can create your own if you are hosting your own application or ask an rtp for these if you would like to contribute to CSH. I'd recommend making a config.sh to automatically do the exports you need. It is in the .gitignore so it will not go to the remote repository.
```
export SERVER_NAME=127.0.0.1:8080 # Port 5000 sometimes works better in personal development
export IP=127.0.0.1 # Standard IP
export PORT=8080 # Port 5000 sometimes works better in personal development
export SQLALCHEMY_DATABASE_URI=postgresql://<DB DN>:<DB PW>@<IP:Port>/<Database> # ESSENTIAL to run service
export OIDC_CLIENT_SECRET=<OIDC Secret> # Needed to log in through CSH
export GOOGLE_CLIENT_ID=<Google ID> # Needed to log in through Google
export GOOGLE_CLIENT_SECRET=<Google Secret> # See Above
export SLACK_TOKEN=<Slack Token> # Needed for Slack Notification System
export MAIL_SERVER=<Mail Server> # Needed for Email Notification System
export MAIL_USERNAME=<Username>@<Domain> # See Above
export MAIL_PASSWORD=<Password> # See Above
```
6. To run the application:
  - Set debug mode: `export FLASK_ENV=development`
  - Export application: `export FLASK_APP=app.py`
  - Run: `flask run`
7. Now you can make your changes. Make sure the changes made work and that your code passes pylint (run `pylint rides/`). Once you do that you can make your pull request.

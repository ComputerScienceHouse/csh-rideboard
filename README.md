# RideBoard

RideBoard is CSH service that allows the members to add events and put their vehicles under the event for those members that do not have a car.

## Development
If you would like to develop or run this locally follow the following directions:

### Dependencies
* python
* pip
* virtualenv

### Setup
1. `git clone https://github.com/ag-ayush/rides.git`
2. Create a python virtual environment and activate it.
3. Go to where you cloned the repo.
4. `pip install -r requirements.txt`
5. You will need the LDAP DN, LDAP PW and MySQL Databse:
```
export SERVER_NAME=127.0.0.1:8080
export IP=127.0.0.1
export PORT=8080
export SQLALCHEMY_DATABASE_URI=postgresql://<LDAP DN>:<LDAP PW>@<MySQL Database>
export OIDC_CLIENT_SECRET=<OIDC Secret>
```
6. Now you should be able to run this locally with `python app.py`.

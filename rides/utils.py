import subprocess
from functools import wraps
from flask import session


INTRO_REALM = "https://sso.csh.rit.edu/auth/realms/intro"

def csh_user_auth(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        uid = str(session["userinfo"].get("preferred_username", ""))
        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').rstrip()
        last = str(session["userinfo"].get("family_name", ""))
        first = str(session["userinfo"].get("given_name", ""))
        picture = "https://profiles.csh.rit.edu/image/" + uid
        auth_dict = {
            "first": first,
            "last": last,
            "uid": uid,
            "commit": commit,
            "picture": picture
        }
        kwargs["auth_dict"] = auth_dict
        return func(*args, **kwargs)
    return wrapped_function

def google_user_auth(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        uid = str(session["userinfo"].get("sub", ""))
        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').rstrip()
        last = str(session["userinfo"].get("family_name", ""))
        first = str(session["userinfo"].get("given_name", ""))
        picture = str(session["userinfo"].get("picture", ""))
        auth_dict = {
            "first": first,
            "last": last,
            "uid": uid,
            "commit": commit,
            "picture": picture
        }
        kwargs["auth_dict"] = auth_dict
        return func(*args, **kwargs)
    return wrapped_function

def latin_to_utf8(string):
    return str(bytes(string, encoding='latin1'), encoding='utf8')

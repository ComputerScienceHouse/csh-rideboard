import subprocess
from functools import wraps
from flask import session


INTRO_REALM = "https://sso.csh.rit.edu/auth/realms/intro"

def user_auth(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        uid = str(session["userinfo"].get("preferred_username", ""))
        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').rstrip()
        if session["id_token"]["iss"] == INTRO_REALM:
            last = "(Intro)"
            first = uid
        else:
            last = str(session["userinfo"].get("family_name", ""))
            first = str(session["userinfo"].get("given_name", ""))

        auth_dict = {
            "first": first,
            "last": last,
            "uid": uid,
            "commit": commit
        }
        kwargs["auth_dict"] = auth_dict
        return func(*args, **kwargs)
    return wrapped_function

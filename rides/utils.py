from functools import wraps
from flask import session


def csh_user_auth(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        print(session["userinfo"])
        uid = str(session["userinfo"].get("preferred_username", ""))
        last = str(session["userinfo"].get("family_name", ""))
        first = str(session["userinfo"].get("given_name", ""))
        picture = "https://profiles.csh.rit.edu/image/" + uid
        slack = str(session["userinfo"].get("slackuid",""))
        email = str(session["userinfo"].get("email",""))
        auth_dict = {
            "first": first,
            "last": last,
            "uid": uid,
            "picture": picture,
            "slack": slack,
            "email": email
        }
        kwargs["auth_dict"] = auth_dict
        return func(*args, **kwargs)
    return wrapped_function


def google_user_auth(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        uid = str(session["userinfo"].get("sub", ""))
        last = str(session["userinfo"].get("family_name", ""))
        first = str(session["userinfo"].get("given_name", ""))
        picture = str(session["userinfo"].get("picture", ""))
        email = str(session["userinfo"].get("email",""))
        auth_dict = {
            "first": first,
            "last": last,
            "uid": uid,
            "picture": picture,
            "slack" : None,
            "email" : email
        }
        kwargs["auth_dict"] = auth_dict
        return func(*args, **kwargs)
    return wrapped_function


def latin_to_utf8(string):
    return str(bytes(string, encoding='latin1'), encoding='utf8')

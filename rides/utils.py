# Credit to Liam Middlebrook and Ram Zallan
# https://github.com/liam-middlebrook/gallery


from functools import wraps

from flask import session

INTRO_REALM = "https://sso.csh.rit.edu/auth/realms/intro"

def user_auth(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        uid = str(session["userinfo"].get("preferred_username", ""))
        if session["id_token"]["iss"] == INTRO_REALM:
            last = "(Intro)"
            first = uid
        else:
            last = str(session["userinfo"].get("family_name", ""))
            first = str(session["userinfo"].get("given_name", ""))
        auth_dict = {
            "first": first,
            "last": last,
            "uid": uid
        }
        kwargs["auth_dict"] = auth_dict

        return func(*args, **kwargs)

    return wrapped_function

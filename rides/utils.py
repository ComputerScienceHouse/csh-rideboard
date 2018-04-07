# Credit to Liam Middlebrook and Ram Zallan
# https://github.com/liam-middlebrook/gallery


from functools import wraps

from flask import session

def user_auth(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        last = str(session["userinfo"].get("family_name", ""))
        first = str(session["userinfo"].get("given_name", ""))
        uid = str(session["userinfo"].get("preferred_username", ""))

        auth_dict = {
            "first": first,
            "last": last,
            "uid": uid
        }
        kwargs["auth_dict"] = auth_dict

        return func(*args, **kwargs)

    return wrapped_function

from flask_login import current_user
from flask import flash, redirect, url_for, make_response
from functools import wraps, update_wrapper
from datetime import datetime

def admin_required(f):
    @wraps(f)
    def insidefunc(*args, **kwargs):
        if hasattr(current_user, "is_admin") and current_user.is_admin():
            return f(*args, **kwargs)
        else:
            flash("You are not authorized to view this page")
            return redirect(url_for("index"))
    return insidefunc



# thanks to http://arusahni.net/blog/2014/03/flask-nocache.html
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)

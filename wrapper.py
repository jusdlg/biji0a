from functools import wraps
from flask import session, redirect, url_for, render_template

def login_required(f):
    @wraps(f)
    def wrapper_func(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper_func


def admin_required(f):
    @wraps(f)
    def wrapper_func(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for("login"))
        if session["id"] != 1:
            return render_template("foriden.html")
        return f(*args, **kwargs)
    return wrapper_func
from functools import wraps
from flask import flash, redirect, url_for

def handle_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for("index"))
    return wrapper
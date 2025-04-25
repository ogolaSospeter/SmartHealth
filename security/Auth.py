import os
from flask import flash, redirect, request, jsonify, session, url_for
import jwt
from functools import wraps

SECRET_KEY = os.getenv('SECRET_KEY')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_id', ''):
            return f(*args, **kwargs)
        else:
            error = "You are not logged in!!!"
            flash(error, "danger")
            return redirect(url_for('signOut'))

    return decorated

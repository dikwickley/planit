import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')


def check_admin(user_id):
    db = get_db()
    user_in_db = db.execute(
        'SELECT * FROM admin WHERE user_id = ?', (user_id,)).fetchone()

    return not user_in_db == None


@auth_blueprint.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email.'
            flash(error)
            return render_template('auth/login.html')

        if not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
            flash(error)
            return render_template('auth/login.html')

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['admin'] = False
            if (check_admin(user['id'])):
                session['admin'] = True
            session['email'] = user['email']
            session['name'] = user['name']
            if (user['configured'] == 0):
                return redirect(url_for('plan.configure'))
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@auth_blueprint.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']

        db = get_db()
        error = None

        if not email:
            error = 'email is required.'
        elif not password:
            error = 'password is required.'
        # elif len(password) < 8:
        #     error = 'password too small'
        elif password != confirm_password:
            error = 'password should match'
        else:
            pass

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (email, password, name) VALUES (?, ?, ?)",
                    (email, generate_password_hash(password), name),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/signup.html')


@auth_blueprint.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@auth_blueprint.route('/logout')
def logout():
    session.clear()
    error = "logged out"
    flash(error)
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            error = "login required"
            flash(error)
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


def configured_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if (g.user['configured'] == 0):
            return redirect(url_for('plan.configure'))
        return view(**kwargs)

    return wrapped_view

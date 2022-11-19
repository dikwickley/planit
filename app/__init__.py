from .auth import login_required
import os

import requests
from flask import Flask, render_template, session


def get_random_quote():
    try:
        response = requests.get(
            "https://api.gameofthronesquotes.xyz/v1/random")
        if response.status_code == 200:
            json_data = response.json()
            print(json_data)
            return {"quote": json_data['sentence'], "author": json_data["character"]["name"]}
        else:
            print("Error while getting quote")
    except:
        print("Something went wrong! Try Again!")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='aniket',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import account, admin, auth, exam, plan, practice
    app.register_blueprint(auth.auth_blueprint)
    app.register_blueprint(exam.exam_blueprint)
    app.register_blueprint(plan.plan_blueprint)
    app.register_blueprint(practice.practice_blueprint)
    app.register_blueprint(account.account_blueprint)
    app.register_blueprint(admin.admin_blueprint)

    # a simple page that says hello
    @app.route('/')
    def index():
        # user = None
        # if 'email' in session:
        #     user = session['email']
        return render_template("index.html", is_quote=False)
        data = get_random_quote()
        return render_template("index.html", is_quote=True, quote=data['quote'], author=data['author'])

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')
    return app

import os

from flask import Flask, render_template, session
from flask_pymongo import PyMongo


from .auth import login_required

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config["MONGO_URI"] = "mongodb://aniket:Aniketsprx077@cluster0-shard-00-00-uugt8.mongodb.net:27017,cluster0-shard-00-01-uugt8.mongodb.net:27017,cluster0-shard-00-02-uugt8.mongodb.net:27017/main?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority"
    mongo = PyMongo(app)
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

    from . import auth
    from . import exam
    app.register_blueprint(auth.auth_blueprint)
    app.register_blueprint(exam.exam_blueprint)

    # a simple page that says hello
    @app.route('/')
    @login_required
    def index():
        user = None
        if 'username' in session:
            user = session['username']
        return render_template("index.html", user=user)

    return app
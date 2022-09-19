import os

from flask import Flask, render_template, session



from .auth import login_required

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

    from . import auth
    from . import exam
    from . import plan
    from . import practice
    from . import account
    app.register_blueprint(auth.auth_blueprint)
    app.register_blueprint(exam.exam_blueprint)
    app.register_blueprint(plan.plan_blueprint)
    app.register_blueprint(practice.practice_blueprint)
    app.register_blueprint(account.account_blueprint)

    # a simple page that says hello
    @app.route('/')
    def index():
        # user = None
        # if 'email' in session:
        #     user = session['email']
        return render_template("index.html")
        
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')
    return app
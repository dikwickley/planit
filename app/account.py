from datetime import datetime
from datetime import timedelta
import random
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app import exam
from app.auth import configured_required, login_required

from app.db import get_db

account_blueprint = Blueprint('account',__name__, url_prefix="/account")

@account_blueprint.route('/<screen>',methods=['GET', 'POST'])
@login_required
def show_account(screen):
    db = get_db()

    if screen == "plan-dashboard":
        pass
    elif screen == "test-dashboard":
        pass
    elif screen == "settings":
        pass
    elif screen == "profile":
        pass
    else:
        return redirect(url_for('index'))

    return render_template('account.html')

        
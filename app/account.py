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
        return render_template('account.html', screen=screen)
    elif screen == "test-dashboard":
        tests_in_db = db.execute(
            "SELECT * FROM test \
                WHERE email=?",(session['email'],)
        ).fetchall()
        print(tests_in_db)
        completed_tests = []
        uncompleted_tests = []

        for index, row in enumerate(tests_in_db):
            if(row['is_submitted']==True):
                completed_tests.append({
                    "index": index + 1,
                    "test_id": row['id'],
                    "date": row['submit_time'].split('T')[0],
                    "submit_time": row['submit_time'].split('T')[1],
                    "number_of_questions": row['number_of_questions'],
                    "marks": row['marks']
                })
            else:
                uncompleted_tests.append({
                    "index": index + 1,
                    "test_id": row['id'],
                    "date": row['start_time'].split('T')[0],
                    "start_time": row['start_time'].split('T')[1],
                    "number_of_questions": row['number_of_questions'],
                    "marks": row['marks']
                })
            
        return render_template('account.html', screen=screen, completed_tests=completed_tests, uncompleted_tests=uncompleted_tests)
    elif screen == "settings":
        pass
    elif screen == "profile":
        pass
    else:
        return redirect(url_for('index'))

    return render_template('account.html')

        
from datetime import datetime
from datetime import timedelta
import json
import random
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app import exam
from app.auth import configured_required, login_required

from app.db import get_db

account_blueprint = Blueprint('account',__name__, url_prefix="/account")

def trim_string(s: str, limit: int, ellipsis='…') -> str:
    s = s.strip()
    if len(s) > limit:
        return s[:limit-1].strip() + ellipsis
    return s

@account_blueprint.route('/<screen>',methods=['GET', 'POST'])
@login_required
def show_account(screen):
    db = get_db()
    email = session['email']

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
        
        total_answer = {}

        total_answer['right'] = db.execute("SELECT count(*) FROM result_details \
            WHERE email=? AND result=1",(email,)).fetchone()[0]
        total_answer['wrong'] = db.execute("SELECT count(*) FROM result_details \
            WHERE email=? AND result=-1",(email,)).fetchone()[0]
        total_answer['skipped'] = db.execute("SELECT count(*) FROM result_details \
            WHERE email=? AND result=0",(email,)).fetchone()[0]

        print(total_answer)

        date_answers = {}

        date_answers['right'] = {}
        date_answers['wrong'] = {}
        date_answers['skipped'] = {}

        result_times_in_db = db.execute("SELECT result_time, count(result) FROM result_details\
            WHERE email=? AND result=1\
            GROUP BY result_time ORDER BY result_time ",(email,))
        for times in result_times_in_db:
            date_answers['right'][times[0]] = times[1]

        result_times_in_db = db.execute("SELECT result_time, count(result) FROM result_details\
            WHERE email=? AND result=-1\
            GROUP BY result_time ORDER BY result_time",(email,))
        for times in result_times_in_db:
            date_answers['wrong'][times[0]] = times[1]

        result_times_in_db = db.execute("SELECT result_time, count(result) FROM result_details\
            WHERE email=? AND result=0\
            GROUP BY result_time ORDER BY result_time",(email,))
        for times in result_times_in_db:
            date_answers['skipped'][times[0]] = times[1]

        print(date_answers)


        topic_answer = {}

        topic_answer['right'] = []
        topic_answer['wrong'] = []
        topic_answer['skipped'] = []
        

        result_topics_in_db = db.execute("SELECT exam_details.topic_name as tn, exam_details.subject_name as sn, count(result_details.result) as cnt FROM\
            result_details LEFT JOIN exam_details ON result_details.topic_id = exam_details.id\
                WHERE email=? AND result_details.result=1 GROUP BY topic_name",(email,))
        for topic in result_topics_in_db:
            topic_answer['right'].append({
                "topic_name": topic['tn'],
                "subject_name": topic['sn'],
                "topic_count": topic['cnt'],
            })

        result_topics_in_db = db.execute("SELECT exam_details.topic_name as tn, exam_details.subject_name as sn, count(result_details.result) as cnt FROM\
            result_details LEFT JOIN exam_details ON result_details.topic_id = exam_details.id\
                WHERE email=? AND result_details.result=-1 GROUP BY topic_name",(email,))
        for topic in result_topics_in_db:
            topic_answer['wrong'].append({
                "topic_name": topic['tn'],
                "subject_name": topic['sn'],
                "topic_count": topic['cnt'],
            })

        result_topics_in_db = db.execute("SELECT exam_details.topic_name as tn, exam_details.subject_name as sn, count(result_details.result) as cnt FROM\
            result_details LEFT JOIN exam_details ON result_details.topic_id = exam_details.id\
                WHERE email=? AND result_details.result=0 GROUP BY topic_name",(email,))
        for topic in result_topics_in_db:
            topic_answer['skipped'].append({
                "topic_name": topic['tn'],
                "subject_name": topic['sn'],
                "topic_count": topic['cnt'],
            })

        print(topic_answer)
        
        return render_template('account.html', screen=screen, completed_tests=completed_tests, uncompleted_tests=uncompleted_tests, total_answer=json.dumps(total_answer), date_answers=json.dumps(date_answers), topic_answer=topic_answer)

    elif screen == "settings":
        pass
    elif screen == "profile":
        pass
    else:
        return redirect(url_for('index'))

    return render_template('account.html')

        
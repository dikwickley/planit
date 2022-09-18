from crypt import methods
from datetime import datetime
from datetime import timedelta
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app import exam
from app.auth import configured_required, login_required

from app.db import get_db

practice_blueprint = Blueprint('practice', __name__, url_prefix='/practice')

@practice_blueprint.route('/config', methods=['GET','POST'])
@login_required
def config_test():
    db = get_db()
    if request.method == 'POST':
        exam_id = request.form['exam']
        topics_in_db = db.execute(
            "SELECT * FROM exam_details \
            WHERE exam_id = ?",(exam_id,)
        ).fetchall()
        exam_name =  db.execute(
            "SELECT * FROM exam WHERE id = ?",(exam_id,)
        ).fetchone()["exam_name"]
        topics = {}
        for topic in topics_in_db:
            topic_id = topic["id"]
            topic_name = topic["topic_name"]
            subject_name = topic["subject_name"]
            if subject_name in topics:
                topics[subject_name].append({
                   "topic_id": topic_id, "topic_name" : topic_name
                })
            else:
                topics[subject_name] = [{
                    "topic_id": topic_id, "topic_name" : topic_name
                }]

        print(topics)
        print(exam_name)
        return render_template('practice/configure.html', topics=topics, topic_keys=list(topics.keys()),exam_name=exam_name)
    else:
        exams_in_db = db.execute(
            "SELECT * FROM exam"
        ).fetchall()

        exams = []

        for exam in exams_in_db:
            exams.append({"id": exam["id"], "exam_name": exam["exam_name"]})
        print(exams)
        return render_template('practice/configure.html',exams=exams)
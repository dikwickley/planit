from datetime import datetime
from datetime import timedelta
import random
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

@practice_blueprint.route('/make', methods=["POST"])
@login_required
def make_test():
    db = get_db()
    if request.method == "POST":
        test_topics = request.form.getlist('test_topics')
        number_of_questions = int(request.form["number_of_questions"])
        minutes_per_question = 3

        start_time = datetime.now().replace(microsecond=0).isoformat()
        end_time = (datetime.now() + timedelta(minutes=minutes_per_question*number_of_questions)).replace(microsecond=0).isoformat()
        email = session['email']
        print(start_time)
        print(end_time)
        
        print(test_topics)

        #make a test
        test_id = db.execute(
            "INSERT INTO test (email, start_time, end_time, number_of_questions, marks) \
                VALUES(?,?,?,?,?)",
                (email, start_time,end_time,number_of_questions, 0 )
        ).lastrowid
        

        #get test id
        # test_id = db.execute(
        #     "SELECT last_insert_rowid()"
        # )



        print("test_id",test_id)

        questions_in_db = db.execute(
            "SELECT * FROM questions\
                WHERE topic_id in {}".format(tuple(test_topics))
        ).fetchall()
        questions = []
        for question in questions_in_db:
            questions.append(question["id"])
    
        random.shuffle(questions)
        questions = questions[0:number_of_questions]

        for question_id in questions:

            db.execute(
                "INSERT INTO test_details(test_id,question_id)\
                    VALUES(?,?)",(test_id, question_id,)
            )

        db.commit()
        return questions
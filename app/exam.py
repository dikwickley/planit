import functools
import json
import random
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from lorem_text import lorem
from app.db import get_mongo
from app.db import get_db

exam_blueprint = Blueprint('exam', __name__, url_prefix='/exam')


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))


"""
to add more exams
http://127.0.0.1:5000/exam/GCS/1
"""


@exam_blueprint.route('/add/<code>/<id>', methods=['GET'])
def get_all_exam(code, id):
    if request.method == 'GET':
        mongo = get_mongo()
        db = get_db()
        syllabus = mongo.syllabus.find_one({"exam": code})
        syllabus = syllabus[syllabus['exam']]
        for key in syllabus:
            topics = syllabus[key]
            for topic in topics:
                print(topic[3], topic[1])
                hours = random.randint(1, 5)
                db.execute(
                    'INSERT INTO exam_details (exam_id, topic_name, subject_name, required_hours) VALUES("?","?","?","?")',
                    (id, topic[1], topic[3], hours)
                )
                db.commit()
        return syllabus


@exam_blueprint.route('dummy-questions/<exam_id>', methods=['GET'])
def add_dummy_exams(exam_id):
    db = get_db()
    topics = db.execute(
        "SELECT * FROM exam_details \
            WHERE exam_id = ?", (exam_id,)
    ).fetchall()
    print(topics)

    for topic in topics:
        topic_id = topic['id']
        for x in range(random.randint(1, 7)):
            question_statement = lorem.sentence()
            a = "option 1"
            b = "option 2"
            c = "option 3"
            d = "option 4"
            answer = random.choice(["a", "b", "c", "d"])
            db.execute(
                "INSERT INTO questions (topic_id, question_statement, a,b,c,d,answer) \
                    VALUES(?,?,?,?,?,?,?)",
                (topic_id, question_statement, a, b, c, d, answer)

            )

    db.commit()
    return "done"

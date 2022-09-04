import functools
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from app.db import get_mongo
from app.db import get_db

exam_blueprint = Blueprint('exam',__name__, url_prefix='/exam')

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
@exam_blueprint.route('/<code>/<id>', methods=['GET'])
def get_all_exam(code,id):
    if request.method == 'GET':
        mongo = get_mongo()
        db = get_db()
        syllabus = mongo.syllabus.find_one({"exam": code})
        syllabus = syllabus[syllabus['exam']]
        for key in syllabus:
            topics = syllabus[key]
            for topic in topics:
                print(topic[3], topic[1])
                db.execute(
                    "INSERT INTO exam_details (exam_id, topic_name, subject_name) VALUES(?,?,?)",
                    (id, topic[1], topic[3])
                )
                db.commit()
        return syllabus
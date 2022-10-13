import functools
import json
import csv
import random
import os
from app.__init__ import create_app

from flask import (
    Blueprint,  send_file, flash, g, redirect, render_template, request, session, url_for
)
from app.db import get_mongo
from app.db import get_db


admin_blueprint = Blueprint('admin',__name__, url_prefix='/admin')

data_dir = os.path.join(create_app().instance_path, 'data')


@admin_blueprint.route('/', methods=['GET','POST'])
def admin():
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

        column_names = [
            "topic_name",
            "subject_name",
            "required_hours"
        ]
        file_name = f"{exam_id}_{exam_name}.csv"
        file_path = os.path.join(data_dir, file_name)
        fp = open(file_path, 'w+')
        myFile = csv.writer(fp, lineterminator = '\n') #use lineterminator for windows
        myFile.writerow(column_names)
        for row in topics_in_db:
            topic = [
                row['topic_name'],
                row['subject_name'],
                row['required_hours']
            ]
            myFile.writerow(topic)
        fp.close()
        return send_file(file_path, as_attachment=True)
    else:
        exams_in_db = db.execute(
            "SELECT * FROM exam"
        ).fetchall()

        exams = []

        for exam in exams_in_db:
            exams.append({"id": exam["id"], "exam_name": exam["exam_name"]})
        print(exams)
        return render_template("admin/index.html", exams=exams)
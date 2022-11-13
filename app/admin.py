import json
import csv
import os
from flask import (
    Blueprint,  send_file, flash, g, redirect, render_template, request, session, url_for, current_app
)
from app.db import get_mongo
from app.db import get_db


admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')


data_dir = os.path.join(admin_blueprint.root_path, 'data')

print("root path", admin_blueprint.root_path)


@admin_blueprint.route('/', methods=['GET', 'POST'])
def admin():
    db = get_db()

    if ('admin' not in session):
        # session['admin'] = False;
        return redirect(url_for('index'))

    data = {}

    exams_in_db = db.execute(
        "SELECT count(*) as count from exam").fetchone()['count']

    users_in_db = db.execute(
        "SELECT count(*) as count from user").fetchone()['count']

    tests_in_db = db.execute(
        "SELECT count(*) as count from test").fetchone()['count']

    data['exams_in_db'] = exams_in_db
    data['users_in_db'] = users_in_db
    data['tests_in_db'] = tests_in_db

    users = []
    user_details_in_db = db.execute(
        "SELECT * FROM user WHERE configured=1"
    ).fetchall()

    for user in user_details_in_db:
        print(user['name'])
        users.append({
            "id": user['id'],
            "email": user['email'],
            "name": user['name']
        })

    return render_template("admin/dashboard.html", data=data, users=users)


@admin_blueprint.route('/plan/<email>', methods=['GET', 'POST'])
def admin_user_plan_progress(email):
    db = get_db()

    plan_in_db = db.execute(
        "SELECT * FROM plan\
            WHERE email=?", (email,)
    ).fetchone()

    plan_id = plan_in_db["id"]
    start_date = plan_in_db["start_date"]
    end_date = plan_in_db["end_date"]

    dates = {
        "start_date": start_date.strftime("%m/%d/%Y"),
        "end_date": end_date.strftime("%m/%d/%Y")
    }

    uncompleted_topics_in_db = db.execute(
        "SELECT * FROM plan_details WHERE completed = 0 AND plan_id=?", (
            plan_id,)
    ).fetchall()

    completed_topics_in_db = db.execute(
        "SELECT * FROM plan_details WHERE completed = 1 AND plan_id=?", (
            plan_id,)
    ).fetchall()

    topic_number_data = {
        "completed": len(completed_topics_in_db),
        "uncompleted": len(uncompleted_topics_in_db),
    }
    print(topic_number_data)

    subject_data = {}

    for topic_row in completed_topics_in_db:
        if topic_row["subject_name"] in subject_data:
            subject_data[topic_row["subject_name"]] += 1
        else:
            subject_data[topic_row["subject_name"]] = 1

    subject_data["Uncompleted"] = len(uncompleted_topics_in_db)

    print(subject_data)

    return render_template('admin/plan_progress.html', email=email, topic_number_data=json.dumps(topic_number_data), start_end=dates, dates=json.dumps(dates), subject_data=json.dumps(subject_data))


@admin_blueprint.route('/syllabus', methods=['GET', 'POST'])
def admin_syllabus():
    db = get_db()

    if ('admin' not in session):
        # session['admin'] = False;
        return redirect(url_for('index'))

    exams_in_db = db.execute(
        "SELECT * FROM exam"
    ).fetchall()

    exams = []

    for exam in exams_in_db:
        exams.append({"id": exam["id"], "exam_name": exam["exam_name"]})
    print(exams)

    return render_template("admin/syllabus.html", exams=exams)


@admin_blueprint.route('/questions', methods=['GET', 'POST'])
def admin_question():
    db = get_db()

    if ('admin' not in session):
        # session['admin'] = False;
        return redirect(url_for('index'))

    topics_in_db = db.execute(
        "SELECT * FROM exam_details"
    ).fetchall()

    topics = []

    for topic in topics_in_db:
        topics.append({"id": topic["id"], "topic_name": topic["topic_name"]})

    return render_template("admin/questions.html", topics=topics)


@admin_blueprint.route('/download/questions', methods=['GET', 'POST'])
def download_questions():
    db = get_db()
    if request.method == "POST":
        topic_id = request.form['topic_id']
        questions_in_db = db.execute(
            "SELECT * FROM questions \
            WHERE topic_id = ?", (topic_id,)
        ).fetchall()
        column_names = [
            "id",
            "topic_id",
            "question_statement",
            "a",
            "b",
            "c",
            "d",
            "answer"
        ]
        topic_name = db.execute(
            "SELECT * FROM exam_details WHERE id = ?", (topic_id,)
        ).fetchone()["topic_name"]

        file_name = f"{topic_id}_{topic_name}.csv"
        file_path = os.path.join(data_dir, file_name)
        fp = open(file_path, 'w+')
        # use lineterminator for windows
        myFile = csv.writer(fp, lineterminator='\n')
        myFile.writerow(column_names)

        for row in questions_in_db:
            question = [
                row["id"],
                row["topic_id"],
                row["question_statement"],
                row["a"],
                row["b"],
                row["c"],
                row["d"],
                row["answer"]
            ]
            myFile.writerow(question)

        fp.close()
        return send_file(file_path, as_attachment=True)


@admin_blueprint.route('/upload/questions', methods=['GET', 'POST'])
def upload_questions():
    db = get_db()
    if request.method == "POST":

        if 'file' not in request.files:
            flash('No files')
            return redirect(url_for('admin.admin'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('admin.admin'))
        file_name = file.filename

        topic_id, topic_name = file_name.split('_')
        file_path = os.path.join(data_dir, file_name)

        file.save(file_path)

        update_rows = []
        new_rows = []
        delete_rows = []

        with open(file_path, mode='r')as file:

            # reading the CSV file
            csvFile = csv.reader(file)

            # displaying the contents of the CSV file
            for lines in csvFile:
                print(lines)
                if (lines[0] == ''):
                    new_rows.append(lines)
                elif (lines[1] == '' and lines[2] == '' and lines[3] == ''):
                    delete_rows.append(lines[0])
                else:
                    update_rows.append(lines)

        update_rows.pop(0)

        print("update", update_rows)
        print("new", new_rows)
        print("delete", delete_rows)

        for id in delete_rows:
            db.execute(
                "DELETE FROM questions where id=?", (id,)
            )
        for lines in update_rows:
            db.execute(
                "UPDATE questions SET question_statement=?, a=?, b=?, c=?, d=?, answer=? WHERE id=?", (
                    lines[2], lines[3], lines[4], lines[5], lines[6], lines[7], lines[0])
            )

        for lines in new_rows:
            db.execute(
                "INSERT INTO questions (topic_id, question_statement, a, b, c, d, answer) VALUES(?,?,?,?,?,?,?)",
                (topic_id, lines[2], lines[3],
                 lines[4], lines[5], lines[6], lines[7])
            )
        db.commit()
        error = "updated questions for " + topic_name
        flash(error)
        return redirect(url_for('admin.admin_question'))


@admin_blueprint.route('/download/syllabus', methods=['GET', 'POST'])
def download_syllabus():
    db = get_db()
    if request.method == "POST":
        exam_id = request.form['exam']
        topics_in_db = db.execute(
            "SELECT * FROM exam_details \
            WHERE exam_id = ?", (exam_id,)
        ).fetchall()
        exam_name = db.execute(
            "SELECT * FROM exam WHERE id = ?", (exam_id,)
        ).fetchone()["exam_name"]

        column_names = [
            "id",
            "topic_name",
            "subject_name",
            "required_hours"
        ]
        file_name = f"{exam_id}_{exam_name}.csv"
        file_path = os.path.join(data_dir, file_name)
        fp = open(file_path, 'w+')
        # use lineterminator for windows
        myFile = csv.writer(fp, lineterminator='\n')
        myFile.writerow(column_names)
        for row in topics_in_db:
            topic = [
                row['id'],
                row['topic_name'],
                row['subject_name'],
                row['required_hours']
            ]
            myFile.writerow(topic)
        fp.close()
        return send_file(file_path, as_attachment=True)


@admin_blueprint.route('/upload/syllabus', methods=['GET', 'POST'])
def upload_syllabus():
    db = get_db()
    if request.method == "POST":

        if 'file' not in request.files:
            flash('No files')
            return redirect(url_for('admin.admin'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('admin.admin'))
        file_name = file.filename

        exam_id, exam_name = file_name.split('_')
        file_path = os.path.join(data_dir, file_name)

        file.save(file_path)

        update_rows = []
        new_rows = []
        delete_rows = []

        with open(file_path, mode='r')as file:

            # reading the CSV file
            csvFile = csv.reader(file)

            # displaying the contents of the CSV file
            for lines in csvFile:
                print(lines)
                if (lines[0] == ''):
                    new_rows.append(lines)
                elif (lines[1] == '' and lines[2] == '' and lines[3] == ''):
                    delete_rows.append(lines[0])
                else:
                    update_rows.append(lines)

        update_rows.pop(0)

        print("update", update_rows)
        print("new", new_rows)
        print("delete", delete_rows)

        for id in delete_rows:
            db.execute(
                "DELETE FROM exam_details where id=?", (id,)
            )

        for lines in update_rows:
            db.execute(
                "UPDATE exam_details SET topic_name=?, subject_name=?, required_hours=? WHERE id=?", (
                    lines[1], lines[2], lines[3], lines[0],)
            )

        for lines in new_rows:
            db.execute(
                "INSERT INTO exam_details (exam_id, topic_name, subject_name, required_hours) VALUES(?,?,?,?)",
                (exam_id, lines[1], lines[2], lines[3])
            )
        db.commit()

        os.remove(file_path)

        error = "updated syllabus"
        flash(error)
        return redirect(url_for('admin.admin_syllabus'))

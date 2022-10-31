import functools
import json
import csv
import random
import os
import re
from flask import (
    Blueprint,  send_file, flash, g, redirect, render_template, request, session, url_for, current_app
)
from app.db import get_mongo
from app.db import get_db


admin_blueprint = Blueprint('admin',__name__, url_prefix='/admin')


data_dir = os.path.join(admin_blueprint.root_path, 'data')

print("root path", admin_blueprint.root_path)



@admin_blueprint.route('/', methods=['GET','POST'])
def admin():
    db = get_db()

    if(request.method == 'POST'):
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']

        if(admin_password!='admin' or admin_username != 'admin'):
            error = "wrong credentials"
            flash(error)
            return redirect(url_for('admin.admin'))
        session['admin'] = True

    
    if('admin' not in session):
        session['admin'] = False;
        return render_template("admin/index.html")
      
        
    exams_in_db = db.execute(
        "SELECT * FROM exam"
    ).fetchall()

    exams = []

    for exam in exams_in_db:
        exams.append({"id": exam["id"], "exam_name": exam["exam_name"]})
    print(exams)
    return render_template("admin/index.html", exams=exams)

@admin_blueprint.route('/download/syllabus', methods=['GET','POST'])
def download_syllabus():
    db = get_db()
    if request.method == "POST":
        exam_id = request.form['exam']
        topics_in_db = db.execute(
            "SELECT * FROM exam_details \
            WHERE exam_id = ?",(exam_id,)
        ).fetchall()
        exam_name =  db.execute(
            "SELECT * FROM exam WHERE id = ?",(exam_id,)
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
        myFile = csv.writer(fp, lineterminator = '\n') #use lineterminator for windows
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

@admin_blueprint.route('/upload/syllabus', methods=['GET','POST'])
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
        
        with open(file_path, mode ='r')as file:
   
            # reading the CSV file
            csvFile = csv.reader(file)
            
            # displaying the contents of the CSV file
            for lines in csvFile:
                    print(lines)
                    if(lines[0]==''):
                        new_rows.append(lines)
                    elif(lines[1]=='' and lines[2]=='' and lines[3]==''):
                        delete_rows.append(lines[0]);
                    else:
                        update_rows.append(lines);
                    

        update_rows.pop(0)

        print("update", update_rows)
        print("new", new_rows)
        print("delete", delete_rows)

        for id in delete_rows:
            db.execute(
                "DELETE FROM exam_details where id=?",(id,)
            )

        for lines in update_rows:
            db.execute(
             "UPDATE exam_details SET topic_name=?, subject_name=?, required_hours=? WHERE id=?",(lines[1],lines[2],lines[3],lines[0],)   
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
        return redirect(url_for('admin.admin'))
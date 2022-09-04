from audioop import reverse
from datetime import datetime
from datetime import timedelta
import functools
import json
import math
from this import s
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app import exam
from app.auth import configured_required, login_required

from app.db import get_db

plan_blueprint = Blueprint('plan',__name__, url_prefix='/plan')

def weeks_between(start_date, end_date):
    days = abs(end_date-start_date).days
    return math.floor(days/7)



def increasing_study_function(number_of_topics, number_of_weeks):
    li=[]
    for i in range(0,number_of_weeks):
        li.append((i+1)**1.05)
    x=sum(li)
    for i in range(0,len(li)):
        li[i]=math.ceil(li[i]*(number_of_topics/x)) 
    
    return li

def decreasing_study_function(number_of_topics, number_of_weeks):
    li=[]
    for i in range(0,number_of_weeks):
        li.append((i+1)**1.05)
    x=sum(li)
    for i in range(0,len(li)):
        li[i]=math.ceil(li[i]*(number_of_topics/x)) 
    li.reverse()
    return li

def constant_study_function(number_of_topics, number_of_weeks):
    li=[]
    for i in range(0,number_of_weeks):
        li.append(1)
    x=sum(li)
    for i in range(0,len(li)):
        li[i]=math.ceil(li[i]*(number_of_topics/x)) 
    return li



@plan_blueprint.route('/', methods=['GET','POST'])
@configured_required
def show_plan():
    db = get_db()

    email = session['email']

    print(f"email {email}")

    plan = db.execute(
        "SELECT * FROM plan \
        WHERE email = ?",(email,)
    ).fetchone()

    print(f"plan id {plan}")


    exam_name =  plan['exam']
    start_date = plan['start_date']
    # start_date = datetime.strptime(start_date, '%Y-%m-%d')
    

    plan_in_db = db.execute(
        "SELECT * FROM plan_details\
            WHERE plan_id = ?",(str(plan['id']),)
    ).fetchall()

    print(f"plan in db {plan_in_db}")

    plan_data = {}

    for plan_row in plan_in_db:

        week_number = int(plan_row['week_number'])
        week_start = (start_date + timedelta(days=(week_number-1)*7)).strftime("%d %B, %Y")
        week_end = (start_date + timedelta(days=(week_number)*7)).strftime("%d %B, %Y")
        week_key = f"{week_start} to {week_end}"

        if week_key not in plan_data:
            plan_data[week_key] = [
                {
                    "subject_name": plan_row["subject_name"],
                    "topic_name": plan_row["topic_name"]
                }
            ]
        else:
            plan_data[week_key].append(
                {
                    "subject_name": plan_row["subject_name"],
                    "topic_name": plan_row["topic_name"]
                }
            )

    print(plan_data)
    return render_template('plan/index.html', plan_data=plan_data, exam_name=exam_name)


@plan_blueprint.route('/configure', methods=['GET','POST'])
@login_required
def configure():
    if request.method == 'POST':
        db = get_db()

        email = session['email']

        print(f"email {email}")

        plan_in_db = db.execute(
            "SELECT * FROM plan \
            WHERE email = ?",(email,)
        ).fetchone()

        print(f"plan in db {plan_in_db}")

        if plan_in_db is not None:
            error = "plan already created"
            flash(error)
            return redirect(url_for('plan.show_plan'))

        exam_id = request.form['exam']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        plan_type = request.form['plan_type']

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if(start_date > end_date):
            error = "end date can not be earlier than start date"
            flash(error)
            return redirect(url_for('plan.configure'))

        print(f"exam_id {exam_id}")
        #get exam name
        
        exam_name = db.execute(
            "SELECT * FROM exam \
            WHERE id = ?",(exam_id)
        ).fetchone()['exam_name']
        print(f"exam name {exam_name}")

        #make a plan
        res = db.execute(
            "INSERT INTO plan (email,exam,start_date,end_date) \
                VALUES(?,?,?,?)",
                (email,exam_name,start_date,end_date)
        )
        db.commit()

        #get plan id
        plan_id = db.execute(
            "SELECT * FROM plan \
            WHERE email = ?",(email,)
        ).fetchone()['id']

        

        #count total topics in an exam
        topic_count = db.execute(
            "SELECT count(*) FROM exam_details \
            WHERE exam_id = ?",(exam_id,)
        ).fetchone()[0]

        week_count = weeks_between(start_date, end_date)

        print(topic_count)
        print(week_count)

        if(plan_type == 'increasing'):
            plan_distribution = increasing_study_function(topic_count, week_count)
        elif (plan_type == 'decreasing'):
            plan_distribution = decreasing_study_function(topic_count, week_count)
        elif (plan_type == 'constant'):
            plan_distribution = constant_study_function(topic_count, week_count)

        print(plan_distribution)

        topics = db.execute(
            "SELECT * FROM exam_details \
            WHERE exam_id = ?",(exam_id,)
        ).fetchall()

        current_week = 0

        #add plan details
        for topic in topics:
            subject_name = topic['subject_name']
            topic_name = topic['topic_name']
            print(subject_name, topic_name)
            if(plan_distribution[current_week]==0):
                current_week += 1
            db.execute(
                "INSERT INTO plan_details (plan_id, week_number, subject_name, topic_name, completed) \
                    VALUES(?,?,?,?,?)",
                    (plan_id,current_week+1,subject_name,topic_name, 0)

            )
            plan_distribution[current_week] -= 1

            db.commit()

        #mark configured as true for user
        db.execute(
            "UPDATE user \
                SET configured=1\
                    WHERE email = ?",
                    (email,)
        )
        db.commit()

        return redirect(url_for('plan.show_plan'))
    else:
        db = get_db()

        email = session['email']

        print(f"email {email}")

        plan_in_db = db.execute(
            "SELECT * FROM plan \
            WHERE email = ?",(email,)
        ).fetchone()

        print(f"plan in db {plan_in_db}")

        if plan_in_db is not None:
            error = "plan already created"
            flash(error)
            return redirect(url_for('plan.show_plan'))
        return render_template('plan/configure.html')
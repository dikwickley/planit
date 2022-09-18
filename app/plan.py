from audioop import reverse
from datetime import datetime
from datetime import timedelta
import math
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



def increasing_study_function(hours, number_of_weeks):
    li=[]
    for i in range(0,number_of_weeks):
        li.append((i+1)**1.05)
    x=sum(li)
    for i in range(0,len(li)):
        li[i]=math.ceil(li[i]*(hours/x)) 
    
    return li

def decreasing_study_function(hours, number_of_weeks):
    li=[]
    for i in range(0,number_of_weeks):
        li.append((i+1)**1.05)
    x=sum(li)
    for i in range(0,len(li)):
        li[i]=math.ceil(li[i]*(hours/x)) 
    li.reverse()
    return li

def constant_study_function(hours, number_of_weeks):
    li=[]
    for i in range(0,number_of_weeks):
        li.append(1)
    x=sum(li)
    for i in range(0,len(li)):
        li[i]=math.ceil(li[i]*(hours/x)) 
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
            plan_data[week_key] = {
                "total_hours" : plan_row["required_hours"],
                # "hours_per_day" : math.ceil(plan_row["required_hours"]/7),
                "data" :  [
                        {
                            "subject_name": plan_row["subject_name"],
                            "topic_name": plan_row["topic_name"],
                            "hours": plan_row["required_hours"]
                        }
                    ]
            }
           
        else:
            plan_data[week_key]["total_hours"] += plan_row["required_hours"]
            # plan_data[week_key]["hours_per_day"] = math.ceil(plan_row["total_hours"]/7)
            plan_data[week_key]["data"].append(
                {
                    "subject_name": plan_row["subject_name"],
                    "topic_name": plan_row["topic_name"],
                    "hours": plan_row["required_hours"]
                }
            )

    for key in plan_data:
        print (key) # for the keys
        print (plan_data[key])
        plan_data[key]["hours_per_day"] = math.ceil(plan_data[key]["total_hours"]/7)

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
        daily_study_hours = int(request.form['daily_hours'])

        start_d = datetime.strptime(start_date, '%Y-%m-%d')
        end_d = datetime.strptime(end_date, '%Y-%m-%d')

        if(start_d > end_d):
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
        plan_id = db.execute(
            "INSERT INTO plan (email,exam,start_date,end_date) \
                VALUES(?,?,?,?)",
                (email,exam_name,start_date,end_date)
        ).lastrowid
        

        print(f"plan {plan_id}")


        #count total topics in an exam
        # topic_count = db.execute(
        #     "SELECT count(*) FROM exam_details \
        #     WHERE exam_id = ?",(exam_id,)
        # ).fetchone()[0]

        hour_count = db.execute(
            "SELECT sum(required_hours) FROM exam_details \
                WHERE exam_id = ?;",(exam_id,)
        ).fetchone()[0]

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if((end_date - start_date).days < 7):
            error = "too less days"
            flash(error)
            return redirect(url_for('plan.configure'))

        week_count = weeks_between(start_date, end_date)

        print(hour_count)
        print(week_count)

        if(plan_type == 'increasing'):
            plan_distribution = increasing_study_function(hour_count, week_count)
        elif (plan_type == 'decreasing'):
            plan_distribution = decreasing_study_function(hour_count, week_count)
        elif (plan_type == 'constant'):
            plan_distribution = constant_study_function(hour_count, week_count)

        print(plan_distribution)

        for weekly_hours in plan_distribution:
            if(math.ceil(weekly_hours/7)>daily_study_hours):
                error="daily study hours required more than specified study hours. please change plan type or increase date range"
                flash(error)
                return redirect(url_for('plan.configure'))


        topics = db.execute(
            "SELECT * FROM exam_details \
            WHERE exam_id = ?",(exam_id,)
        ).fetchall()

        current_week = 0

        #add plan details
        for topic in topics:
            subject_name = topic['subject_name']
            topic_name = topic['topic_name']
            required_hours =  topic['required_hours']
            print(subject_name, topic_name)
            if(plan_distribution[current_week]<0 and current_week < len(plan_distribution) ):
                #re distributing previous plan to next week
                plan_distribution[current_week + 1] += abs(plan_distribution[current_week])
                current_week += 1
            db.execute(
                "INSERT INTO plan_details (plan_id, week_number, subject_name, topic_name,required_hours, completed) \
                    VALUES(?,?,?,?,?,?)",
                    (plan_id,current_week+1,subject_name,topic_name,required_hours, 0)

            )
            plan_distribution[current_week] -= topic['required_hours']

            

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
        
        exams_in_db = db.execute(
            "SELECT * FROM exam"
        ).fetchall()

        exams = []

        for exam in exams_in_db:
            exams.append({"id": exam["id"], "exam_name": exam["exam_name"]})
        print(exams)
        return render_template('plan/configure.html',exams=exams)
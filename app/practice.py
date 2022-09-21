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

@practice_blueprint.route('/result/<test_id>', methods=['POST','GET'])
@login_required
def show_result(test_id):
    db = get_db()

    test_questions = db.execute('SELECT question_id FROM test_details\
        WHERE test_id = ?',(test_id,)).fetchall()
    
    # print(test_questions['question_id'])
    test_question_list = []
    for question in test_questions:
        test_question_list.append(question['question_id'])

    print(test_question_list)

    # return test_question_list

    # question_answers_in_db = db.execute('SELECT * FROM questions\
    #     WHERE id in ?',(tuple(test_question_list),))
    questions_in_db = db.execute(
            "SELECT * FROM questions\
                WHERE id in {}".format(tuple(test_question_list))
        ).fetchall()

    question_answers = {}

    for q_a in questions_in_db:
        question_answers[q_a['id']] = {
            "statement" : q_a['question_statement'],
            "answer" : q_a['answer'],
            "option_a" : q_a['a'],
            "option_b" : q_a['b'],
            "option_c" : q_a['c'],
            "option_d" : q_a['d']
        }

    # return question_answers

    right_answers = []
    wrong_answers = []
    skipped_answers = []

    test_details_in_db = db.execute('SELECT * FROM test_details\
        WHERE test_id = ?',(test_id,)).fetchall()

    for test_detail in test_details_in_db:
        if(test_detail['answer'] is None):
            answer = question_answers[test_detail['question_id']]
            answer['your_answer'] = None
            skipped_answers.append(answer)
            continue

        if(test_detail['answer'] == test_detail['question_id']):
            answer = question_answers[test_detail['question_id']]
            answer['your_answer'] = test_detail['answer']
            right_answers.append(answer)
        else:
            answer = question_answers[test_detail['question_id']]
            answer['your_answer'] = test_detail['answer']
            wrong_answers.append(answer)


    return {
        "right": right_answers,
        "wrong": wrong_answers,
        "skipped": skipped_answers
    }
    # for test_details in  

@practice_blueprint.route('/save-answer', methods=['POST'])
@login_required
def save_answer():
    db = get_db()
    test_id = request.form['test_id']
    sequence_number = int(request.form['sequence_number'])

    answer = request.form.get('answer')

    #save this answer in test
    print("save answer", answer)
    db.execute("UPDATE test_details \
        SET answer=?\
            WHERE test_id = ? AND sequence_number = ?",(answer, test_id, sequence_number))
    db.commit()
    return redirect(url_for('practice.show_test', test_id=test_id, sequence_number=sequence_number+1))
    
@practice_blueprint.route('/submit-test', methods=["POST"])
@login_required
def submit_test():
    db = get_db()
    test_id = request.form.get('test_id')

    return test_id

@practice_blueprint.route('/test/<test_id>/<sequence_number>', methods=['GET','POST'])
@login_required
def show_test(test_id, sequence_number):
    db = get_db()

    email = session['email']

    test_in_db = db.execute("SELECT * FROM test\
        where id = ?",(test_id,)).fetchone()

    if test_in_db is None:
        error = "no test exist"
        flash(error)
        return redirect(url_for('practice.config_test'))

    if test_in_db['is_submitted'] == True:
        error = "test already submitted"
        flash(error)
        return redirect(url_for('practice.config_test'))


    if test_in_db['email'] != email:
        error = "no auth to access test"
        flash(error)
        return redirect(url_for('practice.config_test'))
    
    number_of_questions = test_in_db['number_of_questions']
    
    #check for date time condition
    # end_time = test_in_db['end_time']
    # print('end_time',end_time)

    if int(sequence_number) == 0:
        error = "can't move previous"
        flash(error)
        return redirect(url_for('practice.show_test', test_id=test_id, sequence_number=1))

    if int(sequence_number) > (number_of_questions):
        error = "moved to start of test"
        flash(error)
        return redirect(url_for('practice.show_test', test_id=test_id, sequence_number=1))

    test_details_in_db = db.execute("SELECT * FROM test_details \
        WHERE test_id = ? AND sequence_number = ?",(test_id, sequence_number)).fetchone()

    
    answered_questions = {}
    answered_questions_in_db = db.execute("SELECT * FROM test_details\
        WHERE answer is not NULL AND test_id = ? ",(test_id,)).fetchall()

    for answer in answered_questions_in_db:
        answered_questions[answer["sequence_number"]] = answer['answer']

    if test_details_in_db is None:
        error = "question does not exist"
        flash(error)
        return redirect(url_for('practice.config_test'))

    question_id = test_details_in_db["question_id"]

    
    print("question_id",question_id)
    
    question_in_db = db.execute("SELECT * FROM questions\
        WHERE id = ? ",(question_id,)).fetchone()
    
    question_statement = question_in_db['question_statement']
    options = {
        'a': question_in_db['a'],
        'b': question_in_db['b'],
        'c': question_in_db['c'],
        'd': question_in_db['d'],
    }
    return render_template('practice/test.html',sequence_number=int(sequence_number), question_statement=question_statement, options=options, test_id=test_id, number_of_questions=number_of_questions, answered_questions=answered_questions)
    # return [sequence_number, question_statement, options, test_id, number_of_questions]

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
        
        if len(test_topics)<1:
            error = "too less topics"
            flash(error)
            return redirect(url_for('practice.config_test'))
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
        sequence_number = 1
        for question_id in questions:

            db.execute(
                "INSERT INTO test_details(sequence_number,test_id,question_id)\
                    VALUES(?,?,?)",(sequence_number, test_id, question_id,)
            )

            sequence_number += 1

        db.commit()
        return redirect(url_for('practice.show_test', test_id=test_id, sequence_number=1))
from crypt import methods
from flask import Flask, redirect, render_template, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]='mysql+pymysql://root:root@localhost/UpworkJob'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config['SECRET_KEY']='backdoor'
db=SQLAlchemy(app)
moment = Moment(app)


class students (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_full_name = db.Column(db.String(200),nullable=False)
    year_group = db.Column(db.Integer,nullable=False)
    house = db.Column(db.String(40),nullable=False)
    student_email = db.Column(db.String(400),nullable=False)
    password = db.Column(db.String(300),nullable=False)
    lessons = db.relationship('lessons', backref='student', lazy='dynamic')

class teachers (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_full_name = db.Column(db.String(200),nullable=False)
    teacher_email = db.Column(db.String(400),nullable=False)
    house = db.Column(db.String(40),nullable=False)
    password = db.Column(db.String(300),nullable=False)
    lessons = db.relationship('lessons', backref='teacher', lazy='dynamic')

class lessons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_lesson = db.Column(db.String(260), nullable=False)
    duration = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(260), nullable=False)
    teachers_id = db.Column(db.Integer, db.ForeignKey(teachers.id))
    students_id = db.Column(db.Integer, db.ForeignKey(students.id))


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/main_page')
def main_page():
    return render_template('main_page.html')


@app.route('/student_page')
def student_page():
    return render_template('student_page.html')


@app.route('/teacher_page')
def teacher_page():
    return render_template('teacher_page.html')


@app.route('/individual_student/<int:id>', methods=['GET'])
def individual_student(id):
    if 'student_email' in session:
        student = students.query.filter_by(id=id).first_or_404()
    else:
        return redirect(url_for('student_login'))
    return render_template('student.html', student=student)


#teacher login
@app.route('/teacher_login', methods=["POST", "GET"])
def teacher_login():
    if request.method == "POST":
        teacher_email = request.form.get("teacher_email")
        password = request.form.get("password")
        teacher_login = teachers.query.filter_by(teacher_email=teacher_email,password=password).first()
        if teacher_login:
            session["teacher_email"]=teacher_email
            return redirect (url_for('add_lesson', id=teacher_login.id))
        else:
            flash("wrong email or password")
            return redirect (url_for('teacher_login'))
    return render_template("teacher_login.html")

#teacher register
@app.route('/teacher_register', methods=["POST","GET"])
def teacher_register():
    if request.method == "POST":
        teacher_full_name = request.form.get("teacher_full_name")
        house = request.form.get("house")
        teacher_email = request.form.get("teacher_email")
        password = request.form.get("password")
        teacher_register = teachers(teacher_full_name=teacher_full_name, house=house, teacher_email=teacher_email, password=password)
        db.session.add(teacher_register)
        db.session.commit()
        return redirect (url_for('teacher_login'))
    return render_template("teacher_register.html")


@app.route('/add_lesson/<int:id>', methods=['POST', 'GET'])
def add_lesson(id):
    if 'teacher_email' not in session:
        flash('only teachers can add lessons')
        return redirect(url_for('teacher_login'))
    if request.method == 'POST':
        name_lesson = request.form.get('name_lesson')
        duration = request.form.get('duration')
        date = request.form.get('date')
        teacher = teachers.query.filter_by(id=id).first()
        addlesson = lessons(name_lesson=name_lesson,duration=duration,date=date, teacher=teacher)
        db.session.add(addlesson)
        db.session.commit()
        return redirect(url_for('lesson'))
    return render_template('add_lesson.html')


@app.route('/lesson', methods=['GET'])
def lesson():
    lesson = lessons.query.all()
    return render_template('lessons.html', lesson=lesson)

#student login
@app.route('/student_login', methods=["POST", "GET"])
def student_login():
    if request.method == "POST":
        student_email = request.form.get("student_email")
        password = request.form.get("password")
        student_login = students.query.filter_by(student_email=student_email,password=password).first()
        if student_login:
            session["student_email"]=student_email
            return redirect (url_for('individual_student', id=student_login.id))
        else:
            flash("Wrong email or password")
            return redirect (url_for('student_login'))
    return render_template("student_login.html")

#student register
@app.route('/student_register', methods=["POST", "GET"])
def student_register():
    if request.method == "POST":
        student_full_name = request.form.get("student_full_name")
        year_group = request.form.get("year_group")
        house = request.form.get("house")
        student_email = request.form.get("student_email")
        password = request.form.get("password")
        student_register = students(student_full_name=student_full_name, year_group=year_group, house=house, student_email=student_email, password=password)
        db.session.add(student_register)
        db.session.commit()
        return redirect (url_for('student_login'))
    return render_template("student_register.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__=="__main__":
    app.run(debug=True)

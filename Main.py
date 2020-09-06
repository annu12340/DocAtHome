import time

from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'the random string'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    bloodGroup = db.Column(db.String(10))
    email = db.Column(db.String(100))


class MedicalDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heredityIssues = db.Column(db.String(100))
    desc = db.Column(db.String(50))
    allergy = db.Column(db.String(50))
    ongoingmedName = db.Column(db.String(50))
    pastmedName = db.Column(db.String(50))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    docName = db.Column(db.String(50))
    department = db.Column(db.String(50))
    date = db.Column(db.Integer)
    time = db.Column(db.Integer)
    mode = db.Column(db.String(10))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby_name = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Pending')


# ** THE STACKOVERFLOW MODELS ***
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    shortdescription = db.Column(db.String(200))
    description = db.Column(db.String(200))
    img = db.Column(db.String(200))
    like = db.Column(db.Integer, default=0)
    dislike = db.Column(db.Integer, default=0)
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    createdby = db.Column(db.Integer, default=0)
    postID = db.Column(db.Integer, db.ForeignKey('posts.id'))


# *****  DOCTOR SIDE *****
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    department = db.Column(db.String(50))
    hospital = db.Column(db.String(50))
    year = db.Column(db.Integer, default=1)
    license = db.Column(db.String(50))
    credentials = db.Column(db.String(50))
    password = db.Column(db.String(50))
    homeVisits = db.Column(db.String(50))


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(50))
    doc_name = db.Column(db.String(50))
    feedback = db.Column(db.String(50))
    detailed_report = db.Column(db.String(50))
    date = db.Column(db.Integer)
    consultation_fee = db.Column(db.Integer)
    doc_who_created_it = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))


################################  REGISTER  LOGIN  LOGOUT ROUTES ###################################


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        data = User.query.filter_by(username=username,
                                    password=password).first()

        if data is not None:
            session['user'] = data.id
            print(session['user'])
            return redirect(url_for('index'))

        return render_template('incorrectLogin.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'],
                        password=request.form['password'],
                        age=request.form['age'],
                        gender=request.form['gender'], bloodGroup=request.form['bloodGroup'],
                        email=request.form['email'],
                        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('medical_register'))
    return render_template('register.html')


@app.route('/medical_register/', methods=['GET', 'POST'])
def medical_register():
    if request.method == 'POST':
        user_id = session['user']
        new_user = MedicalDetails(heredityIssues=request.form['heredityIssues'],

                                  desc=request.form['desc'],
                                  allergy=request.form['allergy'],
                                  ongoingmedName=request.form['ongoingmedName'],
                                  pastmedName=request.form['pastmedName'], createdby_id=user_id)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('medical_register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


####################################  OTHER ROUTES  #########################################

@app.route('/index')
def index():
    username = User.query.get(session['user']).username
    print(username)
    today = time.strftime("%m/%d/%Y")
    myAppointments = Appointment.query.filter_by(createdby_name=username).filter_by(status='Confirmed').all()
    return render_template('index.html', myAppointments=myAppointments, today=today)


@app.route('/upcoming')
def upcoming():
    username = User.query.get(session['user']).username
    print(username)
    show_doc = Doctor.query.all()
    myAppointments = Appointment.query.filter_by(createdby_name=username).filter_by(status='Confirmed').all()
    return render_template('upcoming.html', myAppointments=myAppointments, show_doc=show_doc)


@app.route('/UserviewAppointments')
def UserviewAppointments():
    username = User.query.get(session['user']).username
    print(username)
    myAppointments = Appointment.query.filter_by(createdby_name=username).all()
    return render_template('UserviewAppointments.html', myAppointments=myAppointments)


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        user_id = session['user']
        print(user_id)
        new_appointment = Appointment(docName=request.form['docName'],
                                      department=request.form['department'],
                                      date=request.form['date'], time=request.form['time'], mode=request.form['mode'],
                                      createdby_id=user_id, createdby_name=User.query.get(user_id).username)

        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        show_doc = Doctor.query.all()
        return render_template('appointment.html', show_doc=show_doc)


@app.route('/profile')
def profile():
    userid = session['user']
    print(userid)
    Profile = User.query.filter_by(id=userid).one()

    return render_template('profile.html', i=Profile)


@app.route('/history')
def history():
    userid = session['user']
    print(id)
    m = MedicalDetails.query.filter_by(createdby_id=userid).all()
    feedback = Feedback.query.filter_by(patient_id=userid).all()
    return render_template('history.html', m=m, feedback=feedback)


# **************** THE STACK OVERFLOW CODE *************

@app.route('/showPost')
def showPost():
    showPost = Posts.query.order_by(desc(Posts.id))
    return render_template('showPost.html', showPost=showPost)


@app.route('/addPost', methods=['GET', 'POST'])
def addPost():
    if request.method == 'POST':
        user_id = session['user']
        print("user id is ", user_id)
        new_question = Posts(title=request.form['title'], shortdescription=request.form['shortdescription'],
                             description=request.form['description'], img=request.form['img'],
                             createdby_id=user_id)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('addPost.html')


@app.route('/ParticularPost', methods=['GET', 'POST'])
def ParticularPost():
    if request.method == 'POST':
        id = request.args
        userid = session['user']
        createdby = User.query.get(userid).username

        new_response = Response(createdby=createdby, description=request.form['description'],
                                postID=id['id'])
        db.session.add(new_response)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        id = request.args
        print(id)
        q = Posts.query.get(id)
        user = q.createdby_id
        username = User.query.get(user).username
        print("username is", username)
        response = Response.query.filter_by(postID=q.id).all()
        print("response is", response)
        return render_template('ParticularPost.html', post=q, username=username, response=response)


@app.route('/likedislike', methods=['GET', 'POST'])
def likedislike():
    url = request.args
    id = int(url['id'])
    likedislike = int(url['likedislike'])
    print("ds", likedislike)
    post = Posts.query.get(id)
    if likedislike == 0:
        post.dislike += 1
        db.session.commit()
    if likedislike == 1:
        post.like += 1
        db.session.commit()

    return redirect(url_for('showPost'))


######################################### ROUTES FOR THE DOCTORS ####################################

# *****  DOCTOR SIDE *****

@app.route('/dlogin', methods=['GET', 'POST'])
def dlogin():
    if request.method == 'GET':
        return render_template('dlogin.html')
    else:
        username = request.form['username']
        password = request.form['password']
        data = Doctor.query.filter_by(username=username,
                                      password=password).first()

        if data is not None:
            session['doctor'] = data.id
            print(session['doctor'])
            return redirect(url_for('dindex'))
        return render_template('incorrectLogin.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/dregister/', methods=['GET', 'POST'])
def dregister():
    if request.method == 'POST':
        new_user = Doctor(username=request.form['username'], department=request.form['department'],
                          password=request.form['password'], hospital=request.form['hospital'],
                          year=request.form['year'], license=request.form['license'],
                          credentials=request.form['credentials'], homeVisits=request.form['homeVisits'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('dlogin'))
    return render_template('dregister.html')


@app.route('/dlogout', methods=['GET', 'POST'])
def dlogout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/dindex')
def dindex():
    docname = Doctor.query.get(session['doctor']).username
    print(docname)
    myAppointments = Appointment.query.filter_by(docName=docname).filter_by(status='Confirmed').all()
    print(myAppointments)
    today = time.strftime("%m/%d/%Y")
    return render_template('dindex.html', myAppointments=myAppointments, today=today)


@app.route('/viewAppointments')
def viewAppointments():
    doctor_id = session['doctor']
    docname = Doctor.query.get(doctor_id).username
    myAppointments = Appointment.query.filter_by(docName=docname).all()
    print(myAppointments)
    return render_template('viewAppointments.html', myAppointments=myAppointments)


@app.route('/ConfirmAppointment')
def ConfirmAppointment():
    id = int(request.args['id'])
    print('to be confirmed ', id)
    confirm_appointment = Appointment.query.filter_by(id=id).one()
    print(confirm_appointment)
    confirm_appointment.status = 'Confirmed'
    db.session.commit()
    return redirect(url_for('dindex'))


@app.route('/CancelAppointment')
def CancelAppointment():
    id = int(request.args['id'])
    print('to be cancelled ', id)
    CancelAppointment = Appointment.query.filter_by(id=id).one()
    print(CancelAppointment)
    CancelAppointment.status = 'Denied'
    db.session.commit()
    return redirect(url_for('dindex'))


@app.route('/notification')
def Notification():
    doctor_id = session['doctor']
    docname = Doctor.query.get(doctor_id).username
    myAppointments = Appointment.query.filter_by(docName=docname).filter_by(status='Pending').all()
    print('notification', myAppointments)
    return render_template('notification.html', myAppointments=myAppointments)


@app.route('/doc_view_history')
def doc_view_history():
    uid = int(request.args['id'])
    print('toview_history ', id)
    user = User.query.filter_by(id=uid).one()
    m=MedicalDetails.query.filter_by(createdby_id=uid).all()
    return render_template('doc_view_history.html', p=user,m=m)


@app.route('/doc_profile')
def doc_profile():
    doc_id = int(request.args['id'])
    print('toview_history ', doc_id)
    profile = Doctor.query.filter_by(id=doc_id).one()
    med= Doctor.query.filter_by(id=doc_id).one()
    return render_template('doc_profile.html', p=profile)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    doc_id = session['user']
    docname = Doctor.query.filter_by(id=doc_id)
    user_id = int(request.args['id'])
    if request.method == 'POST':
        today = time.strftime("%m/%d/%Y")
        details = Feedback(patient_name=request.form['patient_name'], doc_name=docname,
                           feedback=request.form['feedback'],
                           detailed_report=request.form['detailed_report'],
                           consultation_fee=request.form['consultation_fee'],
                           doc_who_created_it=doc_id, patient_id=user_id, date=today)
        db.session.add(details)
        db.session.commit()
        return redirect(url_for('dindex'))
    else:
        return render_template('feedback.html')


######################################### MAIN ####################################


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

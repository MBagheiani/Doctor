from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "\x82\xdc\x15\xc6\x179m\xbf}SxM7}\xb0o\xa2\x87\xfd\t;3\xf6\xc4"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///doctor.sqlite"
db = SQLAlchemy(app)
app.app_context().push()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.Integer, nullable=False)


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    job = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(255), default="Active")


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(255), default="Pending")
    
    user = db.relationship('User', backref=db.backref('appointment', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('appointment', lazy=True))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctors')
def doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/appointment', methods=['GET','POST'])
def appointment():
    if request.method == "POST":
        name = request.form.get('name')
        phone = request.form.get('phone')
        doctor_id = request.form.get('doctor_id')
        date = request.form.get('date')
        
        user = User(name=name, phone=phone)
        db.session.add(user)
        db.session.commit()  
        
        appointment = Appointment(user_id=user.id, doctor_id=doctor_id, date=date)
        db.session.add(appointment)
        
        db.session.commit()
        
        flash('درخواست شما با موفقیت ثبت شد')
        return render_template('confirm.html')
    
    doctors = Doctor.query.filter_by(status="Active")
    return render_template('appointment.html', doctors=doctors)

@app.route('/approve/<int:appointment>')
def appointment_approve(appointment):
    appointment = Appointment.query.get(appointment)
    appointment.status = "Approved"
    
    db.session.commit()
    
    return redirect(url_for("admin_index"))

@app.route('/denied/<int:appointment>')
def appointment_denied(appointment):
    appointment = Appointment.query.get(appointment)
    appointment.status = "Denied"
    
    db.session.commit()
    
    return redirect(url_for("admin_index"))

@app.route('/admin')
def admin_index():
    appointments = Appointment.query.all()
    return render_template('admin.html', appointments=appointments)

@app.route('/admin/create/doctor',methods=['POST'])
def admin_create_doctor():
    name = request.form.get('name')
    job = request.form.get('job')
    phone = request.form.get('phone')
    
    doctor = Doctor(name=name, job=job, phone=phone)
    db.session.add(doctor)
    db.session.commit()
    
    flash('doctor created')

    return redirect(url_for('doctors'))
    

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

import re
import flask
from flask import render_template, request,redirect, url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///hospital.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    birthdate = db.Column(db.Date)
    password = db.Column(db.String(60), nullable=False)


class Hospital_1(db.Model):
    __tablename__ = 'hospital'

    hospital_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hospital_name = db.Column(db.String(255), nullable=False)
    hospital_address = db.Column(db.Text, nullable=False)
    hospital_email = db.Column(db.String(255), nullable=False)
    hospital_phone = db.Column(db.String(20), nullable=False)
    hospital_zip_code = db.Column(db.String(10), nullable=False)

    # Define the relationship with wards
    wards = db.relationship('Ward', backref='hospital', lazy=True)

    def __repr__(self):
        return f"<Hospital {self.hospital_name}>"

class Ward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.hospital_id'), nullable=False)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)

class Nurse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    doctor = db.relationship('Doctor', backref=db.backref('patients', lazy=True))
    nurse_id = db.Column(db.Integer, db.ForeignKey('nurse.id'))
    nurse = db.relationship('Nurse', backref=db.backref('patients', lazy=True))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))


def validate_email(email):
    """Validates an email address using a regular expression."""
    regex = r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(regex, email) is not None

def initialize_wards():
    hospitals = Hospital_1.query.all()
    for hospital in hospitals:
        for i in range(1, 6):  # Add 5 wards for each hospital
            ward_name = f"Ward {i}"
            ward = Ward(name=ward_name, hospital_id=hospital.hospital_id)
            db.session.add(ward)
    db.session.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/login_page')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'password':
        return redirect(url_for('home'))
    else:
        return 'Invalid credentials'


@app.route('/sign_Up')
def sign_up():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    city = request.form['city']
    gender = request.form['gender']
    birthdate_str = request.form['birthdate'] 
    birthdate_obj = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
    password = request.form['password']

    errors = []

    # Validate user input
    if not name:
        errors.append("Name is required")
    elif len(name) == 1:  
        errors.append("Name must be longer than one character")
    if not email or not validate_email(email): 
        errors.append("Invalid email address")
    if not phone:
        errors.append("Phone number is required")
    if not phone:
        errors.append("Phone number is required")
    elif not phone.isdigit() or len(phone) != 10:
        errors.append("Phone number must be a 10-digit number")

    if not errors:
        # Hash the password
        # hashed_password = generate_password_hash(password)

        # Create a new user object
        new_user = User(name=name, email=email, phone=phone, city=city, gender=gender, birthdate=birthdate_obj, password=password)

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        session['user_name'] = name
        # Redirect to home page
        flash('Signup successful. Welcome!')
        return redirect(url_for('hospital', user_name=name, _external=True, _scheme=request.scheme))
    else:
        return render_template('signup.html', errors=errors)



@app.route('/hospital')
def hospital():
    user_name = session.get('user_name', 'Guest')
    hospitals = Hospital_1.query.all()

    # Fetch hospitals data from the API using Flask
    hospitals_data = [
        {
            'hospital_id': hospital.hospital_id,
            'hospital_name': hospital.hospital_name,
            'hospital_address': hospital.hospital_address,
            'hospital_email': hospital.hospital_email,
            'hospital_phone': hospital.hospital_phone,
            'hospital_zip_code': hospital.hospital_zip_code
        }
        for hospital in hospitals
    ]

    return render_template("hospital.html", user_name=user_name, hospitals=hospitals_data)


@app.route('/wards/<int:hospital_id>')
def wards(hospital_id):
    hospital = Hospital_1.query.get(hospital_id)
    if hospital:
        wards = hospital.wards
        return render_template('wards.html', hospital=hospital, wards=wards)
    else:
        return "Hospital not found"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.secret_key = 'Deek Mac web'
    app.run(debug=True)
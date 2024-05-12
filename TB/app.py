from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    localization = db.Column(db.String(50), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)

class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnosis.id'), nullable=False)
    read_length = db.Column(db.Float, nullable=False)
    total_length = db.Column(db.Integer, nullable=False)
    diagnosis = db.relationship('Diagnosis', backref=db.backref('samples', lazy=True))
    patient = db.relationship('Patient', backref=db.backref('samples', lazy=True))

def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patients')
def patients():
    patients = Patient.query.order_by(Patient.surname).all()
    return render_template('patients.html', patients=patients)

@app.route('/new_patient', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        city = request.form['city']
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')

        new_patient = Patient(name=name, surname=surname, city=city, date_of_birth=date_of_birth)
        db.session.add(new_patient)
        db.session.commit()

        return redirect(url_for('patients'))

    return render_template('new_patient.html')

@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        patient.name = request.form['name']
        patient.surname = request.form['surname']
        patient.city = request.form['city']
        patient.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')

        db.session.commit()

        return redirect(url_for('patients'))

    return render_template('edit_patient.html', patient=patient)


@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    samples = Sample.query.filter_by(patient_id=patient_id).all()
    for sample in samples:
        db.session.delete(sample)
    db.session.delete(patient)
    db.session.commit()

    return redirect(url_for('patients'))

@app.route('/diagnoses')
def diagnoses():
    diagnoses = Diagnosis.query.order_by(Diagnosis.type).all()
    return render_template('diagnoses.html', diagnoses=diagnoses)

@app.route('/diagnoses/new', methods=['GET', 'POST'])
def new_diagnosis():
    if request.method == 'POST':
        type = request.form['type']
        localization = request.form['localization']
        new_diagnosis = Diagnosis(type=type, localization=localization)
        db.session.add(new_diagnosis)
        db.session.commit()

        return redirect(url_for('diagnoses'))

    return render_template('new_diagnosis.html')

@app.route('/edit_diagnosis/<int:diagnosis_id>', methods=['GET', 'POST'])
def edit_diagnosis(diagnosis_id):
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)

    if request.method == 'POST':
        diagnosis.type = request.form['type']
        diagnosis.localization = request.form['localization']

        db.session.commit()

        return redirect(url_for('diagnoses'))

    return render_template('edit_diagnosis.html', diagnosis=diagnosis)

@app.route('/delete_diagnosis/<int:diagnosis_id>', methods=['POST'])
def delete_diagnosis(diagnosis_id):
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)
    db.session.delete(diagnosis)
    db.session.commit()

    return redirect(url_for('diagnoses'))

@app.route('/samples')
def samples():
    samples = Sample.query.order_by(Sample.date.desc()).all()
    patients = Patient.query.order_by(Patient.surname).all()
    diagnoses = Diagnosis.query.order_by(Diagnosis.type).all()
    return render_template('samples.html', samples=samples, patients=patients, diagnoses=diagnoses)

@app.route('/samples/new', methods=['GET', 'POST'])
def new_sample():
    patients = Patient.query.order_by(Patient.surname).all()
    diagnoses = Diagnosis.query.order_by(Diagnosis.type).all()

    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        patient_id = int(request.form['patient_id'])
        diagnosis_id = int(request.form['diagnosis_id'])
        read_length = float(request.form['read_length'])
        total_length = int(request.form['total_length'])

        new_sample = Sample(date=date, patient_id=patient_id, diagnosis_id=diagnosis_id, read_length=read_length, total_length=total_length)
        db.session.add(new_sample)
        db.session.commit()

        return redirect(url_for('samples'))

    return render_template('new_sample.html', patients=patients, diagnoses=diagnoses)

@app.route('/samples/edit/<int:sample_id>', methods=['GET', 'POST'])
def edit_sample(sample_id):
    sample = Sample.query.get_or_404(sample_id)
    patients = Patient.query.order_by(Patient.surname).all()
    diagnoses = Diagnosis.query.order_by(Diagnosis.type).all()

    if request.method == 'POST':
        sample.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        sample.patient_id = int(request.form['patient_id'])
        sample.diagnosis_id = int(request.form['diagnosis_id'])
        sample.read_length = float(request.form['read_length'])
        sample.total_length = int(request.form['total_length'])

        db.session.commit()

        return redirect(url_for('samples'))

    return render_template('edit_sample.html', sample=sample, patients=patients, diagnoses=diagnoses)

@app.route('/samples/delete/<int:sample_id>', methods=['POST'])
def delete_sample(sample_id):
    sample = Sample.query.get_or_404(sample_id)
    db.session.delete(sample)
    db.session.commit()

    return redirect(url_for('samples'))

@app.route('/samples/add', methods=['POST'])
def add_sample():
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    patient_id = int(request.form['patient_id'])
    diagnosis_id = int(request.form['diagnosis_id'])
    read_length = float(request.form['read_length'])
    total_length = int(request.form['total_length'])

    new_sample = Sample(date=date, patient_id=patient_id, diagnosis_id=diagnosis_id, read_length=read_length, total_length=total_length)
    db.session.add(new_sample)
    db.session.commit()

    return redirect(url_for('samples'))

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(debug=True)

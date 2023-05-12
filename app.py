from flask import Flask, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_limiter.util import get_remote_address
from decorator import rate_limited,auth_required
import config
import pickle


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/flask_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()


cache = config.cache

# Define Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)

    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __repr__(self):
        return '<Student %r>' % self.name


@app.route('/student_post/', methods=['POST'])
@auth_required
@rate_limited
def create_student():
    data = request.json
    student = Student(name=data['name'], age=data['age'])
    db.session.add(student)
    db.session.commit()
    cache.delete('students')
    return jsonify({'message': 'Student created successfully'}), 201
    

@app.route('/', methods=['GET'])
@auth_required
@rate_limited
def get_students():
    students = cache.get('students')
    if students is None:
        students = Student.query.all()
        students = [{'id': student.id, 'name': student.name, 'age': student.age} for student in students]
        students_details = pickle.dumps(students)
        cache.set(f'students', students_details)
    else:
        students = pickle.loads(students)
        students = jsonify(students)
    return students, 200


@app.route('/studentdetails/<int:id>/', methods=['GET'])
@auth_required
@rate_limited
def get_student(id):
    student = cache.get(f'student_{id}')
    if student is None:
        student = Student.query.filter_by(id=id).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        student = {'id': student.id, 'name': student.name, 'age': student.age}
        student_info = pickle.dumps(student)
        cache.set(f'student_{id}', student_info)
    else:
        student = pickle.loads(student)
        student = jsonify(student)
    return student, 200




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
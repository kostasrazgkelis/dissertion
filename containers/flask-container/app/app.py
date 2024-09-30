from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__, static_folder='static')
app.config.from_object(__name__)


CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "age": self.age,
            "status": self.status
        }
    

@app.route('/api/', methods=['GET'])
def home():
    user_info = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "status": "success"
    }
    return jsonify(user_info)

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables for all models
    app.run(host='0.0.0.0', port=8080, debug=os.environ.get('FLASK_DEBUG', False))
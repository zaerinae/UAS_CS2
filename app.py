from flask_restful import Api
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import (
    JWTManager, create_access_token,
)
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/cs2'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


class Mhs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.String(10), unique=True)
    nama = db.Column(db.String(100))
    password = db.Column(db.String(100))
    alamat = db.Column(db.String(100))

    def __init__(self, nim, nama, password, alamat):
        self.nim = nim
        self.nama = nama
        self.password = password
        self.alamat = alamat

    @staticmethod
    def get_all_users():
        return Mhs.query.all()

    @staticmethod
    def get_user(nama):
        print(nama)
        return None


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('nim', 'nama', 'password', 'alamat')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/', methods=['POST'])
def add_user():
    nim = request.json['nim']
    nama = request.json['nama']
    password = request.json['password']
    alamat = request.json['alamat']

    new_mhs = Mhs(nim, nama, password, alamat)

    db.session.add(new_mhs)
    db.session.commit()

    return user_schema.jsonify(new_mhs)


@app.route('/', methods=['GET'])
def get_users():
    all_users = Mhs.get_all_users()
    result = users_schema.dump(all_users)
    return jsonify(result)


@app.route('/<id>', methods=['GET'])
def get_user(id):
    mahasiswa = Mhs.query.get(id)
    return user_schema.jsonify(mahasiswa)


@app.route('/<id>', methods=['PUT'])
def update_user(id):
    mahasiswa = Mhs.query.get(id)

    nim = request.json['nim']
    nama = request.json['nama']
    password = request.json['password']
    alamat = request.json['alamat']

    mahasiswa.nim = nim
    mahasiswa.nama = nama
    mahasiswa.password = password
    mahasiswa.alamat = alamat

    db.session.commit()

    return user_schema.jsonify(mahasiswa)


@app.route('/<id>', methods=['DELETE'])
def delete_product(id):
    mahasiswa = Mhs.query.get(id)
    db.session.delete(mahasiswa)
    db.session.commit()

    return user_schema.jsonify(mahasiswa)


@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    login_admin = Admin.query.filter_by(username=username).first()
    print(login_admin.username)
    print(login_admin.password)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username != login_admin.username or password != login_admin.password:
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


if __name__ == '__main__':
    app.run()



from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() #initalse SQL alchemy


class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True) #unique id
    name = db.Column(db.String(80), nullable=False)#required
    location = db.Column(db.String(120))
    date_planted = db.Column(db.String(20))
    height = db.Column(db.Float)
    watered = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) #unqiue id
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)







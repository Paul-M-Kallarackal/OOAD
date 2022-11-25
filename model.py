from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Librarian(db.Model):
    l_id = db.Column(db.Integer, primary_key=True)
    l_name = db.Column(db.String(100), nullable=False)
    l_username = db.Column(db.String(100))
    l_password = db.Column(db.String(100))


class User(db.Model):
    __tablename__="User"
    u_id = db.Column(db.Integer, primary_key=True)
    u_email = db.Column(db.String(80), unique=True, nullable=False)
    u_username=db.Column(db.String(100))
    u_password=db.Column(db.String(100))


class Books(db.Model):
    b_id = db.Column(db.Integer, primary_key=True)
    b_isbn=db.Column(db.Integer,nullable=False)

class Fines(db.Model):
    fine_id=db.Column(db.Integer,primary_key=True)
    u_id=db.Column(db.Integer)
    fine_date=db.Column(db.String)
    fine_amount=db.Column(db.Integer)
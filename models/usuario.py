import flask_login as UserMinix
from flask_sqlalchemy import SQLAlchemy
from configbd.bd import db  

class Usuario(UserMinix.UserMixin, db.Model):

    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(50), nullable=False, unique=True)
    contraseña = db.Column(db.String(225), nullable=False)

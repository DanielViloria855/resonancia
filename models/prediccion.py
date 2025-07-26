from configbd.bd import db
from datetime import datetime

class Prediccion(db.Model):
    __tablename__ = 'predicciones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    resultado = db.Column(db.String(50), nullable=False)
    imagen_nombre = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación inversa para que usuario.predicciones funcione
    usuario = db.relationship('Usuario', backref=db.backref('predicciones', lazy=True))

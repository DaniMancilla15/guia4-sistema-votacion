from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="votante")
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Eleccion(db.Model):
    __tablename__ = "elecciones"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(160), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    activa = db.Column(db.Boolean, nullable=False, default=True)

class Candidato(db.Model):
    __tablename__ = "candidatos"
    id = db.Column(db.Integer, primary_key=True)
    eleccion_id = db.Column(db.Integer, db.ForeignKey("elecciones.id", ondelete="CASCADE"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    propuesta = db.Column(db.Text)
    eleccion = db.relationship("Eleccion", backref=db.backref("candidatos", lazy=True, cascade="all, delete-orphan"))

class Voto(db.Model):
    __tablename__ = "votos"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    eleccion_id = db.Column(db.Integer, db.ForeignKey("elecciones.id", ondelete="CASCADE"), nullable=False)
    candidato_id = db.Column(db.Integer, db.ForeignKey("candidatos.id", ondelete="CASCADE"), nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("usuario_id", "eleccion_id", name="uq_usuario_eleccion"),
    )

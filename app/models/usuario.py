from app import db

from enum import Enum


class Perfil(Enum):
    CLIENTE = "CLIENTE"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"
    GERENTE = "GERENTE"

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.Enum(Perfil), nullable=False)
from datetime import datetime, timezone

from app import db


class Fidelidade(db.Model):
    __tablename__ = "fidelidades"

    id = db.Column(db.Integer, primary_key=True)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        unique=True
    )

    pontos = db.Column(db.Integer, nullable=False, default=0)

    consentimento_lgpd = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    data_consentimento = db.Column(
        db.DateTime,
        nullable=True
    )

    def registrar_consentimento(self):
        self.consentimento_lgpd = True
        self.data_consentimento = datetime.now(timezone.utc)
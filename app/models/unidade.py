from app import db


class Unidade(db.Model):
    __tablename__ = "unidades"

    __table_args__ = (
        db.UniqueConstraint(
            "nome",
            "cidade",
            name="uq_unidades_nome_cidade"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
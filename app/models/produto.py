from app import db


class Produto(db.Model):
    __tablename__ = "produtos"

    __table_args__ = (
        db.UniqueConstraint(
            "nome",
            name="uq_produtos_nome"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
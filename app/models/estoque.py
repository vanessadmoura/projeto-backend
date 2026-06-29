from app import db


class Estoque(db.Model):
    __tablename__ = "estoques"

    __table_args__ = (
        db.UniqueConstraint(
            "produto_id",
            "unidade_id",
            name="uq_estoques_produto_unidade"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    produto_id = db.Column(
        db.Integer,
        db.ForeignKey("produtos.id"),
        nullable=False
    )

    unidade_id = db.Column(
        db.Integer,
        db.ForeignKey("unidades.id"),
        nullable=False
    )

    quantidade = db.Column(db.Integer, nullable=False)
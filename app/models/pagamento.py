from datetime import datetime, timezone

from app import db


def utc_now():
    return datetime.now(timezone.utc)


class Pagamento(db.Model):
    __tablename__ = "pagamentos"

    id = db.Column(db.Integer, primary_key=True)

    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey("pedidos.id"),
        nullable=False
    )

    valor = db.Column(db.Float, nullable=False)

    status = db.Column(
        db.String(30),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now
    )
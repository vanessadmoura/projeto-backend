from enum import Enum
from datetime import datetime, timezone

from app import db


class CanalPedido(Enum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"
    PICKUP = "PICKUP"
    WEB = "WEB"


class StatusPedido(Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


def utc_now():
    return datetime.now(timezone.utc)


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    unidade_id = db.Column(
        db.Integer,
        db.ForeignKey("unidades.id"),
        nullable=False
    )

    canal_pedido = db.Column(
        db.Enum(CanalPedido),
        nullable=False
    )

    status = db.Column(
        db.Enum(StatusPedido),
        nullable=False,
        default=StatusPedido.AGUARDANDO_PAGAMENTO
    )

    total = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )

    itens = db.relationship(
        "PedidoItem",
        backref="pedido",
        cascade="all, delete-orphan",
        lazy=True
    )
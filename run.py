import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone

from flask import Flask, request, jsonify
from flasgger import Swagger

from app.swagger_config import template
from config import Config
from app import db, migrate, jwt

from app.routes.auth_routes import auth_bp
from app.routes.produto_routes import produto_bp
from app.routes.unidade_routes import unidade_bp
from app.routes.estoque_routes import estoque_bp
from app.routes.pedido_routes import pedido_bp
from app.routes.pagamento_routes import pagamento_bp
from app.routes.fidelidade_routes import fidelidade_bp


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)


def erro_padronizado(error, message, status, details=None):
    return jsonify({
        "error": error,
        "message": message,
        "details": details or [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": request.path
    }), status


@jwt.unauthorized_loader
def token_ausente_callback(reason):
    return erro_padronizado(
        "TOKEN_AUSENTE",
        "Token de autenticação não informado.",
        401,
        [{"field": "Authorization", "issue": reason}]
    )


@jwt.invalid_token_loader
def token_invalido_callback(reason):
    return erro_padronizado(
        "TOKEN_INVALIDO",
        "Token de autenticação inválido.",
        401,
        [{"field": "Authorization", "issue": reason}]
    )


@jwt.expired_token_loader
def token_expirado_callback(jwt_header, jwt_payload):
    return erro_padronizado(
        "TOKEN_EXPIRADO",
        "Token de autenticação expirado. Faça login novamente.",
        401
    )


@jwt.revoked_token_loader
def token_revogado_callback(jwt_header, jwt_payload):
    return erro_padronizado(
        "TOKEN_REVOGADO",
        "Token de autenticação revogado.",
        401
    )


@jwt.needs_fresh_token_loader
def token_fresh_necessario_callback(jwt_header, jwt_payload):
    return erro_padronizado(
        "TOKEN_FRESH_NECESSARIO",
        "Esta operação exige autenticação recente.",
        401
    )


swagger = Swagger(
    app,
    template=template
)

os.makedirs("logs", exist_ok=True)

handler = RotatingFileHandler(
    "logs/auditoria.log",
    maxBytes=100000,
    backupCount=3,
    encoding="utf-8"
)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


@app.after_request
def registrar_log(response):
    app.logger.info(
        f"Metodo={request.method} "
        f"Rota={request.path} "
        f"Status={response.status_code}"
    )
    return response


@app.route("/")
def home():
    return {
        "message": "API Raízes do Nordeste"
    }


from app.models.usuario import Usuario
from app.models.unidade import Unidade
from app.models.produto import Produto
from app.models.estoque import Estoque
from app.models.pedido import Pedido
from app.models.pagamento import Pagamento
from app.models.fidelidade import Fidelidade
from app.models.pedido_item import PedidoItem


app.register_blueprint(auth_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(unidade_bp)
app.register_blueprint(estoque_bp)
app.register_blueprint(pedido_bp)
app.register_blueprint(pagamento_bp)
app.register_blueprint(fidelidade_bp)


if __name__ == "__main__":
    app.run(debug=True)
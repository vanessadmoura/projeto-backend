import bcrypt

from flask import current_app
from flask_jwt_extended import create_access_token

from app import db
from app.models.usuario import Usuario, Perfil
from app.utils.responses import erro_response


def cadastrar_usuario(data):
    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")

    if nome is not None:
        nome = nome.strip()

    if email is not None:
        email = email.strip().lower()

    if not nome or not email or not senha:
        return erro_response(
            "DADOS_INVALIDOS",
            "Nome, e-mail e senha são obrigatórios.",
            422,
            [
                {"field": "nome", "issue": "Campo obrigatório"},
                {"field": "email", "issue": "Campo obrigatório"},
                {"field": "senha", "issue": "Campo obrigatório"}
            ]
        )

    usuario_existente = Usuario.query.filter_by(email=email).first()

    if usuario_existente:
        return erro_response(
            "EMAIL_JA_CADASTRADO",
            "Já existe um usuário cadastrado com este e-mail.",
            409,
            [
                {"field": "email", "issue": "E-mail já cadastrado"}
            ]
        )

    senha_hash = bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    usuario = Usuario(
        nome=nome,
        email=email,
        senha=senha_hash,
        perfil=Perfil.CLIENTE
    )

    db.session.add(usuario)
    db.session.commit()

    current_app.logger.info(
        f"Novo usuário cadastrado: id={usuario.id}, "
        f"email={usuario.email}, perfil={usuario.perfil.value}"
    )

    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": usuario.perfil.value
    }, 201


def login_usuario(data):
    email = data.get("email")
    senha = data.get("senha")

    if email is not None:
        email = email.strip().lower()

    if not email or not senha:
        return erro_response(
            "DADOS_INVALIDOS",
            "E-mail e senha são obrigatórios.",
            422,
            [
                {"field": "email", "issue": "Campo obrigatório"},
                {"field": "senha", "issue": "Campo obrigatório"}
            ]
        )

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        return erro_response(
            "CREDENCIAIS_INVALIDAS",
            "E-mail ou senha inválidos.",
            401
        )

    senha_valida = bcrypt.checkpw(
        senha.encode("utf-8"),
        usuario.senha.encode("utf-8")
    )

    if not senha_valida:
        return erro_response(
            "CREDENCIAIS_INVALIDAS",
            "E-mail ou senha inválidos.",
            401
        )

    token = create_access_token(
        identity=str(usuario.id),
        additional_claims={
            "perfil": usuario.perfil.value
        }
    )

    current_app.logger.info(
        f"Login realizado: id={usuario.id}, "
        f"email={usuario.email}, perfil={usuario.perfil.value}"
    )

    return {
        "accessToken": token,
        "tokenType": "Bearer",
        "user": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil.value
        }
    }, 200
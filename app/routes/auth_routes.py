from flask import Blueprint, request, jsonify

from app.services.auth_service import cadastrar_usuario, login_usuario


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Cadastra um novo cliente
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
            - email
            - senha
          properties:
            nome:
              type: string
              example: Maria Oliveira
            email:
              type: string
              example: maria@email.com
            senha:
              type: string
              example: 123456
    responses:
      201:
        description: Cliente cadastrado com sucesso
        examples:
          application/json:
            id: 1
            nome: Maria Oliveira
            email: maria@email.com
            perfil: CLIENTE
      409:
        description: E-mail já cadastrado
        examples:
          application/json:
            error: EMAIL_JA_CADASTRADO
            message: Já existe um usuário cadastrado com este e-mail.
            details:
              - field: email
                issue: E-mail já cadastrado
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /auth/register
      422:
        description: Dados inválidos
        examples:
          application/json:
            error: DADOS_INVALIDOS
            message: Nome, e-mail e senha são obrigatórios.
            details:
              - field: nome
                issue: Campo obrigatório
              - field: email
                issue: Campo obrigatório
              - field: senha
                issue: Campo obrigatório
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /auth/register
    """
    resposta, status = cadastrar_usuario(
        request.get_json(silent=True) or {}
    )

    return jsonify(resposta), status


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login de usuário
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - senha
          properties:
            email:
              type: string
              example: gerente@email.com
            senha:
              type: string
              example: 123456
    responses:
      200:
        description: Login realizado com sucesso
        examples:
          application/json:
            accessToken: jwt...
            tokenType: Bearer
            user:
              id: 1
              nome: Gerente Teste
              email: gerente@email.com
              perfil: GERENTE
      401:
        description: Credenciais inválidas
        examples:
          application/json:
            error: CREDENCIAIS_INVALIDAS
            message: E-mail ou senha inválidos.
            details: []
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /auth/login
      422:
        description: Dados inválidos
        examples:
          application/json:
            error: DADOS_INVALIDOS
            message: E-mail e senha são obrigatórios.
            details:
              - field: email
                issue: Campo obrigatório
              - field: senha
                issue: Campo obrigatório
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /auth/login
    """
    resposta, status = login_usuario(
        request.get_json(silent=True) or {}
    )

    return jsonify(resposta), status
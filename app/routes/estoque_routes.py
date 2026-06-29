from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.services.estoque_service import (
    criar_estoque_service,
    listar_estoque_service,
    atualizar_estoque_service
)
from app.utils.responses import erro_response


estoque_bp = Blueprint(
    "estoques",
    __name__,
    url_prefix="/estoques"
)


def perfil_atual():
    claims = get_jwt()
    return claims.get("perfil")


def obter_paginacao():
    page = request.args.get("page", 1)
    limit = request.args.get("limit", 10)

    try:
        page = int(page)
        limit = int(limit)
    except (TypeError, ValueError):
        return None, None, erro_response(
            "PAGINACAO_INVALIDA",
            "page e limit devem ser números inteiros maiores que zero.",
            422,
            [
                {"field": "page", "issue": "Deve ser um número inteiro maior que zero"},
                {"field": "limit", "issue": "Deve ser um número inteiro maior que zero"}
            ]
        )

    if page <= 0 or limit <= 0:
        return None, None, erro_response(
            "PAGINACAO_INVALIDA",
            "page e limit devem ser números inteiros maiores que zero.",
            422,
            [
                {"field": "page", "issue": "Deve ser maior que zero"},
                {"field": "limit", "issue": "Deve ser maior que zero"}
            ]
        )

    if limit > 100:
        return None, None, erro_response(
            "LIMITE_INVALIDO",
            "O limite máximo permitido é 100.",
            422,
            [{"field": "limit", "issue": "Valor máximo permitido: 100"}]
        )

    return page, limit, None


@estoque_bp.route("", methods=["POST"])
@jwt_required()
def criar_estoque():
    """
    Cria um registro de estoque
    ---
    tags:
      - Estoques
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - produto_id
            - unidade_id
            - quantidade
          properties:
            produto_id:
              type: integer
              example: 1
            unidade_id:
              type: integer
              example: 1
            quantidade:
              type: integer
              example: 100
    responses:
      201:
        description: Estoque criado com sucesso
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
      404:
        description: Produto ou unidade não encontrada
      409:
        description: Estoque já cadastrado para o produto nesta unidade
      422:
        description: Dados inválidos
    """
    resposta, status = criar_estoque_service(
        request.get_json(silent=True) or {},
        perfil_atual()
    )

    return jsonify(resposta), status


@estoque_bp.route("", methods=["GET"])
@jwt_required()
def listar_estoque():
    """
    Lista os registros de estoque com paginação
    ---
    tags:
      - Estoques
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        required: false
        type: integer
        description: Número da página
        example: 1
      - in: query
        name: limit
        required: false
        type: integer
        description: Quantidade de itens por página
        example: 10
    responses:
      200:
        description: Lista de estoques retornada com sucesso
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão para consultar estoque
      422:
        description: Parâmetros de paginação inválidos
    """
    page, limit, erro = obter_paginacao()

    if erro:
        resposta, status = erro
        return jsonify(resposta), status

    resposta, status = listar_estoque_service(
        perfil_atual(),
        page,
        limit
    )

    return jsonify(resposta), status


@estoque_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def atualizar_estoque(id):
    """
    Atualiza a quantidade de um estoque
    ---
    tags:
      - Estoques
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID do estoque
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - quantidade
          properties:
            quantidade:
              type: integer
              example: 80
    responses:
      200:
        description: Estoque atualizado com sucesso
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
      404:
        description: Estoque não encontrado
      422:
        description: Dados inválidos
    """
    resposta, status = atualizar_estoque_service(
        id,
        request.get_json(silent=True) or {},
        perfil_atual()
    )

    return jsonify(resposta), status
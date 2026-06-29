from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.services.produto_service import (
    criar_produto_service,
    listar_produtos_service,
    buscar_produto_service
)
from app.utils.responses import erro_response


produto_bp = Blueprint("produtos", __name__, url_prefix="/produtos")


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


@produto_bp.route("", methods=["POST"])
@jwt_required()
def criar_produto():
    """
    Cria um novo produto
    ---
    tags:
      - Produtos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
            - preco
          properties:
            nome:
              type: string
              example: X-Baião
            preco:
              type: number
              example: 25.90
    responses:
      201:
        description: Produto criado com sucesso
        examples:
          application/json:
            id: 1
            nome: X-Baião
            preco: 25.90
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
        examples:
          application/json:
            error: SEM_PERMISSAO
            message: Usuário sem permissão.
            details:
              - field: perfil
                issue: Apenas GERENTE pode cadastrar produtos
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /produtos
      409:
        description: Produto já cadastrado
        examples:
          application/json:
            error: PRODUTO_JA_CADASTRADO
            message: Já existe um produto cadastrado com este nome.
            details:
              - field: nome
                issue: Produto já cadastrado
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /produtos
      422:
        description: Dados inválidos ou preço inválido
        examples:
          application/json:
            error: DADOS_INVALIDOS
            message: Nome e preço são obrigatórios.
            details:
              - field: nome
                issue: Campo obrigatório
              - field: preco
                issue: Campo obrigatório
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /produtos
    """
    resposta, status = criar_produto_service(
        request.get_json(silent=True) or {},
        perfil_atual()
    )

    return jsonify(resposta), status


@produto_bp.route("", methods=["GET"])
def listar_produtos():
    """
    Lista produtos com paginação
    ---
    tags:
      - Produtos
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
        description: Lista de produtos retornada com sucesso
        examples:
          application/json:
            page: 1
            limit: 10
            total: 1
            totalPages: 1
            items:
              - id: 1
                nome: X-Baião
                preco: 25.90
      422:
        description: Parâmetros de paginação inválidos
        examples:
          application/json:
            error: PAGINACAO_INVALIDA
            message: page e limit devem ser números inteiros maiores que zero.
            details:
              - field: page
                issue: Deve ser um número inteiro maior que zero
              - field: limit
                issue: Deve ser um número inteiro maior que zero
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /produtos
    """
    page, limit, erro = obter_paginacao()

    if erro:
        resposta, status = erro
        return jsonify(resposta), status

    resposta, status = listar_produtos_service(page, limit)

    return jsonify(resposta), status


@produto_bp.route("/<int:id>", methods=["GET"])
def buscar_produto(id):
    """
    Busca um produto pelo ID
    ---
    tags:
      - Produtos
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID do produto
        example: 1
    responses:
      200:
        description: Produto encontrado com sucesso
        examples:
          application/json:
            id: 1
            nome: X-Baião
            preco: 25.90
      404:
        description: Produto não encontrado
        examples:
          application/json:
            error: PRODUTO_NAO_ENCONTRADO
            message: Produto não encontrado.
            details:
              - field: id
                issue: Produto inexistente
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /produtos/1
    """
    resposta, status = buscar_produto_service(id)

    return jsonify(resposta), status
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.services.unidade_service import (
    criar_unidade_service,
    listar_unidades_service,
    buscar_unidade_service,
    listar_cardapio_unidade_service
)
from app.utils.responses import erro_response


unidade_bp = Blueprint("unidades", __name__, url_prefix="/unidades")


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


@unidade_bp.route("", methods=["POST"])
@jwt_required()
def criar_unidade():
    """
    Cria uma nova unidade
    ---
    tags:
      - Unidades
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
            - cidade
          properties:
            nome:
              type: string
              example: Raízes do Nordeste - Fortaleza
            cidade:
              type: string
              example: Fortaleza
    responses:
      201:
        description: Unidade criada com sucesso
        examples:
          application/json:
            id: 1
            nome: Raízes do Nordeste - Fortaleza
            cidade: Fortaleza
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
                issue: Apenas GERENTE pode cadastrar unidades
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /unidades
      409:
        description: Unidade já cadastrada
        examples:
          application/json:
            error: UNIDADE_JA_CADASTRADA
            message: Já existe uma unidade cadastrada com este nome nesta cidade.
            details:
              - field: nome/cidade
                issue: Unidade já cadastrada para essa combinação
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /unidades
      422:
        description: Dados inválidos
        examples:
          application/json:
            error: DADOS_INVALIDOS
            message: Nome e cidade são obrigatórios.
            details:
              - field: nome
                issue: Campo obrigatório
              - field: cidade
                issue: Campo obrigatório
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /unidades
    """
    resposta, status = criar_unidade_service(
        request.get_json(silent=True) or {},
        perfil_atual()
    )

    return jsonify(resposta), status


@unidade_bp.route("", methods=["GET"])
def listar_unidades():
    """
    Lista unidades com paginação
    ---
    tags:
      - Unidades
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
        description: Lista de unidades retornada com sucesso
        examples:
          application/json:
            page: 1
            limit: 10
            total: 1
            totalPages: 1
            items:
              - id: 1
                nome: Unidade Centro
                cidade: Fortaleza
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
            path: /unidades
    """
    page, limit, erro = obter_paginacao()

    if erro:
        resposta, status = erro
        return jsonify(resposta), status

    resposta, status = listar_unidades_service(page, limit)

    return jsonify(resposta), status


@unidade_bp.route("/<int:id>", methods=["GET"])
def buscar_unidade(id):
    """
    Busca uma unidade pelo ID
    ---
    tags:
      - Unidades
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID da unidade
        example: 1
    responses:
      200:
        description: Unidade encontrada com sucesso
        examples:
          application/json:
            id: 1
            nome: Raízes do Nordeste - Fortaleza
            cidade: Fortaleza
      404:
        description: Unidade não encontrada
        examples:
          application/json:
            error: UNIDADE_NAO_ENCONTRADA
            message: Unidade não encontrada.
            details:
              - field: id
                issue: Unidade inexistente
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /unidades/1
    """
    resposta, status = buscar_unidade_service(id)

    return jsonify(resposta), status


@unidade_bp.route("/<int:id>/cardapio", methods=["GET"])
def listar_cardapio_unidade(id):
    """
    Lista o cardápio disponível de uma unidade com base no estoque
    ---
    tags:
      - Unidades
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID da unidade
        example: 1
    responses:
      200:
        description: Cardápio da unidade retornado com sucesso
        examples:
          application/json:
            unidadeId: 1
            unidade: Raízes do Nordeste - Fortaleza
            cidade: Fortaleza
            cardapio:
              - produtoId: 1
                nome: X-Baião
                preco: 25.9
                quantidadeDisponivel: 100
      404:
        description: Unidade não encontrada
        examples:
          application/json:
            error: UNIDADE_NAO_ENCONTRADA
            message: Unidade não encontrada.
            details:
              - field: id
                issue: Unidade inexistente
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /unidades/1/cardapio
    """
    resposta, status = listar_cardapio_unidade_service(id)

    return jsonify(resposta), status